from karamel.packages import *
from karamel.exception import KaramelException
from karamel.logger import logger

from .command import Command

__command__ = 'install'
__description__ = 'Install a package'

class InstallCommand(Command):

    def __init__(self, packages_file_url, package_install_dir):
        super().__init__(__command__, __description__)
        self.add_argument('package', nargs='*')
        self.add_argument('-f', '--freeze')
        self.packages_file_url = packages_file_url
        self.package_install_dir = get_package_install_dir(package_install_dir)

    def on_package_downloading(self, package_name):
        logger.info('Downloading \'{}\''.format(package_name))

    def on_package_installing(self, package_name):
        logger.info('Installing \'{}\''.format(package_name))

    def on_package_install_success(self, package_name):
        logger.info('Successfully installed \'{}\''.format(package_name))

    def on_package_already_installed(self, package_name, package_path):
        logger.info('Package \'{}\' already installed in \'{}\''.format(package_name, package_path))

    def on_package_not_found(self, package_name):
        logger.error('Package not found \'{}\''.format(package_name))

    def on_package_bad_version_provided(self, package_name, version):
        logger.error('Could not find the version \'{}\' for package \'{}\''.format(package_name, version))

    def callback(self, args):
        packages_to_install = args.package

        if args.freeze:
            with open(args.freeze, 'r') as stream:
                packages_freeze = [l.strip() for l in stream]
            packages_to_install += packages_freeze

        install_packages(
            self.packages_file_url,
            self.package_install_dir,
            packages_to_install,
            self.on_package_downloading,
            self.on_package_installing,
            self.on_package_install_success,
            self.on_package_already_installed,
            self.on_package_not_found,
            self.on_package_bad_version_provided)
