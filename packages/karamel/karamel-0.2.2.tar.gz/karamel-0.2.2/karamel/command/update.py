import os, git

from karamel.packages import *
from karamel.exception import KaramelException
from karamel.logger import logger

from .command import Command

__command__ = 'update'
__description__ = 'Update a package'

class UpdateCommand(Command):

    def __init__(self, packages_file_url, package_install_dir):
        super().__init__(__command__, __description__)
        self.add_argument('package')
        self.packages_file_url = packages_file_url
        self.package_install_dir = get_package_install_dir(package_install_dir)

    def callback(self, args):
        packages = read_packages_files(self.packages_file_url)

        if args.package in packages:
            package = packages[args.package]
            package_path = os.path.join(self.package_install_dir, args.package)

            if not os.path.isdir(package_path):
                raise KaramelException('Package is not installed')
            else:
                logger.info('Updating {}'.format(args.package))
                package_path = os.path.join(self.package_install_dir, args.package)
                git.Git(package_path).pull()
                logger.info('Successfully updated {}'.format(args.package))

        else:
            raise KaramelException('Package not found')
