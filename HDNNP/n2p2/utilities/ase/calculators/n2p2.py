import sys
import numpy as np
from ase.calculators.calculator import all_changes
from ase.calculators.calculator import FileIOCalculator
from ase.calculators.genericfileio import GenericFileIOCalculator
import os
import shutil
from ase.io.n2p2 import read_n2p2, write_n2p2





class N2P2Template:
    '''example:
        N2P2Calculator(
            directory = 'tmp',
            files = [
                'input.nn',
                'scaling.data',
                'weights.008.data',
                'weights.001.data'],
            )
    '''

    command = 'nnp-predict 0'
    'Command used to start calculation'

    name = 'n2p2'

    def __init__(self, restart=None, ignore_bad_restart_file=False,
                 label=None, atoms=None, command=None, files=[], **kwargs):
        """File-IO calculator.

        command: str
            Command used to start calculation.
        """

        self.files = files

        #FileIOCalculator.__init__(self, restart, ignore_bad_restart_file, label,
        #                    atoms, **kwargs)
        GenericFileIOCalculator.__init__(self,
            #restart, ignore_bad_restart_file, label,
            #                atoms,
                            **kwargs)

        if command is not None:
            self.command = command
        else:
            name = 'ASE_' + self.name.upper() + '_COMMAND'
            self.command = os.environ.get(name, self.command)

        self.implemented_properties = {
            'energy' : self.calculate,
            'forces' : self.calculate}
        self.results = {}

        ## preparing
        if self.directory != os.curdir and not os.path.isdir(self.directory):
            os.makedirs(self.directory)
        self.write_files()

    def write_input(self, atoms, properties=None, system_changes=None):
        """Write input file(s).

        Call this method first in subclasses so that directories are
        created automatically."""

        if self.directory != os.curdir and not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        write_n2p2(
            os.path.join(self.directory, 'input.data'),
            atoms,
            with_energy_and_forces = False)

    def write_files(self): #should this be initialize?
        for filename in self.files:
            src = filename
            basename = os.path.basename(filename)
            dest = os.path.join(self.directory, basename)
            shutil.copyfile(src, dest)

    def read_results(self):
        res_atoms = read_n2p2(
                    filename= os.path.join(self.directory,'output.data'),
                    index=-1,
                    with_energy_and_forces = True)

        self.results = res_atoms.calc.results




class N2P2GenericFileIOCalculator(GenericFileIOCalculator):
    '''example:
        N2P2Calculator(
            directory = 'tmp',
            files = [
                'input.nn',
                'scaling.data',
                'weights.008.data',
                'weights.001.data'],
            )
    '''

    command = 'nnp-predict 0'
    'Command used to start calculation'

    name = 'n2p2'

    def __init__(self, restart=None, ignore_bad_restart_file=False,
                 label=None, atoms=None, command=None, files=[], **kwargs):
        """File-IO calculator.

        command: str
            Command used to start calculation.
        """

        self.files = files

        GenericFileIOCalculator.__init__(self,
            #restart, ignore_bad_restart_file, label,
            #                atoms,
                            **kwargs)

        if command is not None:
            self.command = command
        else:
            name = 'ASE_' + self.name.upper() + '_COMMAND'
            self.command = os.environ.get(name, self.command)

        self.implemented_properties = {
            'energy' : self.calculate,
            'forces' : self.calculate}
        self.results = {}

        ## preparing
        if self.directory != os.curdir and not os.path.isdir(self.directory):
            os.makedirs(self.directory)
        self.write_files()

    def write_input(self, atoms, properties=None, system_changes=None):
        """Write input file(s).

        Call this method first in subclasses so that directories are
        created automatically."""

        if self.directory != os.curdir and not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        write_n2p2(
            os.path.join(self.directory, 'input.data'),
            atoms,
            with_energy_and_forces = False)

    def write_files(self): #should this be initialize?
        for filename in self.files:
            src = filename
            basename = os.path.basename(filename)
            dest = os.path.join(self.directory, basename)
            shutil.copyfile(src, dest)

    def read_results(self):

        res_atoms = read_n2p2(
                    filename= os.path.join(self.directory,'output.data'),
                    index=-1,
                    with_energy_and_forces = True)

        self.results = res_atoms.calc.results




from contextlib import contextmanager
from pathlib import Path
import subprocess

