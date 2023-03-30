# Arguments

You can see all options by running:

```shell
ksux --help
```

## `-b` / `--base_dir`
Directory with all your base manifests which are to be patched. Only manifests with `.yaml`, `.yml` or `.json` extension will be considered

## `-p` / `--patches_dir`
Patches which will be applied to your base manifests. Only patches with `.yaml`, `.yml` or `.json` extension will be considered

## `-o` / `--output_dir`
Path to a directory where the results should be saved. The directory will be created if it does not exist

## `-e` / `--output_extension`
Extension of patched manifests. Default is `json`. Other allowed options are `yaml` and `yml`. `JSON` format is recommended, as it is more robust than `yaml`

## `--patched_only`
Save only patched manifest. By default, all manifests in the `base` directory whether patched or not will be saved to the `output` directory

## `-x` / `--exclude`
Exclude one or more resources. The format for excluding a resource must be: `{apiVersion}_{kind}_{name}`. E.g. if you want to exclude service with name `my-svc`:

```shell
ksux -b /path/to/base -p /path/to/patches -o /patch/to/output -x v1_Service_my-svc
```

## `--dry-run`
print patched manifests to stdout. For readability, it is recommended to supply the `-e yaml` flag, otherwise the output will be in json format 

## `-q` / `--quiet`
set logging level to `ERROR`

## `--version`
Print package version