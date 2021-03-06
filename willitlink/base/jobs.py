import os

import multiprocessing
import multiprocessing.pool
import multiprocessing.dummy

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
    if pool is None:
        pool = cpu_count()

    if pool == 1 or parallel is False:
        return sync_runner(jobs, force, retval)
    elif parallel == 'threads':
        return async_thread_runner(jobs, force, pool, retval)
    else:
        return async_process_runner(jobs, force, pool, retval)

def async_thread_runner(jobs, force, pool, retval):
    try:
        p = multiprocessing.dummy.Pool(pool)
    except:
        print('[ERROR]: can\'t start pool, falling back to sync ')
        return sync_runner(jobs, force, retval)

    return async_runner(jobs, force, pool, retval, p)

def async_process_runner(jobs, force, pool, retval):
    try:
        p = NestedPool(pool)
    except:
        print('[ERROR]: can\'t start pool, falling back to sync ')
        return sync_runner(jobs, force, retval)

    return async_runner(jobs, force, pool, retval, p)

def async_runner(jobs, force, pool, retval, p):
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

def mapper(func, iter, pool=None, parallel='process'):
    if pool is None:
        pool = cpu_count()
    elif pool == 1:
        return map(func, iter)

    if parallel in ['serial', 'single']:
        return map(func, iter)
    else:
        if parallel == 'process':
            p = NestedPool(pool)
        elif parallel.startswith('thread'):
            p = multiprocessing.dummy.Pool(pool)
        else:
            return map(func, iter)

    result = p.map(func, iter)

    p.close()
    p.join()

    return result


def resolve_dict_keys(dict):
    return { k:v.get() for k,v in dict.items() }

def resolve_results(results):
    return [ r.get() for r in results ]

class WorkerPool(object):
    def __exit__(self, *args):
        self.p.close()
        self.p.join()

class ThreadPool(WorkerPool):
    def __enter__(self):
        self.p = multiprocessing.dummy.Pool()
        return self.p

class ProcessPool(WorkerPool):
    def __enter__(self):
        self.p = NestedPool()
        return self.p
