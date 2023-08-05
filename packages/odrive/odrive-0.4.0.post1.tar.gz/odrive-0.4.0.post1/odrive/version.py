
import re
import subprocess
import os
import sys

def version_str_to_tuple(version_string):
    """
    Converts a version string to a tuple of the form
    (major, minor, revision, prerelease)

    Example: "fw-v0.3.6-23" => (0, 3, 6, True)
    """
    regex=r'.*v([0-9a-zA-Z]+).([0-9a-zA-Z]+).([0-9a-zA-Z]+)(.*)'
    return (int(re.sub(regex, r"\1", version_string)),
            int(re.sub(regex, r"\2", version_string)),
            int(re.sub(regex, r"\3", version_string)),
            (re.sub(regex, r"\4", version_string) != ""))


def get_version_from_git():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    try:
        # Determine the current git commit version
        git_tag = subprocess.check_output(["git", "describe", "--always", "--tags", "--dirty=*"],
            cwd=script_dir)
        git_tag = git_tag.decode(sys.stdout.encoding).rstrip('\n')

        (major, minor, revision, is_prerelease) = version_str_to_tuple(git_tag)

        # if is_prerelease:
        #     revision += 1
        return git_tag, major, minor, revision, is_prerelease

    except Exception as ex:
        print(ex)
        return "[unknown version]", 0, 0, 0, 1

def get_version_str(git_only=False, is_post_release=False):
    """
    Returns the versions of the tools
    If git_only is true, the version.txt file is ignored even
    if it is present.
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Try to read the version.txt file that is generated during
    # the packaging step
    version_file_path = os.path.join(script_dir, 'version.txt')
    if os.path.exists(version_file_path) and git_only == False:
        with open(version_file_path) as version_file:
            return version_file.readline().rstrip('\n')
    
    _, major, minor, revision, unreleased = get_version_from_git()
    version = '{}.{}.{}'.format(major, minor, revision)
    if is_post_release:
        version += ".post"
    elif unreleased:
        version += ".dev"
    return version

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Version Dump\n')
    parser.add_argument("--output", type=argparse.FileType('w'), default='-',
                        help="C header output file")
    
    args = parser.parse_args()

    git_name, major, minor, revision, unreleased = get_version_from_git()
    args.output.write('#define FW_VERSION "{}"\n'.format(git_name))
    args.output.write('#define FW_VERSION_MAJOR {}\n'.format(major))
    args.output.write('#define FW_VERSION_MINOR {}\n'.format(minor))
    args.output.write('#define FW_VERSION_REVISION {}\n'.format(revision))
    args.output.write('#define FW_VERSION_UNRELEASED {}\n'.format(1 if unreleased else 0))
