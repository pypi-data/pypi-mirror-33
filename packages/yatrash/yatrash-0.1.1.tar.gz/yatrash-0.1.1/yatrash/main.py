import argparse
from yatrash.trash import trash, default_trash_dir


description = '''
description:
  Safely move files into a trash can instead of rm.

  - Files are stored by their path relative to either ~ or /
    (preferring ~ if possible).
  - If an existing item with the same name is already in the trash, I
    add _1, _2, ... to the end of the filename.
  - Metadata is copied; See Python documentation on shutil.copy2 for
    details.'''[1:]

example = '''
example usage:
  $ touch a
  $ mkdir b
  $ touch b/c
  $ touch /tmp/d
  $ trash a b/c /tmp/d
  /home/sam/subdir/a.txt -> /home/sam/.trash/subdir/a.txt
  /home/sam/subdir/b/c.txt -> /home/sam/.trash/subdir/b/c.txt
  /tmp/d.txt -> /home/sam/.trash/_root/tmp/d.txt
  $ touch a
  $ trash a
  /home/sam/subdir/a.txt -> /home/sam/.trash/subdir/a_1.txt
'''[1:]

trash_dir_help = '''
destination for trash (defaults to ${{TRASH_DIR}}, and then '{}')
'''.strip().format(default_trash_dir)

trash_files_help = '''
the files to remove
'''.strip()


def main():
    parser = argparse.ArgumentParser(
        description=description, epilog=example,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('trash_files', type=str, nargs='+',
                        help=trash_files_help)
    parser.add_argument('--trash-dir', metavar='DIR', default='',
                        help=trash_dir_help)
    args = parser.parse_args()

    trash(args.trash_files, args.trash_dir)

    return 0


__all__ = ['main']
