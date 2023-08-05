from karamel.packages import *
from karamel.logger import logger

from .command import Command

__command__ = 'search'
__description__ = 'Search package'

class SearchCommand(Command):

    def __init__(self, packages_file_url):
        super().__init__(__command__, __description__)
        self.add_argument('pattern')
        self.packages_file_url = packages_file_url

    def callback(self, args):
        packages_found = search_packages(self.packages_file_url, args.pattern)

        for package_name, package_info in packages_found.items():
            logger.info('{}'.format(package_name))
            logger.info('  {}'.format(package_info['description']))
            logger.info('  {}'.format(package_info['url']))
            logger.info('')
