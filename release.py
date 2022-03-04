# -*- coding: utf-8 -*-
"""
:文件名: scripts/release.py

:创建时间: 03/04/2022 10:50 AM

:作者: 许翀轶

:模块描述: release 脚本帮助

*Copyright (c) 2021 上海博佳医药科技有限公司*
"""
import logging
import pathlib
import json
import pathlib
import re
import sys
import typing
import time
import git
import git.repo as git_repo


class _ConsoleLoggerFormatter(logging.Formatter):
    grey = '\x1b[38;20m'
    light_green = '\x1b[92;20m'
    yellow = '\x1b[33;20m'
    red = '\x1b[31;20m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    record_fmt = '[%(levelname)s][%(asctime)s] %(message)s'

    FORMATS = {
        logging.DEBUG: record_fmt,
        logging.INFO: light_green + record_fmt + reset,
        logging.WARNING: yellow + record_fmt + reset,
        logging.ERROR: red + record_fmt + reset,
        logging.CRITICAL: bold_red + record_fmt + reset
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def _round(value: float, decimal: int = 3) -> float:
    return round(value, decimal)


def release(release_type: typing.Literal['patch', 'minor'], ignore_uncommitted_changes: bool = False) -> None:
    """release 支持"""
    logger: typing.Final[logging.Logger] = logging.Logger("MaSReleaser", level=logging.DEBUG)
    # create console handler
    _console_handler = logging.StreamHandler(stream=sys.stdout)
    _console_handler.setFormatter(_ConsoleLoggerFormatter())
    logger.addHandler(_console_handler)

    
    try:
        root = pathlib.Path(__file__).parent.parent
        sys.path.append(root.as_posix())

        package_json_fp = root.joinpath('package.json')
        package_json: typing.Final[typing.Dict[str, typing.Any]] = json.load(open(package_json_fp, encoding='utf-8'))
        app_version = package_json['version']
        if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', app_version):
            raise ValueError('package.json 中的 version 字段必须是 {major}.{minor}.{patch}, 并且每个关键词都是自然数')

        logger.info('================== Arguments ==================')
        logger.info(f'* type={release_type}')
        logger.info(f'* ignore_uncommitted_changes={ignore_uncommitted_changes}')

        repo = git_repo.Repo(root.joinpath('.git'))
        if repo.is_dirty(untracked_files=True):
            if not ignore_uncommitted_changes:
                raise ValueError('Uncommitted changes found, make sure you have committed all changes')
            logger.warning(f'Uncommitted changes found but is surpressed with ignore_uncommitted_changes=True')

        start_time = time.time()
        logger.info(f'Pulling from origin {repo.remotes.origin.url}...')
        repo.remotes.origin.pull()
                
        major, minor, patch = app_version.split(r'.')
        current_commit = repo.head.commit
        branch_name = repo.active_branch.name
        sha = current_commit.hexsha
        author_info = f'{current_commit.author.name}<{current_commit.author.email}>'
        datetime_info = repo.head.commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S%z')
        logger.debug('=================== Git =====================')
        logger.debug(f'* branch={branch_name}')
        logger.debug(f'* sha={sha}')
        logger.debug(f'* author_info={author_info}')
        logger.debug(f'* datetime_info={datetime_info}')

        def _branch_exists_on_remote(branch_name: str) -> bool:
            for ref in typing.cast(typing.Iterable[git.RemoteReference], repo.remote().refs):
                if branch_name in ref.name:
                    return True

            return False

        def _change_version(version: str) -> None:
            package_json['version'] = version
            logger.info(f'Versioning {version}...')
            open(package_json_fp, mode='w', encoding='utf-8').write(json.dumps(package_json, ensure_ascii=True, indent=4))
            

        if release_type == 'patch':
            semantic_version = f'{major}.{minor}.{int(patch) + 1}'
            hotfix_branch_name = f'hotfix/v{semantic_version}'
            logger.info(f'Starting new hotfix branch {hotfix_branch_name}...')
            if branch_name != 'master':
                raise RuntimeError('You are **MUST** working on "master" branch when you are trying to start a hotfix branch')
            
            if _branch_exists_on_remote(hotfix_branch_name):
                raise RuntimeError(f'{hotfix_branch_name} is already exists, stop release')
            hotfix_branch_head = repo.create_head(hotfix_branch_name)
            hotfix_branch_head.checkout()

            _change_version(semantic_version)
            
            repo.git.add(A=True)
            repo.git.commit(m=f'hotfix: Branching hotfix(v{semantic_version}) from master(v{major}.{minor}.{patch})\n\n@bypass-review')
            logger.info(f'Pushing hotfix branch {hotfix_branch_name}...')
            repo.git.push('--set-upstream', 'origin', hotfix_branch_head)
        elif release_type == 'minor':
            semantic_version = f'{major}.{minor}.{patch}'

            release_branch_name = f'release/v{semantic_version}'
            logger.info(f'Starting new release branch {release_branch_name}...')
            if branch_name != 'develop':
                raise RuntimeError('You are **MUST** working on "develop" branch when you are trying to start a release branch')

            if _branch_exists_on_remote(release_branch_name):
                raise RuntimeError(f'{release_branch_name} is already exists, stop release')

            release_branch_head = repo.create_head(release_branch_name)
            release_branch_head.checkout()
            logger.info(f'Pushing release branch {release_branch_head}...')
            repo.git.push('--set-upstream', 'origin', release_branch_head)

            logger.info(f'Switch back to develop')
            repo.git.checkout('develop')

            _change_version(semantic_version)
            repo.git.add(A=True)
            repo.git.commit(m=f'develop: Development(v{semantic_version})\n\n@bypass-review')
            logger.info(f'Pushing develop...')
            repo.git.push('origin', 'develop')
        else:
            raise NotImplementedError(f'Release type {release_type} is not supported')

        end_time = time.time()
        logger.info(f'Release finished in {_round(end_time - start_time)}s')
        logger.info('ALL DONE!')
        exit(0)
    except Exception as e:
        logger.error('=================== ERROR ====================')
        logger.error('RELEASE FAILED', exc_info=e)
        exit(1)
