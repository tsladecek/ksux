import enum
import json
import logging
import os.path
from typing import List, Dict

from yaml import dump


def save_manifests(
        patched_manifests: List[Dict],
        out_dir: str,
        extension: str
) -> None:

    os.system(f'mkdir -p {out_dir}')

    for p in patched_manifests:
        output_path = os.path.join(
            out_dir,
            f'{p["apiVersion"].replace("/", "-")}_{p["kind"]}_{p["metadata"]["name"]}.{extension}'.lower()
        )

        with open(output_path, 'w') as f:
            if extension == 'json':
                json.dump(p, f)
            elif extension == 'yaml' or extension == 'yml':
                f.write(dump(p))
            else:
                logging.error('Invalid extension. Allowed values are: json, yaml and yml')
                exit(1)
