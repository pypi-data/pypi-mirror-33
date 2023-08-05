from karamel.packages import *
from karamel.exception import KaramelException
from karamel.logger import logger

from .command import Command

__command__ = 'list'
__description__ = 'List packages'

class ListCommand(Command):

    def __init__(self, packages_file_url, package_install_dir):
        super().__init__(__command__, __description__)
        self.add_argument('--installed', action='store_true')
        self.packages_file_url = packages_file_url
        self.package_install_dir = get_package_install_dir(package_install_dir)

    def callback(self, args):
        if args.installed:
            packages = get_installed_packages(self.package_install_dir)
        else:
            packages = read_packages_files(self.packages_file_url)

        if packages:
            for package_name in packages:
                logger.info('{}'.format(package_name))
