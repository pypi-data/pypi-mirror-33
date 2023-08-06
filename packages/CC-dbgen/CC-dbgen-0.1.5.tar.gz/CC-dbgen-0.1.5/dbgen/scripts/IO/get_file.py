from os         import environ,system,remove,listdir
from subprocess import getstatusoutput

def get_file(pth:str)->str:
    """
    Reads contents of file
    """
    user = environ['SHERLOCK_USERNAME']
    ssh  = 'ssh %s@login.sherlock.stanford.edu '%user

    if isinstance(pth,str):
        status,content = getstatusoutput(ssh+'cat %s'%pth)
        if status == 0:
            return content
        else:
            print('could not find '+pth)
            return ''
    elif isinstance(pth,list):
        delim = "&&&&&"
        cmd = (' echo "%s"; '%delim).join(['cat %s;'%x for x in pth])
        #print('command = '+cmd)
        _,content = getstatusoutput(ssh+cmd)
        #print('content = '+content)
        files = content.split(delim)
        return ['' if 'No such file' in f else f for f in files]
