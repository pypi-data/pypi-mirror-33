import json
import os
import uuid
from datetime import datetime
from multiprocessing import Process
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Type
from urllib.parse import urlparse

import pkg_resources
import urllib3
from colorama import Fore, init
from ereuse_utils import DeviceHubJSONEncoder, now
from requests_toolbelt.sessions import BaseUrlSession

from ereuse_workbench.benchmarker import Benchmarker
from ereuse_workbench.computer import Computer, PrivateFields
from ereuse_workbench.eraser import EraseType, Eraser
from ereuse_workbench.os_installer import Installer
from ereuse_workbench.tester import Smart, Tester
from ereuse_workbench.usb_sneaky import USBSneaky


class Workbench:
    """
    Create a full report of your computer with serials,
    testing, benchmarking, erasing and installing an OS.
    """

    def __init__(self, smart: Smart = False, erase: EraseType = False, erase_steps: int = 1,
                 erase_leading_zeros: bool = False, stress: int = 0,
                 install: str = False, server: str = None, Tester: Type[Tester] = Tester,
                 Computer: Type[Computer] = Computer, Eraser: Type[Eraser] = Eraser,
                 Benchmarker: Type[Benchmarker] = Benchmarker,
                 USBSneaky: Type[USBSneaky] = USBSneaky, Installer: Type[Installer] = Installer):
        """
        Configures this Workbench.

        :param smart: Should we perform a SMART test to the hard-drives?
                      If so, pass :attr:`.Workbench.Smart.short` for a
                      short test and :attr:`.Workbench.Smart.long` for a
                      long test. Falsy values disables the
                      functionality.
        :param erase: Should we erase the hard-drives? Pass-in a
                      :attr:`.Workbench.Erase.normal` to perform
                      a normal erasure (quite secure) or
                      :attr:`.Workbench.Erase.sectors` to perform
                      a slower but fully secured erasure. Falsy values
                      disables the functionality.
                      See `a detailed explanation of the erasure
                      process in the FAQ
                      <https://ereuse-org.gitbooks.io/faq/content/w-
                      hich-is-the-data-wiping-process-performed.html>`_.
        :param erase_steps: In case `erase` is truthy, how many steps
                            overriding data should we perform? Policies
                            and regulations may set a specific value.
        :param erase_leading_zeros: In case `erase` is truthy,
                                    should we finish erasing with an
                                    extra step that writes zeroes?
                                    This can be enforced
                                    by policy and regulation.
        :param stress: How many minutes should stress the machine.
                       0 minutes disables this test. A stress test
                       puts the machine at 100% (CPU, RAM and HDD)
                       to ensure components can handle heavy work.
        :param install: Image name to install. A falsy value will
                        disable installation. The image is a FSA file
                        that will be installed on the first hard-drive.
                        Do not add the extension ('.fsa').
        :param server: An URL pointing to a WorkbenchServer. Setting a
                       truthy value will turn-on server functionality
                       like USBSneaky module, sending snapshots to
                       server and getting configuration from it.
        :param Tester: Testing class to use to perform tests.
        :param Computer: Computer class to use to retrieve computer
                         information.
        """
        if os.geteuid() != 0:
            raise EnvironmentError('Execute Workbench as root.')

        init(autoreset=True)
        self.smart = smart
        self.erase = erase
        self.erase_steps = erase_steps
        self.erase_leading_zeros = erase_leading_zeros
        self.stress = stress
        self.server = server
        self.uuid = uuid.uuid4()
        self.install = install
        self.install_path = Path('/media/workbench-images')

        if self.server:
            # Override the parameters from the configuration from the server
            self.session = BaseUrlSession(base_url=self.server)
            self.session.verify = False
            self.session.headers.update({'Content-Type': 'application/json'})
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.config_from_server()
            if self.install:
                # We get the OS to install from the server through a mounted samba
                self.mount_images(self.server)
            # By setting daemon=True USB Sneaky will die when we die
            self.usb_sneaky = Process(target=USBSneaky, args=(self.uuid, server), daemon=True)

        self.phases = 1 + bool(self.smart) + bool(self.stress) + bool(self.erase) + \
                      bool(self.install)
        """
        The number of phases we will be performing.
        
        A phase is a piece of execution. Gathering hardware info is
        the first phase, and executing a smart test is the second one.
        """

        self.installer = Installer()
        self.tester = Tester()
        self.eraser = Eraser(self.erase, self.erase_steps, self.erase_leading_zeros)
        self.benchmarker = Benchmarker()
        self.Computer = Computer

    def config_from_server(self):
        """Configures the Workbench from a config endpoint in the server."""
        r = self.session.get('/config')
        r.raise_for_status()
        for key, value in r.json().items():
            if key == 'smart' and value:
                self.smart = Smart(value)
            elif key == 'erase' and value:
                self.erase = EraseType(value)
            else:
                setattr(self, key, value)

    def mount_images(self, server: str):
        """Mounts the folder where the OS images are."""
        self.install_path.mkdir(parents=True, exist_ok=True)
        ip, _ = urlparse(server).netloc.split(':')
        try:
            run(('mount',
                 '-t', 'cifs',
                 '-o', 'guest,uid=root,forceuid,gid=root,forcegid',
                 '//{}/workbench-images'.format(ip),
                 str(self.install_path)), universal_newlines=True, check=True)
        except CalledProcessError as e:
            raise CannotMount('Did you umount?') from e

    def run(self) -> str:
        """
        Executes Workbench on this computer and
        returns a valid JSON for DeviceHub.
        """
        try:
            return self._run()
        except Exception:
            print('{}Workbench panic - unexpected exception found. Please take '
                  'a photo of the screen and send it to eReuse Workbench Developers.'
                  .format(Fore.RED))
            raise
        finally:
            if self.server and self.install:
                # Un-mount images
                try:
                    run(('umount', str(self.install_path)), universal_newlines=True, check=True)
                except CalledProcessError as e:
                    raise CannotMount() from e

    def _run(self) -> str:
        print('{}Starting eReuse.org Workbench'.format(Fore.CYAN))
        if self.server:
            self.usb_sneaky.start()

        print('{} Getting computer information...'.format(self._print_phase(1)))
        init_time = now()
        computer_getter = self.Computer(self.benchmarker)
        computer, components = computer_getter.run()
        snapshot = {
            'device': computer,
            'components': components,
            '_uuid': self.uuid,
            '_totalPhases': self.phases,
            '_phases': 0,  # Counter of phases we have executed
            'snapshotSoftware': 'Workbench',
            'inventory': {
                'elapsed': now() - init_time
            },
            # The version of Workbench
            # from https://stackoverflow.com/a/2073599
            # This throws an exception if you git clone this package
            # and did not install it with pip
            # Perform ``pip install -e .`` or similar to fix
            'version': pkg_resources.require('ereuse-workbench')[0].version,
            'automatic': True,
            'date': now(),  # todo we should ensure debian updates the machine time from Internet
            '@type': 'devices:Snapshot'
        }
        self.after_phase(snapshot, init_time)
        hdds = tuple(c for c in components if c['@type'] == 'HardDrive')

        if self.benchmarker:
            snapshot['benchmarks'] = [
                self.benchmarker.benchmark_memory()
            ]

        if self.smart:
            print('{} Run SMART test and benchmark hard-drives...'.format(self._print_phase(2)))
            for hdd in hdds:
                hdd['test'] = self.tester.smart(hdd[PrivateFields.logical_name], self.smart)
                if hdd['test']['error']:
                    print('{}Failed SMART for HDD {}'.format(Fore.RED, hdd.get('serialNumber')))
            self.after_phase(snapshot, init_time)

        if self.stress:
            print('{} Run stress tests for {} mins...'.format(self._print_phase(3), self.stress))
            snapshot['tests'] = [self.tester.stress(self.stress)]
            self.after_phase(snapshot, init_time)

        if self.erase:
            text = '{} Erase Hard-Drives with {} method, {} steps and {} overriding with zeros...'
            print(text.format(self._print_phase(4), self.erase.name, self.erase_steps,
                              '' if self.erase_leading_zeros else 'not'))
            for hdd in hdds:
                hdd['erasure'] = self.eraser.erase(hdd[PrivateFields.logical_name])
                if not hdd['erasure']['success']:
                    print('{}Failed erasing HDD {}'.format(Fore.RED, hdd.get('serialNumber')))
            self.after_phase(snapshot, init_time)

        if self.install:
            print('{} Install {}...'.format(self._print_phase(5), self.install))
            snapshot['osInstallation'] = self.installer.install(self.install_path / self.install)

            if not snapshot['osInstallation']['success']:
                print('{}Failed installing OS'.format(Fore.RED))
            self.after_phase(snapshot, init_time)
        print('{}eReuse.org Workbench has finished properly.'.format(Fore.GREEN))

        # Comply with DeviceHub's Snapshot
        snapshot.pop('_phases', None)
        snapshot.pop('_totalPhases', None)
        return json.dumps(snapshot, skipkeys=True, cls=DeviceHubJSONEncoder, indent=2)

    def after_phase(self, snapshot: dict, init_time: datetime):
        snapshot['_phases'] += 1
        snapshot['elapsed'] = now() - init_time
        if self.server:
            # Send to server
            url = '/snapshots/{}'.format(snapshot['_uuid'])
            data = json.dumps(snapshot, cls=DeviceHubJSONEncoder, skipkeys=True)
            self.session.patch(url, data=data).raise_for_status()

    @staticmethod
    def _print_phase(phase: int):
        return '[ {}Phase {}{} ]'.format(Fore.CYAN, phase, Fore.RESET)


class CannotMount(Exception):
    pass
