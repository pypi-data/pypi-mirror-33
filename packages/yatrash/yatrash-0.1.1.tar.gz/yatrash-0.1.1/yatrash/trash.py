import os
import sys
import shutil
import itertools
from pathlib import Path


default_trash_dir = '~/.trash'


def candidate_names(path):
    '''unused_names('f.txt') yields f.txt, f_1.txt, f_2.txt, ...'''
    yield path
    for i in itertools.count(1):
        yield path.with_name('{path.stem}_{i}.{path.suffix}'
                             .format(**locals()))


def trash(trash_files, trash_dir):
    # get/make trashdir
    if not trash_dir:
        # empty-string and non-existence are treated the same way
        trash_dir = os.environ.get('TRASH_DIR', '')
        if not trash_dir:
            trash_dir = default_trash_dir
    trash_path = Path(trash_dir).expanduser()
    trash_path.mkdir(exist_ok=True, parents=True)

    for trash_file_ in trash_files:
        trash_file = Path(trash_file_)
        if not trash_file.exists():
            print("{}: not found".format(trash_file))
            sys.exit(1)

        # get absolute path
        trash_file = Path(trash_file_).resolve()

        # get a destination which does not already exist
        try:
            trash_dest_candidate = (trash_path /
                                    trash_file.relative_to(Path.home()))
        except ValueError:
            trash_dest_candidate = (trash_path /
                                    '_root' / trash_file.relative_to('/'))

        trash_dest = next(filter(lambda path: not path.exists(),
                                 candidate_names(trash_dest_candidate)))

        trash_dest.parent.mkdir(exist_ok=True, parents=True)
        print('{} -> {}'.format(trash_file, trash_dest))

        try:
            shutil.move(trash_file, trash_dest)
        except Exception as e:
            print(str(e))
            sys.exit(2)


__all__ = ['trash']
