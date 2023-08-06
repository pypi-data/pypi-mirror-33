"""python -m stilt.project <path/to/project>

"""
import os
import sys
from pathlib import Path
from subprocess import call

import requests


_defaults = {
    'mkdir': {
        'parents': False,
        'exist_ok': False
    },
    'python': {
        'gitignore': 'https://raw.githubusercontent.com/' +
        'github/gitignore/master/Python.gitignore'
    },
}


def main(args):
    ppath = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else None
    if ppath is None:
        sys.exit('error: specify project path')

    # Steps:
    #   1) Create project path
    #   2) Populate initial file content
    #   3) Initialize git

    #   1) Create project path
    path_ = Path(ppath)
    path_.mkdir(**_defaults['mkdir'])

    #   2) Populate initial file content
    try:
        response = requests.get(_defaults['python']['gitignore'])
        if response.status_code == 200 and response.encoding == 'utf-8':
            with open(os.path.join(path_, '.gitignore'),
                      'wt', encoding=response.encoding) as gitignore:
                gitignore.write(response.text)
        else:
            print('error: expected status code 200 and encoding utf-8',
                  file=sys.stderr)
    except Exception as e:
        print('error:', e, file=sys.stderr)

    #   3) Initialize git
    #      Install pre-commit?
    try:
        call('git init %(projectpath)s' %
             {'projectpath': path_})
    except OSError as e:
        print('error:', e, file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv)
