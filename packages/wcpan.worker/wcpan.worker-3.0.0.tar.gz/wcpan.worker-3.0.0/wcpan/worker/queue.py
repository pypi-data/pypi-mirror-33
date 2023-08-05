import asyncio
from typing import Callable

from wcpan.logger import DEBUG, EXCEPTION

from .task import regular_call, ensure_task, MaybeTask, TerminalTask


class AsyncQueue(object):

    def __init__(self, maximum=None):
        self._max = 1 if maximum is None else maximum
        self._lock = asyncio.Semaphore(self._max)
        self._loop = asyncio.get_event_loop()
        self._running = False

        self._reset()

    def start(self):
        if self._running:
            return
        self._loop.create_task(self._process())
        self._running = True

    async def stop(self):
        if not self._running:
            return
        self._running = False
        task = TerminalTask()
        for i in range(self._max):
            self._queue.put_nowait(task)
        self._end = asyncio.Event()
        await self._end.wait()
        self._reset()

    def flush(self, filter_: Callable[['Task'], bool]):
        q = self._get_internal_queue()
        nq = filter(lambda _: not filter_(_), q)
        nq = list(nq)
        DEBUG('wcpan.worker') << 'flush:' << 'before' << len(q) << 'after' << len(nq)
        self._set_internal_queue(nq)

    def post(self, task: MaybeTask):
        task = ensure_task(task)
        self._queue.put_nowait(task)

    async def _process(self):
        while self._running:
            await self._lock.acquire()
            task = await self._queue.get()
            self._loop.create_task(self._run(task))

    async def _run(self, task):
        try:
            if isinstance(task, TerminalTask):
                return
            else:
                await regular_call(task)
        except Exception as e:
            EXCEPTION('wcpan.worker', e) << 'uncaught exception'
        finally:
            self._queue.task_done()
            self._lock.release()
            if self._end and self._lock._value == self._max:
                self._end.set()

    def _reset(self):
        self._queue = asyncio.PriorityQueue()
        self._end = None

    def _get_internal_queue(self):
        return self._queue._queue

    def _set_internal_queue(self, nq):
        self._queue._queue = nq
