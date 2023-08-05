import os, shutil

from karamel.packages import *
from karamel.exception import KaramelException
from karamel.logger import logger

from .command import Command

__command__ = 'uninstall'
__description__ = 'Uninstall a package'

class UninstallCommand(Command):

    def __init__(self, packages_file_url, package_install_dir):
        super().__init__(__command__, __description__)
        self.add_argument('package')
        self.add_argument('-y', '--yes', action='store_true')
        self.packages_file_url = packages_file_url
        self.package_install_dir = get_package_install_dir(package_install_dir)

    def callback(self, args):
        packages = read_packages_files(self.packages_file_url)
        packages_installed = get_installed_packages(self.package_install_dir)

        if args.package in packages_installed:
            package_path = os.path.join(self.package_install_dir, args.package)
            logger.info('Uninstalling {}:'.format(args.package))
            logger.info('  {}'.format(package_path))

            install = False
            if not args.yes:
                response = input('Proceed (y/n)? ')
                if response == 'y':
                    install = True
                elif response != 'n':
                    raise KaramelException('Bad response')
            else:
                install = True

            if install:
                shutil.rmtree(package_path)
                logger.info('Successfully uninstalled {}'.format(args.package))

        else:
            raise KaramelException('Package not installed: cannot find {} in {}'.format(args.package, self.package_install_dir))
