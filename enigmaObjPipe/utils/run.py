import os
import re
from subprocess import check_call
from multiprocessing import Pool
from typing import Callable, Tuple


def create_command(command: str, bsub: bool = False,
                   que: str = 'normal', core_num: int = 4,
                   err: str = './log.err', out: str = './log.out', **kwargs):
    '''Rearrange the command to run to shell

    Key arguments:
        command: shell command to run
        bsub: boolean to mark bsub use
        que: bsub queue to submit the job to
        core_num: threads to request to bsub
        err: bsub log error output
        out: bsub log output

    kwargs:
        name: name to provide to the bsub
        dependency: bsub id to set it was the dependency

    Returns:
        command: shell command to be executed
    '''
    if bsub and 'bsub_command' in kwargs: # bsub command is given
        command = kwargs.get('bsub_command')
    elif bsub: # command with bsub options have given
        bsub_command = f'bsub -q {que} -n {core_num} -e {err} -o {out}'

        if 'name' in kwargs:
            name = kwargs.get('name')
            bsub_command += f' -J {name}'

        if 'dependency' in kwargs:
            dependency = kwargs.get('dependency')
            bsub_command += f' -W "ended\\({dependency}\\)"'

        command = f'{bsub_command} {command}'

    command = re.sub(r'\s+', ' ', command)
    return command


def RAISE(ERR):
    raise ERR


class RunCommand(object):
    def run(self, command, bsub=False, que='normal', core_num=4, **kwargs):
        """Run either with basic terminal or bsub

        Key arguments:
            bsub: True or False

        Kwargs:
            bsub_command: bsub command to run
            name: bsub name
            que: bsub que type
            core_num: bsub n cpu

        TODO:
            add bsub -w options
        """
        command = create_command(command, bsub, que, core_num, **kwargs)
        check_call(command, shell=True)

    def run_in_parallel(self, pool: Pool, function: Callable) -> None:
        '''Run function in parallel on the subject'''

        if type(function) == str:
            pool.apply_async(func=getattr(self, function),
                             args=(),
                             error_callback=RAISE)
        else:
            pool.apply_async(func=function,
                             args=(self,),
                             error_callback=RAISE)

    def run_test(self, command, bsub=False, que='normal', core_num=4, **kwargs):
        """Test run either with basic terminal or bsub

        Key arguments:
            bsub: True or False

        Kwargs:
            bsub_command: bsub command to run
            name: bsub name
            que: bsub que type
            core_num: bsub n cpu

        TODO:
            add bsub -w options
        """
        command = create_command(command, bsub, que, core_num, **kwargs)
        return command

