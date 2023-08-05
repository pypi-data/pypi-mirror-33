from __future__ import absolute_import, unicode_literals
from .celery import app
from celery import Task

from tlscanary import xpcshell_worker as xw


foxes = []


def kill_stray_foxes():
    """Ensure that there are no stray foxes leaking into the environment"""
    global foxes
    for fox in foxes:
        if fox.worker_process is None:
            # Worker was never spawned
            continue
        try:
            fox.kill()
        except OSError:
            # already killed
            pass


def new_worker(*args, **kwargs):
    """Return worker instance that is registered with the global foxes registry"""
    global foxes
    fox = xw.XPCShellWorker(*args, **kwargs)
    foxes.append(fox)
    return fox


class XPCShellWorkerTask(Task):
    _test_instance = None
    _base_instance = None

    @property
    def test_instance(self):
        if self._test_instance is None:
            self._test_instance = new_worker()
            self._test_instance.spawn()
        return self._test_instance

    @property
    def base_instance(self):
        if self._base_instance is None:
            self._base_instance = new_worker()
            self._base_instance.spawn()
        return self._base_instance


@app.task(base=XPCShellWorkerTask)
def regression_scan(host, rank=None, include_certificates=False):
    test_result = regression_scan.test_instance.ask(
        xw.Command("scan",
                   host=host, rank=rank,
                   include_certificates=include_certificates,
                   timeout=10), timeout=12)
    if test_result.is_success():
        return test_result
    base_result = regression_scan.test_instance.ask(
        xw.Command("scan",
                   host=host, rank=rank,
                   include_certificates=False,
                   timeout=10), timeout=12)
    if base_result.is_success():
        return test_result()



@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)
