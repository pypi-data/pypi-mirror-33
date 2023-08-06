import os
from pathlib import Path
import shutil

_PKGDIR = Path(__file__).parent.resolve()

CONDA_ROOT = os.environ.get('CONDA_ROOT_DIR', '~/miniconda3')
DEFAULT_SHELL = 'sh'

class MenuItem:
    def __init__(self, display, *, data=None):
        self.display = display
        self.data = data
    
    def __repr__(self):
        p = [type(self).__name__, '(', repr(self.display)]
        if self.data is not None:
            p += [', data=', repr(self.data)]
        p += [')']
        return ''.join(p)

class CondaEnv:
    def __init__(self, path):
        self.path = path
        self.display = path.name
    
    def __repr__(self):
        return 'CondaEnv(%r)' % self.path
    
    def delete(self):
        shutil.rmtree(str(self.path))

    def activate(self):
        e = os.environ
        e['PATH'] = str(self.path / 'bin') + ':' + e['PATH']
        e['CONDA_DEFAULT_ENV'] = self.path.name
        e['CONDA_PREFIX'] = str(self.path)

        shell = os.environ.get('SHELL', DEFAULT_SHELL)
        print("\nLaunching {} with conda environment: {}".format(
              shell, self.path.name))
        print("Exit the shell to leave the environment.", flush=True)

        if os.path.basename(shell) == 'bash':
            os.execvp(shell,
                      [shell, '--rcfile', str(_PKGDIR / 'conda-bashrc.sh')])

        # Generic shell
        activate_d = os.path.join(os.environ['CONDA_PREFIX'],
                                  'etc', 'conda', 'activate.d')
        if os.path.isdir(activate_d):
            print('Files in activate.d will not be run (unknown shell):')
            print(os.listdir(activate_d), flush=True)
        os.execvp(shell, [shell])

def find_conda_envs():
    env_dir = Path(CONDA_ROOT).expanduser() / 'envs'
    if not env_dir.is_dir():
        raise Exception(("Can't find conda envs at {}. "
                         "Set $CONDA_ROOT_DIR to point to your conda install.")
                        .format(env_dir))
    for f in env_dir.iterdir():
        if f.is_dir():
            yield CondaEnv(f)
    

def find_envs():
    envs = list(find_conda_envs())
    return sorted(envs, key=lambda x: x.display.lower())
