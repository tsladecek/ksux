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
    parser.add_argument('-x', '--exclude', help='Exclude one or more manifests. To target the manifest, argument '
                                                'expects format: {apiVersion}_{kind}_{name}. E.g. if you wished to '
                                                'exclude deployment with name "backend", the option would look like: '
                                                'ksux -b ... -p ... -o ... -x apps/v1_Deployment_backend',
                        action='append')
    parser.add_argument('-xf', '--exclude-file', help='File with a list of resources to be excluded. Resources'
                                                      'must follow the format: {apiVersion}_{kind}_{name}')
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

    exclude = [] if not args.exclude else args.exclude

    if args.exclude_file:
        try:
            with open(args.exclude_file) as f:
                for line in f.readlines():
                    res = line.strip()

                    # ignore comments (lines starting with "#") and empty lines
                    if res and not res.startswith('#'):
                        exclude.append(res)
        except FileNotFoundError:
            logging.error(f'File {args.exclude_file} not found')

    # validate exclude
    for e in exclude:
        try:
            apiVersion, kind, name = e.split('_')
        except ValueError:
            logging.error('Exclude items have to be in format: {apiVersion}_{kind}_{name}')
            exit(1)

    final, all_manifests = patch_manifests(base_dir=args.base_dir, patches_dir=args.patches_dir, exclude=exclude)

    if args.dry_run:
        logging.info('Showing patched manifests.')
        if args.output_extension in ['yaml', 'yml']:
            print('---')
            for i, m in enumerate(final):
                round_trip_dump(m, sys.stdout)
                print('---')
        else:
            print(json.dumps(final))
    else:
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

        save_manifests(patched_manifests=final, out_dir=args.out_dir, extension=args.output_extension)

    if args.output_extension in ['yaml', 'yml']:
        logging.warning(
            'Make sure to check the manifests, especially if your input was in json format and you had some "add" ops '
            'in your patches. In this case it is impossible to preserve quotes correctly!')
