import json
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
    parser.add_argument('-e', '--output_extension', help='Extension of output files', choices=['yaml', 'json', 'yml'],
                        default='json')
    parser.add_argument('--patched_only', help='If all manifests should be saved, even those which were not patched',
                        action='store_true')
    parser.add_argument('--dry-run', help='Print manifests to stdout', action="store_true")
    parser.add_argument('-q', '--quiet', help='Do not print debug, info and warning messages', action='store_true')
    parser.add_argument('--version', help='Package version', action="store_true")

    args = parser.parse_args()

    if args.version:
        print('VERSION')
        exit(0)

    if args.quiet:
        logging.root.setLevel(logging.ERROR)
    else:
        logging.root.setLevel(logging.INFO)

    final, all_manifests = patch_manifests(base_dir=args.base_dir, patches_dir=args.patches_dir)

    # Create final list of manifests
    if not args.patched_only:
        versions = all_manifests.keys()
        final = []

        for v in versions:
            version = all_manifests[v]
            kinds = version.keys()
            for k in kinds:
                kind = version[k]
                resource_names = kind.keys()

                for r in resource_names:
                    final.append(kind[r])

    if args.dry_run:
        if args.output_extension in ['yaml', 'yml']:
            print('---')
            for i, m in enumerate(final):
                round_trip_dump(m, sys.stdout)
                print('---')
        else:
            print(json.dumps(final))

    else:
        save_manifests(patched_manifests=final, out_dir=args.out_dir, extension=args.output_extension)

    if args.output_extension in ['yaml', 'yml']:
        logging.warning(
            'Make sure to check the manifests, especially if your input was in json format and you had some "add" ops '
            'in your patches. In this case it is impossible to preserve quotes correctly!')
