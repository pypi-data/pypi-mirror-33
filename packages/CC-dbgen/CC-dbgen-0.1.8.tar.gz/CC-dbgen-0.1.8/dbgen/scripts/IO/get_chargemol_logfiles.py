from typing     import List,Tuple
from subprocess import getstatusoutput
from json       import loads
from os         import environ
def get_chargemol_logfiles(rootpath : str
                    #      ,filejson : str
                          ) -> Tuple[List[str],List[str]]:
    """
    Searches for chargemol calculation logfiles.
    Returns unzipped (stordir,logfile) pairs

    Requirements to be flagged as a DFT job:
        - There must exist at least one .traj file in the directory
        - If there's a DDEC analysis file, we'll assume it's a Chargemol job
            (need to check if it is completed)

    """
    ############################
    # Initialize Variables
    #---------------------
    dirs,logs  = [],[]
    user       = environ['SHERLOCK_USERNAME']

    # Main Program
    #-------------
    ssh = 'ssh %s@login.sherlock.stanford.edu '%user
    cmd = """for f in $(find {0} -name total_cube_DDEC_analysis.output);
                    do
                        result=$(tail -3 $f | grep -c "Finished chargemol") ;
                if [ ! $result -eq 0 ]; then
                    echo "$f"
                    fi
                done""".format(rootpath)
    exit,output = getstatusoutput(ssh+cmd)
    assert exit==0,'Failure in get_chargemol_logfile bash execution: '+output
    for logfile in output.split('\n'):
        if logfile:
            last_slash = logfile.rfind('/')
            dir = logfile[:last_slash]
            if True: #dir not in files:
                dirs.append(dir)
                logs.append(logfile)

    return dirs,logs
