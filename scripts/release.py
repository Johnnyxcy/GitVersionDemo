import pathlib
from git_utils import get_git_version

def release() -> None:

    print(get_git_version(pathlib.Path(__file__).parent.parent))


if __name__ == '__main__':
    release()