import os
import subprocess

class CommandError(Exception): pass

def command(command, cwd=None, capture=False, ignore=False):
    dev_null = None
    if capture:
        out_stream = subprocess.PIPE
        err_stream = subprocess.PIPE
    else:
        dev_null = open(os.devnull, 'w+')
        # Non-captured, hidden streams are discarded.
        out_stream = dev_null
        err_stream = dev_null

    try:
        p = subprocess.Popen(command,
                             shell=True,
                             cwd=cwd,
                             stdout=out_stream,
                             stderr=err_stream)

        (stdout, stderr) = p.communicate()
    finally:
        if dev_null is not None:
            dev_null.close()

    out = {
        'cmd': command,
        'err': stderr.strip() if stdout else "",
        'out': stdout.strip() if stdout else "",
        'return_code': p.returncode,
        'cwd': cwd if cwd is not None else os.getcwd(),
        'succeeded': True if p.returncode == 0 else False,
        'failed': False if p.returncode == 0 else True
    }

    if ignore is True:
        return out
    elif out['succeeded'] is True:
        if capture is True:
            return out
        else:
            return None
    else:
        raise CommandError(out)
