import asyncio
import logging
from collections import namedtuple, OrderedDict
from weakref import WeakValueDictionary
from functools import partial
from aiogear.packet import Type
from aiogear.mixin import GearmanProtocolMixin
from aiogear.response import NoJob

logger = logging.getLogger(__name__)


JobInfo = namedtuple('JobInfo', ['handle', 'function', 'uuid', 'reducer', 'workload'])


class Worker(GearmanProtocolMixin, asyncio.Protocol):
    def __init__(self, *functions, loop=None, grab_type=Type.GRAB_JOB, timeout=None):
        super(Worker, self).__init__(loop=loop)
        self.transport = None
        self.main_task = None
        self.functions = OrderedDict()
        self.running = WeakValueDictionary()
        self.waiters = []
        self.shutting_down = False
        self.timeout = timeout

        grab_mapping = {
            Type.GRAB_JOB: self.grab_job,
            Type.GRAB_JOB_UNIQ: self.grab_job_uniq,
            Type.GRAB_JOB_ALL: self.grab_job_all,
        }

        try:
            self.grab = grab_mapping[grab_type]
        except KeyError:
            raise RuntimeError(
                'Grab type must be one of GRAB_JOB, GRAB_JOB_UNIQ or GRAB_JOB_ALL')

        for func_arg in functions:
            try:
                func, name = func_arg
                self.functions[name] = func
            except TypeError:
                name = func_arg.__name__
                self.functions[name] = func_arg

    def connection_made(self, transport):
        logger.info('Connection is made to %r', transport.get_extra_info('peername'))
        self.transport = transport

        if self.timeout is not None:
            can_do = partial(self.can_do_timeout, timeout=self.timeout)
        else:
            can_do = self.can_do

        for fname in self.functions.keys():
            logger.debug('Registering function %s', fname)
            can_do(fname)
        self.main_task = self.get_task(self.run())

    def connection_lost(self, exc):
        self.transport = None

    def get_task(self, coro):
        return asyncio.ensure_future(coro, loop=self.loop)

    async def run(self,):
        no_job = NoJob()
        while not self.shutting_down:
            self.pre_sleep()
            await self.wait_for(Type.NOOP)
            response = await self.grab()
            if response == no_job:
                continue

            try:
                job_info = self._to_job_info(response)
                func = self.functions.get(job_info.function)
                if not func:
                    logger.warning(
                        'Failed to find function %s in %s', job_info.function,
                        ', '.join(self.functions.keys()))
                    self.work_fail(job_info.handle)
                    continue

                try:
                    result_or_coro = func(job_info)
                    if asyncio.iscoroutine(result_or_coro):
                        task = self.get_task(result_or_coro)
                        self.running[job_info.handle] = task
                        result = await task
                    else:
                        result = result_or_coro
                    self.work_complete(job_info.handle, result)
                except Exception as ex:
                    logger.exception('Job (handle %s) resulted with exception', job_info.handle)
                    self.work_exception(job_info.handle, str(ex))
                finally:
                    self.running.pop(job_info.handle, None)

            except AttributeError:
                logger.error('Unexpected GRAB_JOB response %r', response)

    async def shutdown(self, graceful=False):
        logger.debug('Shutting down worker {}gracefully...'.format('' if graceful else 'un'))
        self.shutting_down = True
        sub_tasks = list(self.running.values())
        if graceful:
            if sub_tasks:
                await asyncio.wait(sub_tasks, loop=self.loop)
        else:
            async def cancel_and_wait(tasks):
                for task in tasks:
                    task.cancel()
                try:
                    await asyncio.wait(tasks, loop=self.loop)
                except asyncio.CancelledError:
                    pass
            if sub_tasks:
                await cancel_and_wait(sub_tasks)
        self.main_task.cancel()

        if self.transport:
            self.transport.close()

    @staticmethod
    def _to_job_info(job_assign):
        attrs = ['handle', 'function', 'uuid', 'reducer', 'workload']
        values = [getattr(job_assign, attr, None) for attr in attrs]
        return JobInfo(*values)

    def register_function(self, func, name=''):
        if not self.transport:
            raise RuntimeError('Worker must be connected to the daemon')
        name = name or func.__name__
        self.functions[name] = func
        return self.can_do(name)

    def grab_job_all(self):
        self.send(Type.GRAB_JOB_ALL)
        return self.wait_for(Type.NO_JOB, Type.JOB_ASSIGN_ALL)

    def grab_job_uniq(self):
        self.send(Type.GRAB_JOB_UNIQ)
        return self.wait_for(Type.NO_JOB, Type.JOB_ASSIGN_UNIQ)

    def grab_job(self):
        self.send(Type.GRAB_JOB)
        return self.wait_for(Type.NO_JOB, Type.JOB_ASSIGN)

    def pre_sleep(self):
        self.send(Type.PRE_SLEEP)

    def can_do(self, function):
        self.send(Type.CAN_DO, function)

    def can_do_timeout(self, function, timeout):
        self.send(Type.CAN_DO_TIMEOUT, function, timeout)

    def work_fail(self, handle):
        self.send(Type.WORK_FAIL, handle)

    def work_exception(self, handle, data):
        self.send(Type.WORK_EXCEPTION, handle, data)

    def work_complete(self, handle, result):
        if result is None:
            result = ''
        self.send(Type.WORK_COMPLETE, handle, result)

    def set_client_id(self, client_id):
        self.send(Type.SET_CLIENT_ID, client_id)
