# External modules
from ase        import Atoms    # type: ignore
from ase.io     import read     # type: ignore
from os.path    import join,exists,getsize
from os         import environ,mkdir,listdir
from subprocess import call
from shutil     import rmtree
from string     import ascii_uppercase,digits
from random     import choices

# Internal modules
from dbgen.scripts.Pure.Atoms.traj_to_json import traj_to_json
################################################################################
def anytraj(root : str) -> str:
    """
    ASE IO read function - takes any traj it can find
    """
    user = environ['SHERLOCK_USERNAME']
    rand = ''.join(choices(ascii_uppercase+digits, k=16))
    mkdir(rand)

    call(['scp','-C','-r','-q','%s@login.sherlock.stanford.edu:%s/*.traj'%(user,root)
         ,rand])
    trajs = [join(rand,t) for t in listdir(rand) if getsize(join(rand,t)) > 100]

    if len(trajs) == 0:
        raise ValueError('Get Traj could not find any traj in '+root)
    else:
        atoms = read(trajs[0])
        rmtree(rand)
        return traj_to_json(atoms)

if __name__=='__main__':
    import sys
    print(anytraj(sys.argv[1]))
