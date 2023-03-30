# ksux

Easy and fast customization of kubernetes templates.

## Why?
Patching kubernetes manifests does not have to be tedious. `kustomize` and `helm` make this unnecessarily difficult, although they are great at what they were meant to do.

`ksux` aims to fill a hole where a small project requires patching existing manifests. Let's say that you have the following file structure:

```text
|- base
|  |- deployment.yaml
|  |- service.yaml
|  |- configmap.yaml
|- dev
|- staging
|- prod
```

where your `base` folder contains kubernetes manifest templates, and the `dev`, `staging` and `prod` folders should contain patched templates from the base dir. How to do it?

We propose a simple solution. Just create a new directory `patches` (or whatever name you like) and create (a) patch file(s).

```text
|- base
|  |- deployment.yaml
|  |- service.yaml
|  |- configmap.yaml
|- dev
|- staging
|- prod
|- patches
|- |- deployment_patch.yaml
```

The content of the patch file should be composed of a list of patches (not necessary if the file will contain only one patch) where each patch must adhere to following structure:

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

e.g. say you wish to change the image for a deployment called web to `nginx:1.23`:

!!! tip
    Pay close attention to the `path` attribute of the first operation. We need to target a container from a list of containers. In `kustomize` you can do this only by specifying index of an element in a list which is baaaad (`/spec/template/spec/containers/0/image` for obvious reasons). We allow you to target a resource in a list by its name, which is more robust towards item order changes in a list.

```yaml
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
```

then just call following command to generate patched manifest to `dev` folder:

```shell
ksux -b base/ -p patches/ -o dev/
```

!!! info
    By default, ksux will output files in `json` format. `yaml` is supported as well, just add the `-e yaml` flag to the `ksux` command.
    However, we recommend using templates in json format. `YAML` is great for readability, but error-prone. We tried to make sure that the yaml stays as intact as possible, however `json` should be the safe choice.