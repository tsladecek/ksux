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
   <a href='https://tsladecek.github.io/ksux/'><img src='https://img.shields.io/badge/Documentation-link-green' /></a>
</p>

---

- [Requirements](#requirements)
- [Installation](#installation)
  - [Local](#local)
  - [Docker](#docker)
- [How does it work?](#how-does-it-work)
  - [the `op.path`](#the-oppath)
- [Example](#example)

#### tldr

***`ksux` reads `yaml` / `json` manifests in a `base/` directory and applies patches to them specified in the `patches/` directory. The output are patched manfests in the `output/` directory***

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

To run the command inside a docker container, you need to make sure that all volumes are mapped to the container. Let's say that you have a following file structure:

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

the important part is the `-v` flag, which will mount your local folder as a volume to the container.

## How does it work?

Let's say that you have many manifests in some directory (`base` directory) that you wish to patch with patches (in the `patches` directory).

Patches could be in `yaml` or `json` format (as well as your manifests). However the patches **must** adhere to following schema:

```yaml
name: <patch description>
target:
  apiVersion: <apiVersion of targeted resource>
  kind: <kind of targeted resource>
  name: <name of targeted resource>
ops:
  - name: <operation description>
    path: <path to the part of the manifest to be patched>
    value: <value which should be replaced or added>
    action: <add|replace|remove>
    enforce_integer: <Optional - bool. whether exported value must be an integer in output json. Defaults to "false">
    list_key: <Optional - key by which an element in list should be targeted. Defaults to "name">
```

each patch file can be a list of patches. You can use the classic yaml format, e.g.:

```yaml
- name: deployment patches
  target:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  ops:
    - name: replace_image
      path: /spec/template/spec/containers/nginx/image
      value: nginx:1.23
      action: replace
- name: service patches
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
name: deployment patches
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
name: service patches
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

**note**: By default, ksux will output patched manifests in `json` format. If you wish to output them in `yaml`, provide the `-e yaml` flag to the command above

This will save all patched manifests to the output dir. You can use the `--dry-run` flag to print the patched manifests to stdout:

```shell
ksux -b <path_to_base_dir> -p <path_to_patches_dir> --dry-run
```

For a list of all options see:

```shell
ksux --help
```

### the `op.path`

This is the "bread and butter" of this package. Similar to kustomize path, however you **can** target list item by names of child objects. E.g. say you have a list of ports in a service:

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

To target the `https` service and change its name, you can specify the path: `/spec/ports/https/name` and then set the value to the new name:

```yaml
name: service patches
target:
  apiVersion: v1
  kind: Service
  name: nginx-service
ops:
- name: rename_https_port
  path: /spec/ports/https/name
  action: replace
  value: new_name
```

---

You can extend this even further. If you provide the `list_key` prop to a patch, you can target any list item with any key you wish to use. For example, lets say you have an ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: "domain.com"
      http:
        paths:
        - path: /api
          pathType: Prefix
          backend:
            service:
              name: backend
              port:
                number: 80
```

and you wish to use a different host in each of your environments. E.g. in `dev` environment, you would like the host to be `dev.domain.com`, in `staging` environment `staging.domain.com`, etc.

You can easily write a patch for each such environment:

```yaml
name: ingress dev patches
target:
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  name: ingress
ops:
  - name: replace host
    path: /spec/rules/domain.com/host
    action: replace
    value: "dev.domain.com"
    list_key: "host"
```

Ez 🙃

## Example

In the `./examples` folder there are 3 sub-folders:
    - `/examples/base` with deployment, service and a configmap manifests. These are the base manifests which we wish to patch
    - `/examples/patches` contain the patches (notice that both base kubernetes manifests and patches can be either in `json` or `yml`/`yaml` format)
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

By default, the manifests will be saved in `json` format with `.json` extension. If you wish to  save the manifests in `yaml` format, simply provide the `-e` flag with corresponding extension. E.g.:

```shell
ksux -b examples/base -p examples/patches -o examples/out -e yaml
```
