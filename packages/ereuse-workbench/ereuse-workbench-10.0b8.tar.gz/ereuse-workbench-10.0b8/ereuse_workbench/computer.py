import json
import re
from enum import Enum
from itertools import chain
from math import floor
from subprocess import PIPE, run
from typing import List, Set

from contextlib import suppress
from ereuse_utils.nested_lookup import get_nested_dicts_with_key_containing_value, \
    get_nested_dicts_with_key_value
from pySMART import Device
from pydash import clean, compact, find_key, get
from warnings import catch_warnings, filterwarnings

from ereuse_workbench import utils
from ereuse_workbench.benchmarker import Benchmarker


class PrivateFields(Enum):
    """
    These fields are not converted to JSON so they are kept
    private for internal usage.
    """
    logical_name = 'logical_name'


class Computer:
    """
    Gets hardware information from the computer and its components,
    like serial numbers or model names. At the same time and
    if a Benchmarker is passed-in, benchmarks some of them.

    This class is divided by the methods that extract the hardware
    information for each component individually and a ``.run()``
    method that glues them.

    This class uses ``LSHW`` as the main source of hardware information,
    which is obtained once when it is instantiated.
    """
    CONNECTORS = 'usb', 'firewire', 'serial', 'pcmcia'
    TO_REMOVE = {
        'none',
        'prod',
        'o.e.m',
        'oem',
        r'n/a',
        'atapi',
        'pc',
        'unknown'
    }
    """Delete those *words* from the value"""
    assert all(v.lower() == v for v in TO_REMOVE), 'All words need to be lower-case'

    CHARS_TO_REMOVE = '(){}[]'
    """
    Remove those *characters* from the value. 
    All chars inside those are removed. Ex: foo (bar) => foo
    """

    MEANINGLESS = {
        'to be filled',
        'system manufacturer',
        'system product',
        'sernum',
        'xxxxx',
        'system name',
        'not specified',
        'modulepartnumber',
        'system serial',
        '0001-067a-0000',
        'partnum',
        'manufacturer',
        '0000000',
        'fffff'
    }
    """Discard a value if any of these values are inside it. """
    assert all(v.lower() == v for v in MEANINGLESS), 'All values need to be lower-case'

    CHASSIS_TO_TYPE = {
        # dmi types from https://ezix.org/src/pkg/lshw/src/master/src/core/dmi.cc#L632
        'Desktop': {'desktop', 'low-profile', 'tower', 'docking', 'all-in-one'},
        'Microtower': {'pizzabox', 'mini-tower', 'space-saving', 'lunchbox', 'mini', 'stick'},
        'Laptop': {'portable', 'laptop', 'convertible', 'tablet', 'detachable'},
        'Netbook': {'notebook', 'handheld', 'sub-notebook'},
        'Server': {'server'}
    }
    """A conversion table from DMI's chassis type value to our type value."""
    PHYSICAL_RAM_TYPES = 'ddr', 'sdram', 'sodimm'

    def __init__(self, benchmarker: Benchmarker = False):
        self.benchmarker = benchmarker
        # Obtain raw from LSHW
        stdout = run(('lshw', '-json', '-quiet'),
                     check=True,
                     stdout=PIPE,
                     universal_newlines=True).stdout
        self.lshw = json.loads(stdout)

    def run(self) -> (dict, List[dict]):
        """
        Get the hardware information.

        This method returns *almost* DeviceHub ready information in a
        tuple, where the first element is information related to the
        overall machine, like the S/N of the computer, and the second
        item is a list of hardware information per component.
        """
        computer = self.computer()
        components = chain(self.processors(), self.ram_modules(), self.hard_drives(),
                           self.graphic_cards(), [self.motherboard()], self.network_adapters(),
                           self.sound_cards())
        return computer, compact(components)

    def computer(self):
        node = self.lshw  # Computer node is just the root of lshw
        chassis = node['configuration'].get('chassis', None)
        _type = find_key(self.CHASSIS_TO_TYPE, lambda values, key: chassis in values)
        return dict({
            'type': _type,
            '@type': 'Computer'
        }, **self._common(node))

    def processors(self):
        nodes = get_nested_dicts_with_key_value(self.lshw, 'class', 'processor')
        # We want only the physical cpu's, not the logic ones
        # In some cases we may get empty cpu nodes, we can detect them because
        # all regular cpus have at least a description (Intel Core i5...)
        return (self.processor(node) for node in nodes if
                'logical' not in node['id'] and 'description' in node and not node.get('disabled'))

    def processor(self, node):
        speed = utils.convert_frequency(node['size'], node['units'], 'GHz')
        assert 0.1 <= speed <= 9, 'Frequency is not in reasonable GHz'
        processor = {
            '@type': 'Processor',
            'speed': speed,
            'address': node['width']
        }
        if 'cores' in node['configuration']:
            processor['numberOfCores'] = cores = int(node['configuration']['cores'])
            assert 1 <= cores <= 16
        if self.benchmarker:
            processor['benchmarks'] = [
                self.benchmarker.processor(),
                self.benchmarker.processor_sysbench()
            ]
        processor = dict(processor, **self._common(node))
        processor['serialNumber'] = None  # Processors don't have valid SN :-(
        return processor

    def ram_modules(self):
        # We can get flash memory (BIOS?), system memory and unknown types of memory
        memories = get_nested_dicts_with_key_value(self.lshw, 'class', 'memory')
        for memory in memories:
            for ram_type in self.PHYSICAL_RAM_TYPES:
                if ram_type in memory.get('description', '').lower():
                    yield self.ram_module(memory)

    def ram_module(self, module: dict):
        # Node with no size == empty ram slot
        if 'size' in module:
            ram = dict({
                '@type': 'RamModule',
                'size': int(utils.convert_capacity(module['size'], module['units'], 'MB'))
            }, **self._common(module))
            # power of 2
            assert 128 <= ram['size'] <= 2 ** 15 and (ram['size'] & (ram['size'] - 1) == 0), \
                'Invalid value {} MB for RAM Speed'.format(ram['size'])
            if 'clock' in module:
                ram['speed'] = speed = utils.convert_frequency(module['clock'], 'Hz', 'MHz')
                assert 100 <= speed <= 10000, 'Invalid value {} Mhz for RAM speed'.format(speed)
            return ram

    def hard_drives(self, get_removables=False):
        nodes = get_nested_dicts_with_key_containing_value(self.lshw, 'id', 'disk')
        # We can get nodes that are not truly disks as they don't have
        # size. Let's just forget about those.
        return (self.hard_drive(node, get_removables) for node in nodes if 'size' in node)

    def hard_drive(self, node, get_removable=False) -> dict or None:
        logical_name = node['logicalname']
        interface = run('udevadm info '
                        '--query=all '
                        '--name={} | '
                        'grep '
                        'ID_BUS | '
                        'cut -c 11-'.format(logical_name),
                        check=True, universal_newlines=True, shell=True, stdout=PIPE).stdout
        # todo not sure if ``interface != usb`` is needed
        is_not_removable = interface != 'usb' and not get(node, 'capabilities.removable')
        is_removable = interface == 'usb'
        if get_removable and is_removable or not get_removable and is_not_removable:
            # If get_removable and is_removable or not get_removable and is not_removable
            hdd = {
                '@type': 'HardDrive',
                'size': floor(utils.convert_capacity(node['size'], node['units'], 'MB')),
                'interface': interface,
                PrivateFields.logical_name: logical_name
            }
            with catch_warnings():
                filterwarnings('error')
                with suppress(Warning):
                    hdd['type'] = 'SSD' if Device(logical_name).is_ssd else 'HDD'
            assert 10000 < hdd['size'] < 10 ** 8, 'Invalid HDD size {} MB'.format(hdd['size'])
            if self.benchmarker:
                hdd['benchmark'] = self.benchmarker.benchmark_hdd(logical_name)
            hdd = dict(hdd, **self._common(node))
            if not hdd['serialNumber']:
                hdd['serialNumber'] = Device(hdd[PrivateFields.logical_name]).serial
            if not hdd['model']:
                hdd['model'] = Device(hdd[PrivateFields.logical_name]).model
            return hdd

    def graphic_cards(self):
        nodes = get_nested_dicts_with_key_value(self.lshw, 'class', 'display')
        return (self.graphic_card(n) for n in nodes if n['configuration'].get('driver', None))

    def graphic_card(self, node) -> dict:
        return dict({
            '@type': 'GraphicCard',
            'memory': self._graphic_card_memory(node['businfo'].split('@')[1])
        }, **self._common(node))

    @staticmethod
    def _graphic_card_memory(bus_info):
        ret = run('lspci -v -s {bus} |'
                  'grep \'prefetchable\' | '
                  'grep -v \'non-prefetchable\' | '
                  'egrep -o \'[0-9]{{1,3}}[KMGT]+\''.format(bus=bus_info),
                  stdout=PIPE,
                  shell=True,
                  universal_newlines=True)
        # Get max memory value
        max_size = 0
        for value in ret.stdout.splitlines():
            unit = re.split('\d+', value)[1]
            size = int(value.rstrip(unit))

            # convert all values to KB before compare
            size_kb = utils.convert_base(size, unit, 'K', distance=1024)
            if size_kb > max_size:
                max_size = size_kb

        if max_size > 0:
            size = utils.convert_capacity(max_size, 'KB', 'MB')
            assert 8 < size < 2 ** 14, 'Invalid Graphic Card size {} MB'.format(size)
            return size
        return None

    def motherboard(self):
        node = next(get_nested_dicts_with_key_value(self.lshw, 'description', 'Motherboard'))
        return dict({
            '@type': 'Motherboard',
            'connectors': {name: self.motherboard_num_of_connectors(name)
                           for name in self.CONNECTORS},
            'totalSlots': int(run('dmidecode -t 17 | '
                                  'grep -o BANK | '
                                  'wc -l',
                                  check=True,
                                  universal_newlines=True,
                                  shell=True,
                                  stdout=PIPE).stdout),
            'usedSlots': int(run('dmidecode -t 17 | '
                                 'grep Size | '
                                 'grep MB | '
                                 'awk \'{print $2}\' | '
                                 'wc -l',
                                 check=True,
                                 universal_newlines=True,
                                 shell=True,
                                 stdout=PIPE).stdout)
        }, **self._common(node))

    def motherboard_num_of_connectors(self, connector_name) -> int:
        connectors = get_nested_dicts_with_key_containing_value(self.lshw, 'id', connector_name)
        if connector_name == 'usb':
            connectors = (c for c in connectors
                          if 'usbhost' not in c['id'] and 'usb' not in c['businfo'])
        return len(tuple(connectors))

    def network_adapters(self):
        nodes = get_nested_dicts_with_key_value(self.lshw, 'class', 'network')
        return (self.network_adapter(node) for node in nodes)

    def network_adapter(self, node):
        network = self._common(node)
        network['@type'] = 'NetworkAdapter'
        if 'capacity' in node:
            network['speed'] = utils.convert_speed(node['capacity'], 'bps', 'Mbps')
        if 'logicalname' in network:
            # If we don't have logicalname it means we don't have the
            # (proprietary) drivers fot that NetworkAdaptor
            # which means we can't access at the MAC address
            # (note that S/N == MAC) "sudo /sbin/lspci -vv" could bring
            # the MAC even if no drivers are installed however more work
            # has to be done in ensuring it is reliable, really needed,
            # and to parse it
            # https://www.redhat.com/archives/redhat-list/2010-October/msg00066.html
            # workbench-live includes proprietary firmwares
            if not network['serialNumber']:
                network['serialNumber'] = utils.get_hw_addr(node['logicalname'])
        return network

    def sound_cards(self):
        nodes = get_nested_dicts_with_key_value(self.lshw, 'class', 'multimedia')
        return (self.sound_card(node) for node in nodes)

    def sound_card(self, node):
        return dict({
            '@type': 'SoundCard'
        }, **self._common(node))

    def _common(self, node: dict) -> dict:
        manufacturer = self.get(node, 'vendor')
        return {
            'manufacturer': manufacturer,
            'model': self.get(node, 'product', remove={manufacturer} if manufacturer else None),
            'serialNumber': self.get(node, 'serial')
        }

    @classmethod
    def get(cls, dictionary: dict, key: str, remove: Set[str] = None) -> str or None:
        """
        Gets a string value from the dictionary and sanitizes it.
        Returns ``None`` if the value does not exist or it doesn't
        have meaning.

        Values are patterned and compared against sets
        of meaningless characters usually found in LSHW's output.

        :param dictionary: A dictionary potentially containing the value.
        :param key: The key in ``dictionary`` where the value
                    potentially is.
        :param remove: Remove these words if found.
        """
        remove = (remove or set()) | cls.TO_REMOVE
        regex = r'({})\W'.format('|'.join(s for s in remove))
        val = re.sub(regex, '', dictionary.get(key, ''), flags=re.IGNORECASE)
        val = '' if val.lower() in remove else val  # regex's `\W` != whole string
        val = re.sub(r'\([^)]*\)', '', val)  # Remove everything between CHARS_TO_REMOVE
        for char_to_remove in cls.CHARS_TO_REMOVE:
            val = val.replace(char_to_remove, '')
        val = clean(val)
        if val and not any(meaningless in val.lower() for meaningless in cls.MEANINGLESS):
            return val
        else:
            return None
