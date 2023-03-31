<p align="center">
  <img src="misc/logo.svg" width="75%">
</p>

<p align=center>
   <em>A simple way for templating kubernetes manifests.</em>
</p>

<p align=center>
   <img src='https://img.shields.io/github/actions/workflow/status/tsladecek/ksux/test.yml?branch=main&label=tests&logo=GitHub' alt=''/>
   <img src='https://img.shields.io/github/repo-size/tsladecek/ksux' alt=''/>
   <img src='https://img.shields.io/github/license/tsladecek/ksux' alt='License: MIT'/>
   <img src='https://img.shields.io/github/v/tag/tsladecek/ksux?color=yellow&label=version&logo=GitHub'/>
   <a href='https://pypi.org/project/ksux/'><img src='https://img.shields.io/pypi/v/ksux?logo=Pypi'/></a>
   <a href='https://hub.docker.com/r/tsladecek/ksux'><img src='https://img.shields.io/docker/image-size/tsladecek/ksux?logo=Docker&sort=date' /></a>
</p>

---

1. [Requirements](#requirements)
2. [Installation](#installation)
   1. [Local](#local)
   2. [Docker](#docker)
3. [How does it work?](#how-does-it-work)
   1. [The `op.path`](#the-oppath)
4. [Example](#example)

**tldr.**

```shell
ksux -b <path_to_base_dir> -p <path_to_patches_dir> -o <output_dir>
```

or using docker:

```shell
docker run --rm -v /path/to/your/configs:/configs tsladecek/ksux ksux -b /configs/base -p /configs/patches -o /configs/out
```

---

## Requirements

This is a python package. So the only requirements are `python3` and `pip`

## Installation

### Local

- Optional: Create and activate a virtual env.

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

### Docker

use the [docker image](https://hub.docker.com/r/tsladecek/ksux)

To run the command inside a docker container, you need to make sure that all volumes are mapped to the container. Let's
say that you have a following file structure:

```shell
|- /home/project
|  |- base
|  |- patches
|  |- out
```

To generate patched manifests in the `/home/project/out` folder, run following command:

```shell
docker run --rm -v /home/project:/configs tsladecek/ksux ksux -b /configs/base -p /configs/patches -o /configs/out
```

the important part is the `-v` flag, which will mount your local folder as volume to the container.

## How does it work?

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

each patch file can be a list of patches. You can use the classic yaml format, e.g.:

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

or use the `---` separator:

```yaml
---
name: deployment_patches
target:
  apiVersion: apps/v1
  kind: Deployment
  name: web
ops:
- name: replace_image
  path: /spec/template/spec/containers/nginx/image
  value: nginx:1.23
  action: replace
---
name: service_patches
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

This will save all patched manifests to the output dir. You can use the `--dry-run` flag to print the patched
manifests to stdout:

```shell
ksux -b <path_to_base_dir> -p <path_to_patches_dir> --dry-run
```

For list of all options see:

```shell
ksux --help
```

### the `op.path`

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

## Example

In the `./examples` folder there are 3 sub-folders:
    - `/examples/base` with deployment, service and a configmap manifests. These are the base manifests which we wish
    to patch
    - `/examples/patches` contain the patches (notice that both base kubernetes manifests and patches can be either in
    `json` or `yml`/`yaml` format)
    - `/examples/out` is the output directory where the patched resources will be output

First, we will `dry-run` the patching:

```shell
ksux -b examples/base -p examples/patches --dry-run
```

You should see the patched manifests printed out to the console. Now we can run it and save the patched manifests
to the `output` folder:

```shell
ksux -b examples/base -p examples/patches -o examples/out
```

By default, the manifests will be saved in `yaml` format with `.yaml` extension. If you wish to use the `.yml` extension
or save the manifests in `json` format, simply provide the `-e` flag with corresponding extension. E.g.:

```shell
ksux -b examples/base -p examples/patches -o examples/out -e json
```
