import os

import multiprocessing
import multiprocessing.pool

from multiprocessing import cpu_count

############### Dependency Checking ###############

def check_three_way_dependency(target, source, dependency):
    if not os.path.exists(target):
        # if .json doesn't exist, rebuild
        return True
    else:
        dep_mtime = os.stat(dependency).st_mtime
        if os.stat(source).st_mtime > dep_mtime:
            # if <file>.txt is older than <file>.fjson,
            return True
        elif dep_mtime > os.stat(target).st_mtime:
            #if fjson is older than json
            return True
        else:
            return False

def check_dependency(target, dependency):
    if dependency is None:
        return True

    if isinstance(target, list):
        return check_multi_dependency(target, dependency)

    if not os.path.exists(target):
        return True

    def needs_rebuild(targ_t, dep_f):
        if targ_t < os.stat(dep_f).st_mtime:
            return True
        else:
            return False

    target_time = os.stat(target).st_mtime
    if isinstance(dependency, list):
        ret = False
        for dep in dependency:
            if needs_rebuild(target_time, dep):
                ret = True
                break
        return ret
    else:
        return needs_rebuild(target_time, dependency)

def check_multi_dependency(target, dependency):
    for t in target:
        if check_dependency(t, dependency) is True:
            return True

    return False


##### Permit Nested Pool #####

class NonDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

class NestedPool(multiprocessing.pool.Pool):
    Process = NonDaemonProcess

############### Task Running Framework ###############

def runner(jobs, pool=None, parallel=True, force=False, retval='results'):
    if pool == 1 or parallel is False:
        return sync_runner(jobs, force, retval)
    else:
        if pool is None:
            pool = cpu_count()

        return async_runner(jobs, force, pool, retval)

def async_runner(jobs, force, pool, retval):
    try:
        p = NestedPool(pool)
    except:
        print('[ERROR]: can\'t start pool, falling back to sync ')
        return sync_runner(jobs, force, retval)

    count = 0
    results = []

    for job in jobs:
        if 'target' not in job:
            job['target'] = None
        if 'dependency' not in job:
            job['dependency'] = None

        if force is True or check_dependency(job['target'], job['dependency']):
            if 'callback' in job:
                if isinstance(job['args'], dict):
                    results.append(p.apply_async(job['job'], kwds=job['args'], callback=job['callback']))
                else:
                    results.append(p.apply_async(job['job'], args=job['args'], callback=job['callback']))
            else:
                if isinstance(job['args'], dict):
                    results.append(p.apply_async(job['job'], kwds=job['args']))
                else:
                    results.append(p.apply_async(job['job'], args=job['args']))

            count += 1

    p.close()
    p.join()

    if retval == 'count':
        return count
    elif retval is None:
        return None
    elif retval == 'results':
        return [ o.get() for o in results ]
    else:
        return dict(count=count,
                    results=[ o.get() for o in results ])

def sync_runner(jobs, force, retval):
    count = 0
    results = []

    for job in jobs:
        if 'target' not in job:
            job['target'] = None
        if 'dependency' not in job:
            job['dependency'] = None

        if force is True or check_dependency(job['target'], job['dependency']):
            if isinstance(job['args'], dict):
                r = job['job'](**job['args'])
            else:
                r = job['job'](*job['args'])

            results.append(r)
            if 'callback' in job:
                job['callback'](r)

            count +=1

    if retval == 'count':
        return count
    elif retval is None:
        return None
    elif retval == 'results':
        return results
    else:
        return dict(count=count,
                    results=results)
