from argparse import ArgumentParser

from src.ksux.src.create_manifests import create_manifests

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('-b', '--base_dir', help='Base directory with yaml/yml/json kubernetes templates')
    parser.add_argument('-o', '--out_dir',
                        help='Output directory.')
    parser.add_argument('-p', '--patches_dir',
                        help='Patches directory. Script will read only files with yaml/yml/json extensions')

    args = parser.parse_args()

    manifests = create_manifests(base_dir=args.base_dir, patches_dir=args.patches_dir)

    # validate_manifests(manifests)

    # save_manifests(manifests=manifests, outdir=args.outdir)
