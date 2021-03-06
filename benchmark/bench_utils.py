import os
from pathlib import Path
import subprocess
import sys
import time
import torch

model_dir = 'models/'
install_file = 'install.py'
hubconf_file = 'hubconf.py'


def _install_deps(model_path):
    if os.path.exists(os.path.join(model_path, install_file)):
        subprocess.check_call([sys.executable, install_file], cwd=model_path)
    else:
        print('skip installing deps and preprocessing since no install.py is found in {}.'.format(model_path))


class workdir():
    def __init__(self, path):
        self.path = path
        self.cwd = os.getcwd()

    def __enter__(self):
        sys.path.insert(0, self.path)
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            os.chdir(self.cwd)
            sys.path.remove(self.path)
        except ValueError:
            pass


def list_model_paths():
    p = Path(__file__).parent.joinpath(model_dir)
    return [str(child.absolute()) for child in p.iterdir()]


def setup():
    for model_path in list_model_paths():
        _install_deps(model_path)


def list_models():
    models = []
    for model_path in list_model_paths():
        with workdir(model_path):
            hub_module = torch.hub.import_module(hubconf_file, hubconf_file)
            Model = getattr(hub_module, 'Model', None)
            if not Model:
                raise RuntimeError('Missing class Model in {}/hubconf.py'.format(model_path))
            models.append(Model)
    return zip(models, list_model_paths())
