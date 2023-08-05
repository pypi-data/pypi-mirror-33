
# =========================================
#       DEPS
# --------------------------------------

import sys
import os
import logging
import coloredlogs

from os import path

CURRENT_PATH = path.abspath(path.dirname(__file__))
ROOT_PATH = path.abspath(path.join(CURRENT_PATH, '..'))

try:
    try:
        sys.path.remove(CURRENT_PATH)
    except:
        pass

    sys.path.index(ROOT_PATH)

except ValueError:
    sys.path.insert(0, ROOT_PATH)

import semver
import git

from easypackage.utils.banner import banner


# =========================================
#       CONSTANTS
# --------------------------------------

DEFAULT_GIT_ORIGIN = 'origin'
DEFAULT_GIT_BRANCH = 'master'
DEFAULT_GIT_VERSION_BASE_TAG = 'v0.0.0'
DEFAULT_GIT_VERSION_ADD_FILES = ['.']
DEFAULT_GIT_VERSION_COMMIT_PREFIX = 'version: '

DEFAULT_LOGGER_LABEL = 'release'
DEFAULT_LOGGER = logging.basicConfig(level = logging.INFO) and logging.getLogger(DEFAULT_LOGGER_LABEL)

# DEFAULT_LOGGER.addHandler(logging.StreamHandler(sys.stderr))
# DEFAULT_LOGGER.addHandler(logging.StreamHandler(sys.stdout))

coloredlogs.install(logger = DEFAULT_LOGGER)


# =========================================
#       FUNCTIONS
# --------------------------------------

def release(project_path, logger = None):
    raise NotImplementedError('This feature is still work in progress, sorry!')

    # TODO: logger = logger or DEFAULT_LOGGER

    """
    Automatically tag and release current project source to the project Git repository,
    if version tag specified in package config file (`package.json`) not been released.

    Usage:

        easypackage.release.release(__file__)
        easypackage.release.release('./src')

    """

    __filename = path.realpath(__file__)
    __dirname = path.dirname(__filename)

    # TODO: use `pkg = easypackage.load()` dependency `@grimen/python-easypackage`
    try:
        with open(path.abspath(path.join(__dirname, '..', 'package.json'))) as package_file:
            pkg = json.load(pkg_file)
    except IOError:
        pkg = {}

    # NOTE: project root path can be passed as additional argument (in case this script is moved outside)
    project_path = path.abspath(path.normpath(sys.argv.pop()))

    if (project_path == __filename):
        project_path = path.abspath(path.join(__dirname))

    error = None

    if not path.exists(project_path):
        message = 'Not a valid project path: `{0}`'.format(project_path)

        print('ERROR {0}'.format(message))

        error = Exception(message)

    if not path.exists(path.join(project_path, '.git')):
        message = 'Not a valid Git repository: `{0}`'.format(project_path)

        print('ERROR {0}'.format(message))

        error = Exception(message)

    print('PROJECT PATH {0}'.format(project_path))

    if not error:
        git_repo = None

        try:
            git_repo = git.Repo(project_path)

        except Exception as error:
            raise error

        git_tag = None

        try:
            if len(git_repo.tags):
                git_tag = str(git_repo.tags[-1])
            else:
                git_tag = DEFAULT_GIT_VERSION_BASE_TAG

            print('GIT TAG {0}'.format(git_tag))

        except Exception as error:
            raise error

        git_version = None

        try:
            git_version = (git_tag or DEFAULT_GIT_VERSION_BASE_TAG).strip()

            print('GIT VERSION {0}'.format(git_version))

        except Exception as error:
            raise error

        package_version = None

        try:
            package_version = pkg.get('version', DEFAULT_GIT_VERSION_BASE_TAG)

            print('PACKAGE VERSION {0}'.format(package_version))

        except Exception as error:
            raise error

        package_semver_version = package_version.replace('v', '')
        git_semver_version = package_version.replace('v', '')

        print(package_semver_version, git_semver_version)

        is_released = (semver.compare(package_semver_version, git_semver_version) <= 0)
        is_released_message = is_released and 'YES' or 'NO'

        print('IS ALREADY RELEASED?: {0}'.format(is_released_message))

        if is_released:
            print('ALREADY RELEASED: To make a new release; bump `version` field inside of `package.json` in project root.')

        else:
            git_tag_new = 'v{0}'.format(package_semver_version)
            git_version_add_files = DEFAULT_GIT_VERSION_ADD_FILES
            git_version_commit_message = '{0}{1}'.format(DEFAULT_GIT_VERSION_COMMIT_PREFIX, git_tag_new)

            print('NOT RELEASED: Releasing version `{0}`...'.format(git_tag_new))

            try:
                print('GIT ADD')

                git_repo.index.add(git_version_add_files)

            except Exception as error:
                raise error

            try:
                print('GIT COMMIT {0}'.format(git_version_commit_message))

                git_repo.index.commit(git_version_commit_message)

            except Exception as error:
                raise error

            try:
                print('GIT TAG {0}'.format(git_tag_new))

                git_repo.create_tag(git_tag_new)

            except Exception as error:
                raise error

            try:
                print('GIT PUSH')

                remote = repo.remote('origin')
                head = repo.head

                # branch = repo.active_branch

                # if branch:
                #     branch = branch.name

                # branch = branch or DEFAULT_GIT_BRANCH

                print('remote', remote)
                print('head', head)

                remote.push(head.reference, tags = True)

            except Exception as error:
                raise error

        print('DONE')


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':

    with banner(__file__):

        search_path = path.abspath(path.normpath(sys.argv.pop()))
        result = release(search_path)

        print('release({0})\n\n  => {1}'.format(search_path, result))
