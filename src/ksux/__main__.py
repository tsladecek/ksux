from argparse import ArgumentParser

from src.ksux.src.create_manifests import create_manifests

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('-b', '--base', help='Base directory with yaml/yml/json kubernetes templates')
    parser.add_argument('-o', '--outdir',
                        help='Output directory. Output files will be named same with preserved structure')
    parser.add_argument('-p', '--patches',
                        help='Patches directory. Script will read only files with yaml/yml/json extensions')

    args = parser.parse_args()

    manifests = create_manifests(base=args.base, patches=args.patches)

    # validate_manifests(manifests)

    # save_manifests(manifests=manifests, outdir=args.outdir)
