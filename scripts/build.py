import json
import pathlib
import platform
import re
import subprocess
import sys
from git.repo import Repo

from build_logger import logger


# {major}.{minor}.{patch}-{tag}+{buildmetadata}

def _exec(command: str) -> str:
    code, output = subprocess.getstatusoutput(command)
    if code != 0:
        raise OSError(f'Fail to execute {command} with code {code}, {output}')
    return output


class Builder(object):

    def build(self) -> None:
        """入口"""

        root = pathlib.Path(__file__).parent.parent
        version: str = json.load(open(root.joinpath('package.json')))['version']
        if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
            raise ValueError('package.json 中的 version 字段必须是 {major}.{minor}.{patch}, 并且每个关键词都是自然数')

        repo = Repo(root.joinpath('.git'))
        major, minor, patch = version.split(r'.')
        logger.info('Start building Modeling & Simulation Studio...')
        logger.debug('================= System Info =================')
        logger.debug(f'Platform Info  | {platform.platform()}')
        logger.debug(f'System Release | {platform.version()}')
        logger.debug(f'Node Name      | {platform.node()}')

        python_version = sys.version.replace('\n', '')
        logger.debug('================= Environment =================')
        logger.debug(f'* NodeJS {_exec("node --version")}')
        logger.debug(f'* g++ {_exec("g++ --version")}')
        logger.debug(f'* CMake {_exec("cmake --version")}')
        logger.debug(f'* Python {python_version}')

        current_commit = repo.head.commit
        sha = current_commit.hexsha

        branch_name = repo.active_branch.name
        logger.debug('===================== Git ======================')
        logger.debug(f'* branch={branch_name}')
        logger.debug(f'* sha={sha}')

        pre_release: str
        parent_commit_sha: str
        if branch_name == 'develop':
            pre_release = 'alpha'
            parent_commit_sha = repo.heads['main'].commit.hexsha
        elif branch_name.startswith('release') or branch_name.startswith('hotfix'):
            pre_release = 'beta'
            parent_commit_sha = repo.heads['develop'].commit.hexsha
        elif re.fullmatch(r'feature/T[0-9]+', branch_name) or re.fullmatch(r'fix/T[0-9]+', branch_name):
            manifest = branch_name.split('/')
            parent_commit_sha = repo.heads['develop'].commit.hexsha
            pre_release = manifest[1]
        else:
            raise NotImplementedError(f'Not Support build branch {branch_name}')

        build_meta = repo.git.rev_list('--count', f'{parent_commit_sha}..{current_commit}')
        semantic_version = f'{major}.{minor}.{patch}-{pre_release}.{build_meta}'
        print('semantic_version', semantic_version)

builder = Builder()

builder.build()
