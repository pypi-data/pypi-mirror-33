from typing     import List,Tuple
from os         import environ
from os.path    import join,exists
from subprocess import getstatusoutput,Popen,PIPE
from json       import loads
################################################################################
def get_dft_logfiles(rootpath : str
                    ) -> Tuple[List[str],List[str],List[str]]:
    """
    Searches for DFT calculation folders. Returns unzipped (stordir,logfile,code) triples

    Requirements to be flagged as a DFT job:
    """
    ############################
    # Initialize Variables
    #---------------------
    out        = []
    user       = environ['SHERLOCK_USERNAME']
    # Main Program
    #-------------
    ssh    = 'ssh %s@login.sherlock.stanford.edu '%user
    cmd    = ssh+"find {} -name runtime.json ".format(rootpath)
    output = getstatusoutput(cmd)[1]
    for logfile in output.split('\n'):
        print('logfile = '+logfile)
        if logfile:
            last_slash = logfile.rfind('/')
            root       = logfile[:last_slash]
            files      = getstatusoutput(ssh+"ls %s"%root)[1].split()
            if 'log' in files:
                logpth   = join(root,'log')
                log      = getstatusoutput(ssh+'cat %s'%logpth)[1]
                is_gpaw  = ' ___ ___ ___ _ _ _ ' in log[:500]
                code     = 'gpaw' if is_gpaw else 'quantumespresso'
                out.append((root,logpth,code))
            elif 'OUTCAR' in files:
                out.append((root,join(root,'OUTCAR'),'vasp'))
            else:
                errstr = 'Malformed CataLog directory? No log nor OUTCAR found \n'
                raise ValueError(errstr+root)

    dirs,logs,codes = zip(*out)
    return (list(dirs),list(logs),list(codes))

if __name__ == '__main__':
    import sys
    print(get_dft_logfiles(sys.argv[1]))
