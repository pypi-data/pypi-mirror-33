import urllib.request
import urllib.error
import os, yaml, git, re

from karamel.exception import PackagesFileNotFound, YamlErrorConfigFileParsing, YamlErrorConfigFileBadType


empty = lambda *args, **kwargs: None

def read_packages_files(packages_file_paths):
    packages_file = {}
    for packages_file_path in packages_file_paths:
        new_packages_file = read_packages_file(packages_file_path)
        packages_file.update(new_packages_file)
    return packages_file


def read_packages_file(packages_file_path):
    try:
        response = urllib.request.urlopen(packages_file_path)
        content = response.read()
    except ValueError:
        try:
            stream = open(packages_file_path, 'r')
            content = stream.read()
            stream.close()
        except:
            raise PackagesFileNotFound(packages_file_path)
    except urllib.error.URLError:
        raise PackagesFileNotFound(packages_file_path)
    except urllib.error.HTTPError:
        raise PackagesFileNotFound(packages_file_path)

    return yaml.safe_load(content)


def get_package_install_dir(package_install_dir):
    package_install_dir = os.path.expanduser(package_install_dir)
    if package_install_dir != '' and not os.path.isdir(package_install_dir):
        os.makedirs(package_install_dir)
    return package_install_dir


def get_installed_packages(package_install_dir):
    if not os.path.isdir(package_install_dir):
        os.makedirs(package_install_dir)
    return os.listdir(package_install_dir)


def search_packages(packages_file_url, pattern):
    packages = read_packages_files(packages_file_url)
    packages_name = list(packages.keys())
    r = re.compile('.*{}.*'.format(pattern))
    packages_matching_pattern = filter(r.match, packages_name)

    packages_found = {}
    for package_name in packages_matching_pattern:
        if package_name in packages:
            packages_found[package_name] = packages[package_name]

    return packages_found


def install_packages(packages_file_url,
                     package_install_dir,
                     packages_to_install,
                     on_package_downloading=empty,
                     on_package_installing=empty,
                     on_package_install_success=empty,
                     on_package_already_installed=empty,
                     on_package_not_found=empty,
                     on_package_bad_version_provided=empty,
                     on_package_could_not_be_download=empty):

    packages = read_packages_files(packages_file_url)
    installed_packages = get_installed_packages(package_install_dir)

    for package_name in packages_to_install:

        # TODO verify package_name with regex

        version_requested = None
        if '==' in package_name:
            package_name, version_requested = package_name.split('==')

        if package_name in packages:
            package = packages[package_name]
            package_path = os.path.join(package_install_dir, package_name)

            found = False

            if not package_name in installed_packages:
                try:
                    on_package_downloading(package_name)
                    download_package(package_install_dir, package['url'], package_name)
                    on_package_installing(package_name)
                    on_package_install_success(package_name)
                    found = True
                except git.exc.GitCommandError:
                    on_package_could_not_be_download(package_name)

            else:
                try:
                    git.Git(package_path).pull()
                except git.exc.GitCommandError:
                    pass
                finally:
                    on_package_already_installed(package_name, package_path)
                    found = True

            if found:
                package_version = get_package_version(package_path)
                if version_requested and version_requested != package_version:
                    try:
                        change_package_version(package_path, version_requested)
                    except BadVersionProvided:
                        on_package_bad_version_provided(package_name, version_requested)
        else:
            on_package_not_found(package_name)


def freeze_packages(package_install_dir, packages_to_freeze=[]):
    packages_installed = get_installed_packages(package_install_dir)
    freeze = {}

    if packages_to_freeze == []:
        packages_to_freeze = packages_installed

    for package_name in packages_to_freeze:
        if package_name in packages_installed:
            package_path = os.path.join(package_install_dir, package_name)
            git_reference = get_package_version(package_path)
            freeze[package_name] = str(git_reference)
        else:
            freeze[package_name] = None

    return freeze


def download_package(package_install_dir, url, package_name):
    git.Repo.clone_from(url, os.path.join(package_install_dir, package_name))


def update_package(packages_file_url,
                   package_install_dir,
                   packages_to_update,
                   on_package_is_not_installed=empty,
                   on_package_updating=empty,
                   on_package_update_success=empty,
                   on_package_not_found=empty):

    packages = read_packages_files(packages_file_url)

    for package_name in packages_to_update:

        # TODO verify package_name with regex

        if package_name in packages:
            package = packages[package_name]
            package_path = os.path.join(package_install_dir, package_name)

            if not os.path.isdir(package_path):
                on_package_is_not_installed(package_name)

            else:
                on_package_updating(package_name)
                git.Git(package_path).pull()
                on_package_update_success(package_name)

        else:
            on_package_not_found(package_name)


class BadVersionProvided(Exception):
    pass


def change_package_version(package_path, package_version):
    try:
        repo_git = git.Repo(package_path).git
        repo_git.checkout(package_version)
    except git.exc.GitCommandError as e:
        raise BadVersionProvided()


def get_package_version(package_path):
    repo = git.Repo(package_path)
    version = repo.head.commit

    current_tag = next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)
    if current_tag: version = current_tag

    try: version = repo.head.ref
    except: pass

    return version


def package_dependencies(package_install_dir, package_name):
    config_file_path = os.path.join(package_install_dir, package_name, 'karamel.yaml')
    config = read_config_file(config_file_path)
    if config and 'dependencies' in config:
        return config['dependencies']
    else:
        return []


def read_config_file(config_file_name):
    if os.path.isfile(config_file_name):
        with open(config_file_name, 'r') as stream:
            try:
                content = stream.read()
                config = yaml.safe_load(content)
                if not isinstance(config, dict):
                    raise YamlErrorConfigFileBadType(type(config))
                return config
            except yaml.YAMLError as exc:
                raise YamlErrorConfigFileParsing(exc)
