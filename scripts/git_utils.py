import logging
import pathlib
import typing
import re

def get_git_version(repo: pathlib.Path) -> typing.Optional[str]:
    git = pathlib.Path(repo, '.git')
    head_path = git.joinpath('HEAD')
    
    if not head_path.exists():
        logging.warning(f'{head_path.as_posix()} not exists, {repo.as_posix()} is not a valid git repo')
        return

    head = open(head_path).read()

    if re.fullmatch(r'^[0-9a-f]{40}$', head):
        return head

    ref_match = re.findall(r'^ref: (.*)$', head)

    if not ref_match:
        return None

    ref = ref_match[0]
    ref_path = git.joinpath(ref)

    try:
        return open(ref_path, encoding='utf-8').read().strip()
    except:
        pass
    # packed_refs_path = git.joinpath('packed-refs')

    # refs_raw = ''
    # try:
    #     refs_raw = open(packed_refs_path, encoding='utf-8').read().strip()
    # except:
    #     return None

    # refs_regex = 


    return None