import textwrap


class KaramelException(Exception):
    pass


class PackagesFileNotFound(KaramelException):

    message = textwrap.dedent('''\
        Cannot find the file {}.
        Check if the url or the path is valid and the file exist.
        If the package file is online also check your connection to Internet.''')

    def __init__(self, packages_file):
        message = self.message.format(packages_file)
        super().__init__(message)


class YamlErrorConfigFileParsing(KaramelException):

    message = textwrap.dedent('''\
        Yaml error during config file parsing.
        Please check the format of your config file.''')

    def __init__(self, exc):
        message = self.message
        super().__init__(message)


class YamlErrorConfigFileBadType(KaramelException):

    message = textwrap.dedent('''\
        The Yaml parsed should be a dict and it is a {}.
        Please check the format of your config file.''')

    def __init__(self, type_found):
        message = self.message.format(type_found)
        super().__init__(message)
