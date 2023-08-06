from typing import List,Tuple
from os import listdir,environ,walk
from fnmatch import fnmatch
from os.path import join,exists
from glob import glob
from subprocess import check_output,getstatusoutput

def get_qe_logfiles(rootpath:str) -> Tuple[List[str],List[str],List[str]]:
    """
    Searches for DFT calculation folders. Returns unzipped (stordir,logfile,code) triples

    Requirements to be flagged as a DFT job:
        - There must exist at least one .traj file in the directory
        - If there's also a 'runtime.json' file, we'll assume it's a CataLog job
        - If there's a DDEC analysis file, we'll assume it's a Chargemol job
        - If there's a subdirectory with one 'pw.inp' and 'log' file, it's a QE job
        - If there exists a file in the directory with a particular signature,
            we identify it as a GPAW job.
    """
    ############################
    # Initialize Variables
    #---------------------
    output = []
    user   = environ['SHERLOCK_USERNAME']

    # Main Program
    #-------------

# dirname dirname dirname dirname
    cmd = r"find {0} -name pw.inp -printf '%h\n'".format(rootpath)
    for calcdir in check_output(cmd).split():
        slash = calcdir.rfind('/')
        stordir = calcdir[:slash]
        output.append((stordir,calcdir,'quantumespresso'))

    if output:
        return tuple(map(list,zip(*output))) # type: ignore
    else:
        print('warning, no log files found in %s'%rootpath)
        return [],[],[]
