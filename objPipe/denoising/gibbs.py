from time import time
from pathlib import Path

class NoiseRemovalPipe(object):
    def run_gibbs_unring(self, dwi: Path, dwi_unring: Path,
                         force: bool = False):
        if force or not dwi_unring.is_file():
            print(f'Running gibbs ringing on {dwi}')
            dwi_unring.parent.mkdir(parents=True, exist_ok=True)
            # command = f'{self.unring} {dwi} {dwi_unring}'
            command = f'cp {dwi} {dwi_unring}'

            self.run(command)
