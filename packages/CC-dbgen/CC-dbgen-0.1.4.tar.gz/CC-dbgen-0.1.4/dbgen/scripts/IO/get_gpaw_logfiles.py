from typing     import List,Tuple
from subprocess import getstatusoutput
from json       import loads
from os         import environ
################################################################################
def get_gpaw_logfiles(rootpath : str
                    ) -> Tuple[List[str],List[str]]:
    """
    Searches for DFT calculation folders. Returns unzipped (stordir,logfile) triples

        - If there exists a file in the directory with a particular signature,
            we identify it as a GPAW job.
    """
    ######################
    # Initialize Variables
    #---------------------
    dirs,logs  = [],[]
    badext     = ["sh","traj","json","gpw","py","err"]
    badextstr  = " ".join(['-not -name "*.%s"'%x for x in badext])
    user       = environ['SHERLOCK_USERNAME']

    ##############
    # Main program
    #-------------
    ssh     = 'ssh %s@login.sherlock.stanford.edu '%user

    cmd = """for f in $(find {0}  -type f {1})
            do
                if $(head -2 $f | tail -1 | grep -q " ___ ___ ___ _ _ _ "); then
                    if $(grep -q "Free energy" $f); then
                        echo $f
                    fi
                fi
        done""".format(rootpath,badextstr)
    exit,gpawcheck = getstatusoutput(cmd)
    assert exit==0,'Failure in get_gpaw_logfile bash execution: '+gpawcheck
    for logfile in gpawcheck.split('\n'):
        if logfile:
            last_slash = logfile.rfind('/')
            dir = logfile[:last_slash]
            if True: #dir not in files:
                dirs.append(dir)
                logs.append(logfile)

    return dirs,logs
