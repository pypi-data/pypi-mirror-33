from typing     import List,Tuple
from os         import environ,system
from os.path    import join,exists
from subprocess import getstatusoutput,Popen,PIPE
from json       import loads

from string     import ascii_uppercase,digits
from random     import choices
################################################################################
def get_catalog_logfiles(rootpath : str
                    ) -> Tuple[List[str],List[str],List[str],List[str],List[str],List[str],List[str],List[str],List[str]]:
    """
    Searches for DFT calculation folders. Returns unzipped (stordir,logfile,code) triples

    to get anytraj: \$(cat \$(ls \$f/*.traj | head -1))
    """
    ######################
    # Initialize Variables
    #---------------------
    user       = environ['SHERLOCK_USERNAME']
    login      = '%s@login.sherlock.stanford.edu'%user
    ssh        = 'ssh %s '%login
    delim1     = '***???***'
    delim2     = '~~~***~~~'
    rand       = ''.join(choices(ascii_uppercase+digits, k=16))

    # Main Program
    #-------------

    cmd    = r"""for f in \$(find {0} -name runtime.json -printf '%h\n')
                    do
                        if [ -f \$f/log ]; then
                            if \$(head -2 \$f/log | tail -1 | grep -q \" ___ ___ ___ _ _ _ \"); then
                                echo \"\$f{1}\$f/log{1}gpaw{1}\$(cat \$f/log){1} {1} {1} {1} \"
                            else
                                echo \"\$f{1}\$f/log{1}quantumespresso{1}\$(cat \$f/log) {1} \$(cat \$f/pw.inp) {1} {1} {1} \"
                            fi
                		else
                            if [ -f \$f/OUTCAR ]; then
                                echo \"\$f{1}\$f/OUTCAR{1}vasp{1}\$(cat \$f/OUTCAR){1} {1}\$(cat \$f/POTCAR){1}\$(cat \$f/POSCAR){1}\$(cat \$f/KPOINTS)\"
                            else
                                echo \"BAD DIRECTORY: \$f\"
                                exit 1
                            fi
                		fi
                        echo \" {1} \$(cat \$f/params.json) {2} \"
                   done""".format(rootpath,delim2,delim1)
    cmd1 = 'echo "%s" | %s "cat > %s; chmod 755 %s"'%(cmd,ssh,rand,rand)
    cmd3 = ssh + ' sh ' + rand
    cmd4 = ssh + ' rm ' + rand
    system(cmd1)
    code,output = getstatusoutput(cmd3)

    assert code == 0, output
    content = [[o.strip() for o in oo.split(delim2)]
                        for oo in output.split(delim1) if oo not in ['',' ']]

    try:
        dirs,logfiles,codes,logs,pws,pots,pos,kpts,params = zip(*content)
    except:
        import pdb;pdb.set_trace()
    system(cmd4)

    return (list(dirs),list(logfiles),list(codes),list(logs),list(pws)
           ,list(pots),list(pos),list(kpts),list(params))

if __name__ == '__main__':
    import sys
    print(get_catalog_logfiles(sys.argv[1]))
