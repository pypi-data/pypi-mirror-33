import os
import subprocess

import semver

from spell.cli.constants import BLACKLISTED_FILES, WHITELISTED_FILEEXTS


def has_staged(repo):
    """given a git.Repo, returns True if there are staged changes in the index"""
    if repo.is_dirty(index=True, working_tree=False, untracked_files=False):
        return len(get_staged_filenames(repo)) > 0
    return False


def get_staged_filenames(repo):
    staged_fnames = []
    for diff in repo.index.diff("HEAD"):
        # For file creation, a_path will be None so fall back to b_path
        path = diff.a_path or diff.b_path
        if path.split(".")[-1] not in WHITELISTED_FILEEXTS:
            staged_fnames.append(path)
    return staged_fnames


def has_unstaged(repo):
    """given a git.Repo, returns True if there are unstaged changes in the working tree"""
    if repo.is_dirty(index=False, working_tree=True, untracked_files=False):
        return len(get_unstaged_filenames(repo)) > 0
    return False


def get_unstaged_filenames(repo):
    return [
        diff.a_path
        for diff in repo.index.diff(None)
        if diff.a_path.split(".")[-1] not in WHITELISTED_FILEEXTS
    ]


def has_untracked(repo):
    """given a git.Repo, returns True if there are untracked files in the working tree"""
    if repo.is_dirty(index=False, working_tree=False, untracked_files=True):
        return len(get_untracked_filenames(repo)) > 0
    return False


def get_untracked(repo):
    return "\n".join(["\t{}".format(f) for f in get_untracked_filenames(repo)])


def get_untracked_filenames(repo):
    return [f for f in repo.untracked_files if os.path.split(f)[1] not in BLACKLISTED_FILES]


def get_git_repo(f):
    """decorator that passes the git repo into the called function as git_repo kwarg"""
    import git

    def inner(*args, **kwargs):
        git_repo = None
        try:
            git_repo = git.Repo(os.getcwd(), search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            pass
        f(*args, git_repo=git_repo, **kwargs)
    return inner


def git_version():
    output = subprocess.check_output(["git", "--version"]).decode()
    return semver.parse_version_info(output.split()[2])
