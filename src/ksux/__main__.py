from argparse import ArgumentParser

import yaml

from src.ksux.src.create_manifests import patch_manifests
from src.ksux.src.save_manifests import save_manifests

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('-b', '--base_dir', help='Base directory with yaml/yml/json kubernetes templates')
    parser.add_argument('-o', '--out_dir', help='Output directory', default='out')
    parser.add_argument('-p', '--patches_dir',
                        help='Patches directory. Script will read only files with yaml/yml/json extensions')
    parser.add_argument('-e', '--out_ext', help='Extension of output files', choices=['yaml', 'json', 'yml'],
                        default='yaml')
    parser.add_argument('--dry-run', help='Print manifests to stdout', action="store_true")

    args = parser.parse_args()

    manifests = patch_manifests(base_dir=args.base_dir, patches_dir=args.patches_dir)

    if args.dry_run:
        yaml_manifests = []

        for m in manifests:
            yaml_manifests.append(yaml.dump(m))

        yaml_manifests = '---\n'.join(yaml_manifests)
        print(yaml_manifests)
    else:
        save_manifests(patched_manifests=manifests, out_dir=args.out_dir, extension=args.out_ext)
