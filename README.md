# ksux

A simple way for templating kubernetes manifests.

## Requirements

This is a python package. So the only requirements are `python3` and `pip`

## Installation

- Optional: Create a virtual env.

```shell
# option 1: virualvenv
virtualvenv ksux
source ksux/bin/activate

# option 2: venv
python -m venv ksux
source ksux/bin/activate

# option 3: conda
conda create -n ksux python
conda activate ksux
```

- Install

```shell
pip install ksux
```

## How does it work?

tldr.

```shell
ksux -b <path_to_base_dir> -p <path_to_patches_dir> -o <output_dir>
```

---

Let's say that you have many manifests in some directory (`base` directory) that you wish to patch with patches (in the
`patches`) directory.

Patches could be in `yaml` or `json` format (as well as your manifests). However, they must adhere to following schema:

```yaml
name: <patch_description>
target:
  apiVersion: <apiVersion of targeted resource>
  kind: <Deployment type of targeted resource>
  name: <name of targeted resource>
ops:
  - name: <operation description>
    path: <path to the part of the manifest to be patched>
    value: <value which should be replaced or added>
    action: <add|replace|remove>
```

each patch file must be a list of patches. E.g.:

```yaml
- name: deployment_patches
  target:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  ops:
    - name: replace_image
      path: /spec/template/spec/containers/nginx/image
      value: nginx:1.23
      action: replace
- name: service_patches
  target:
    apiVersion: v1
    kind: Service
    name: nginx-service
  ops:
    - name: add_https_port
      path: /spec/ports
      value:
        name: https
        port: 443
        protocol: TCP
        targetPort: 443
      action: add
    - name: rename_http_port
      path: /spec/ports/http/name
      action: replace
      value: new_name
```

Then all you need to do, is run:

```shell
ksux -b <path_to_base_dir> -p <path_to_patches_dir> -o <output_dir>
```

This will save all patched manifests to the output dir. You can use the `--dry-run` flag

```shell
ksux -b <path_to_base_dir> -p <path_to_patches_dir> --dry-run
```

For list of all options see:

```shell
ksux --help
```

### the op path

This is a pretty cool thing. Similar to kustomize path, however you can target list item by names of child objects.
E.g. say you have a list of ports in a service:

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: nginx-service
  name: nginx-service
spec:
  ports:
    - name: new_name
      port: 80
      protocol: TCP
      targetPort: 80
    - name: https
      port: 443
      protocol: TCP
      targetPort: 443
  selector:
    app: web
  type: ClusterIP
```

To target the `https` service and change its name, you can specify the path: `/spec/ports/https/name` and then
set the value to the new name 💪.
