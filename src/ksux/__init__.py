import logging
import sys
from argparse import ArgumentParser

from ruamel.yaml import round_trip_dump

from .src.create_manifests import patch_manifests
from .src.save_manifests import save_manifests


def main():
    parser = ArgumentParser()

    parser.add_argument('-b', '--base_dir', help='Base directory with yaml/yml/json kubernetes templates')
    parser.add_argument('-o', '--out_dir', help='Output directory', default='out')
    parser.add_argument('-p', '--patches_dir',
                        help='Patches directory. Script will read only files with yaml/yml/json extensions')
    parser.add_argument('-e', '--out_ext', help='Extension of output files', choices=['yaml', 'json', 'yml'],
                        default='json')
    parser.add_argument('--dry-run', help='Print manifests to stdout', action="store_true")
    parser.add_argument('--version', help='Package version', action="store_true")

    args = parser.parse_args()

    if args.version:
        print('VERSION')
        exit(0)

    manifests = patch_manifests(base_dir=args.base_dir, patches_dir=args.patches_dir)

    if args.dry_run:
        print('---')
        for i, m in enumerate(manifests):
            round_trip_dump(m, sys.stdout)
            print('---')
    else:
        save_manifests(patched_manifests=manifests, out_dir=args.out_dir, extension=args.out_ext)

    if args.out_ext in ['yaml', 'yml']:
        logging.warning(
            'Make sure to check the manifests, especially if your input was in json format and you had some "add" ops '
            'in your patches. In this case it is impossible to preserve quotes correctly!')
