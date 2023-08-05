from karamel.packages import *
from karamel.exception import KaramelException
from karamel.logger import logger

from .command import Command

__command__ = 'freeze'
__description__ = 'Freeze packages'

class FreezeCommand(Command):

    def __init__(self, packages_file_url, package_install_dir):
        super().__init__(__command__, __description__)
        self.add_argument('package', nargs='*')
        self.packages_file_url = packages_file_url
        self.package_install_dir = get_package_install_dir(package_install_dir)

    def callback(self, args):
        if args.package != []:
            package_freezed = freeze_packages(self.package_install_dir, args.package)
        else:
            package_freezed = freeze_packages(self.package_install_dir)

        for package, ref in package_freezed.items():
            print('{}=={}'.format(package, ref))