class N2P2Calculator(FileIOCalculator):
    '''example:
        N2P2Calculator(
            directory = 'tmp',
            files = [
                'input.nn',
                'scaling.data',
                'weights.008.data',
                'weights.001.data'],
            )
    '''

    command = 'nnp-predict 0'
    'Command used to start calculation'

    name = 'n2p2'

    def __init__(self, restart=None,
                label=None, atoms=None, command=None,
                files=[], txt='n2p2.out', **kwargs):
        """File-IO calculator.

        command: str
            Command used to start calculation.
        """

        self.files = files
        FileIOCalculator.__init__(self, restart, **kwargs)

        if command is not None:
            self.command = command
        else:
            name = 'ASE_' + self.name.upper() + '_COMMAND'
            self.command = os.environ.get(name, self.command)

        self.implemented_properties = {
            'energy' : self.calculate,
            'forces' : self.calculate}
        self.results = {}

        self.txt=txt

        ## preparing
        if self.directory != os.curdir and not os.path.isdir(self.directory):
            os.makedirs(self.directory)
        self.write_files()

    def write_input(self, atoms, properties=None, system_changes=None):
        """Write input file(s).

        Call this method first in subclasses so that directories are
        created automatically."""

        if self.directory != os.curdir and not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        write_n2p2(
            os.path.join(self.directory, 'input.data'),
            atoms,
            with_energy_and_forces = False)

    def write_files(self): #should this be initialize?
        for filename in self.files:
            src = filename
            basename = os.path.basename(filename)
            dest = os.path.join(self.directory, basename)
            shutil.copyfile(src, dest)



    @contextmanager
    def _txt_outstream(self):
        ## copied from the vasp calculator and lightly changed
        """Custom function for opening a text output stream. Uses self.txt
        to determine the output stream, and accepts a string or an open
        writable object.
        If a string is used, a new stream is opened, and automatically closes
        the new stream again when exiting.

        Examples:
        # Pass a string
        calc.txt = 'vasp.out'
        with calc.txt_outstream() as out:
            calc.run(out=out)   # Redirects the stdout to 'vasp.out'

        # Use an existing stream
        mystream = open('vasp.out', 'w')
        calc.txt = mystream
        with calc.txt_outstream() as out:
            calc.run(out=out)
        mystream.close()

        # Print to stdout
        calc.txt = '-'
        with calc.txt_outstream() as out:
            calc.run(out=out)   # output is written to stdout
        """

        txt = self.txt
        open_and_close = False  # Do we open the file?

        if txt is None:
            # Suppress stdout
            out = subprocess.DEVNULL
        else:
            if isinstance(txt, str):
                if txt == '-':
                    # subprocess.call redirects this to stdout
                    out = None
                else:
                    # Open the file in the work directory
                    txt = Path(self.directory) / txt
                    # We wait with opening the file, until we are inside the
                    # try/finally
                    open_and_close = True
            elif hasattr(txt, 'write'):
                out = txt
            else:
                raise RuntimeError('txt should either be a string'
                                   'or an I/O stream, got {}'.format(txt))

        try:
            if open_and_close:
                out = open(txt, 'w')
            yield out
        finally:
            if open_and_close:
                out.close()

    def execute(self):
        # lightly modified from the original fileIO form to dump the stderr and
        # stdout to a log file since there can be so many extrapolation warnings
        if self.command is None:
            raise CalculatorSetupError(
                'Please set ${} environment variable '
                .format('ASE_' + self.name.upper() + '_COMMAND') +
                'or supply the command keyword')
        command = self.command
        if 'PREFIX' in command:
            command = command.replace('PREFIX', self.prefix)

        try:
            with self._txt_outstream() as out:
                proc = subprocess.Popen(command,
                                        shell=True,
                                        stdout=out,
                                        stderr=out,
                                        cwd=self.directory)
        except OSError as err:
            # Actually this may never happen with shell=True, since
            # probably the shell launches successfully.  But we soon want
            # to allow calling the subprocess directly, and then this
            # distinction (failed to launch vs failed to run) is useful.
            msg = 'Failed to execute "{}"'.format(command)
            raise EnvironmentError(msg) from err

        errorcode = proc.wait()

        if errorcode:
            path = os.path.abspath(self.directory)
            msg = ('Calculator "{}" failed with command "{}" failed in '
                   '{} with error code {}'.format(self.name, command,
                                                  path, errorcode))
            raise CalculationFailed(msg)


    def read_results(self):
        res_atoms = read_n2p2(
                    filename= os.path.join(self.directory,'output.data'),
                    index=-1,
                    with_energy_and_forces = True)

        self.results = res_atoms.calc.results
