"""Clone git repositories and keep repo directories organized."""

import argparse
import logging
import os
import subprocess
import urllib.parse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def clone(git_url, repohome):
    """Clone git URL to a specified root directory."""

    clone_path = _get_clone_directory(repohome, git_url)
    if os.path.isdir(clone_path):
        logger.info("Directory '%s' already exists. Quit.", clone_path)
        return

    os.makedirs(clone_path)
    git_cmd = 'git', 'clone', git_url, clone_path
    clone_result = subprocess.run(git_cmd)
    if clone_result.returncode != 0:
        logger.error("git clone failed.")
        os.rmdir(clone_path)


def _get_clone_directory(repohome, git_url):
    """Return directory path, where the repo should be cloned."""
    url = urllib.parse.urlparse(git_url)
    # omit '.git', if present:
    path_dirname = url.path if not url.path.endswith('.git') else url.path[:-4]
    # omit username, if present: alcm-b@bitbucket.org -> bitbucket.org
    path_servername = url.netloc.split('@').pop()
    return os.path.join(repohome, path_servername, path_dirname.lstrip('/'))


def _parseargs():
    """Parse command line arguments"""
    argdef = argparse.ArgumentParser(description="Clone a git URL")
    argdef.add_argument('git_url', help="git URL to be cloned")
    argdef.add_argument('--repohome', default='/tmp/repoman',
                         help="Root directory, where to keep git repos.")

    return argdef.parse_args()

def run():
    """Provide entry point for setuptools."""
    args = _parseargs()
    clone(args.git_url, args.repohome)
