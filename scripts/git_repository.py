import pathlib
import typing
import re


class GitRepository(object):
    """Git 仓库管理"""
    def __init__(self, repo_path: pathlib.Path) -> None:
        self.__repo_path = repo_path
        self.__git = pathlib.Path(self.__repo_path, '.git')

    @property
    def repo_path(self) -> pathlib.Path:
        return self.__repo_path

    def get_current_branch(self) -> str:
        """获取当前 HEAD 的分支名称

        Raises:
            ValueError: 如果当前 HEAD 不是分支而是 commit, raise

        Returns:
            str: 当前 HEAD 的分支名称
        """
        head = self.__get_current_head()
        if re.fullmatch(r'^[0-9a-f]{40}$', head):
            raise ValueError(f'Current HEAD {head} is only commit, not on any branch')

        ref_match = re.findall(r'^ref: (.*)$', head)
        return ref_match[0]

    def get_current_commit(self) -> typing.Optional[str]:
        """获取当前 HEAD 的 commit 号

        Returns:
            typing.Optional[str]: 当前 HEAD 的 commit 号, 如果找不到返回 None
        """
        head = self.__get_current_head()

        if re.fullmatch(r'^[0-9a-f]{40}$', head):
            return head

        ref_match = re.findall(r'^ref: (.*)$', head)

        if not ref_match:
            return None

        return self.__get_commit_by_ref(ref_match[0])

    def get_commit_by_branch(self, branch_name: str) -> str:
        """获取分支上的最新 commit 号

        Args:
            branch_name (str): 需要检查的分支名称

        Returns:
            str: 该分支上的最新 commit 号
        """
        return self.__get_commit_by_ref(f'refs/heads/{branch_name}')

    def __get_commit_by_ref(self, ref: str) -> str:
        if not ref.startswith('refs/heads'):
            raise ValueError(f'ref must starts with "refs/heads", given {ref}')
        return open(self.__git.joinpath(ref), encoding='utf-8').read().strip()
       
    def __get_current_head(self) -> str:
        head_path = self.__git.joinpath('HEAD')
        
        if not head_path.exists():
            raise FileNotFoundError(f'{head_path.as_posix()} not exists, {self.__repo_path.as_posix()} is not a valid git repo_path')

        return open(head_path).read()
