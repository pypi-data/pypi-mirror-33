import os
import tempfile
import subprocess
import shutil


def MopacSolver(cmd='mopac', method='PM7'):
    """
    Wraps `MOPAC <http://openmopac.net>`_, which needs to be installed on the system.

    :param str cmd: MOPAC executable
    :param str method: model to calculate energy
    """
    kcal, ev, angstrom = 627.503, 27.2107, 0.52917721092
    tmpdir = tempfile.mkdtemp()
    try:
        atoms = yield
        while True:
            mopac_input = '{} 1SCF GRADIENTS\n\n\n'.format(method) + '\n'.join(
                '{} {} 1 {} 1 {} 1'.format(el, *coord) for el, coord in atoms
            )
            input_file = os.path.join(tmpdir, 'job.mop')
            with open(input_file, 'w') as f:
                f.write(mopac_input)
            subprocess.check_output([cmd, input_file])
            with open(os.path.join(tmpdir, 'job.out')) as f:
                energy = float(next(l for l in f if 'TOTAL ENERGY' in l).split()[3])/ev
                next(l for l in f if 'FINAL  POINT  AND  DERIVATIVES' in l)
                next(f)
                next(f)
                gradients = [
                    [float(next(f).split()[6])/kcal*angstrom for _ in range(3)]
                    for _ in range(len(atoms))
                ]

            atoms = yield energy, gradients
    finally:
        shutil.rmtree(tmpdir)
