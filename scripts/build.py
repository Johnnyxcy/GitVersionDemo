import json
import pathlib
import typing

from git import Repo


# {major}.{minor}.{patch}-{tag}+{buildmetadata}


def build(target_platform: typing.Literal['windows', 'mac'], target_architecture: str) -> None:
    root = pathlib.Path(__file__).parent.parent
    version = json.load(open(root.joinpath('package.json')))['version']
    repo = Repo(root.joinpath('.git'))

    branch_name = repo.active_branch.name
    semantic_version = f'{version}'
    if branch_name == 'develop':
        semantic_version += '-alpha'
    elif branch_name.startswith('release'):
        semantic_version += '-beta'
    else:
        semantic_version += f'-{branch_name}'

    semantic_version += f'+{str(repo.head.commit)[:7]}'
    print(semantic_version)
