# Installation

## Pypi

`ksux` is a python package. All you need to do is run:

```shell
pip install ksux
```

!!! note
    It is recommended to use a virtual environment. Do not install the package to your base environment. You can easily set up a virtual environment with one of following commands (or any other of your favorite implementations): 
    ```shell
    # activate with "source ksux/bin/activate" 
    python -m venv ksux
    virtualenv ksux
    
    # activate with "conda activate ksux"
    conda create -n ksux ksux
    ```
    

## Docker

There is also a docker image which is great for use in CI. However, you can use it as a command line tool as well. The only difference from running `ksux` directly, is the necessity to mount volumes to the container:

```shell
docker run --rm -v /path/to/base:/base -v /path/to/patches:/patches -o /path/to/output:/output tsladecek/ksux ksux -b /base -p /patches -o /output
```