import asyncio
import datetime
import enum
import functools
import json
import logging
from asyncio import Future  # noqa: F401
from typing import Any, Awaitable, Callable, Dict, List, \
    Optional
from typing import Union  # noqa: F401

from .requests import get_pool_manager
from .types import HandlerDict, HandlerFn, Update


class UpdateQueue(list):  # type: ignore
    """ A modified list, always sorted by descending update_id """

    def append(self, item: Update) -> None:
        if item not in self:
            super(UpdateQueue, self).append(item)
            super(UpdateQueue, self).sort(
                key=lambda x: x['update_id'], reverse=True)


class ExceptionThrownWhen(enum.Enum):
    checking_update = 10
    executing_handler = 20
    pass


class Bot(object):
    def __init__(self,
                 token: str,
                 max_handlers: int = -1,
                 before_update: Optional[Callable[
                     [Update], Awaitable[Any]
                 ]] = None,
                 check_update: Optional[Callable[
                     [Update], Awaitable[Any]
                 ]] = None,
                 after_exception: Optional[Callable[
                     [Update, Exception, str], Awaitable[Any]
                 ]] = None
                 ) -> None:
        """
        The Class(TM).

        :param token: The Telegram-given token
        :param max_handlers:  The max number of handler that can be processed
            (default = -1 -> infinite)
        :param before_update: A function called before processing each update
            is handled (default = None)
        :param check_update: A function called as validator before an update
            is handled, if the return value is falsy the update is not queued
            (default = None)
        :param after_exception: A function called after an exception (e.g. to
            report it on a telegram chat, to send you a mail with the error,
            ecc..) (default = None)
        """

        self.token = token
        self.max_handlers = max_handlers
        self.before_update = before_update
        self.check_update = check_update
        self.after_exception = after_exception

        self.http = get_pool_manager()
        self.logger = logging.getLogger('ubot')
        self.base_url = 'https://api.telegram.org:443/bot' + self.token + '/'
        self.handlers = []  # type:  List[HandlerDict]
        self.ignore_check_handlers = []  # type: List[HandlerDict]
        self.last_id = None  # type: Optional[int]
        self.last_queued_dt = None  # type:  Optional[datetime.datetime]
        self.update_queue = UpdateQueue()
        self.current_handlers = 0  # type: int
        self.task_queue = []  # type: List[Future[Any]]

        self.logger.info('set webhook url with a get on '
                         '{url}setWebhook?url="insert webhook url here"'
                         .format(url=self.base_url))

    async def api_request(self, method: str,
                          endpoint: str,
                          fields: Optional[Dict[str, Any]] = None
                          ) -> Dict[str, Any]:
        """
        Wraps the urllib3 request in a more user friendly way, making it async
        and premitting the base Telegram API url.

        :param method: The HTTP method name (GET, POST, PUT, DELETE, HEAD)
        :param endpoint: A Telegram API endpoint (e.g. sendMessage), omitting
            the first slash
        :param fields: A dict of params to be used in the request (used as
            query params with GET/HEAD/DELETE, used as from parans with
            POST/PUT)
        :return: The response from the server, in the form of a dict
        """

        url = self.base_url + endpoint
        loop = asyncio.get_event_loop()
        func = functools.partial(self.http.request, method, url, fields=fields)

        res = await loop.run_in_executor(None, func)

        self.logger.info('Response to {method} on {url} has status: {status}'
                         'and body: {body}'
                         .format(method=method, url=url, status=res.status,
                                 body=res.data))

        return res

    async def push_update(self, update: Update) -> None:
        """
        Pushes an update in the ``update_queue``. This function should be
        called when the webhook URL is hit by a request from Telegram
        containing an update.

        :param update: The update (a dict) received from the Telegram webhook
        :return: None
        """

        if self.before_update:
            await self.before_update(update)

        now = datetime.datetime.now()

        # no last_id or next id immediately follows last one -> ready for
        # handling
        if self.last_id is None or \
                update['update_id'] == self.last_id + 1:
            await self.queue_all_handlers_recursive(update)

        # else we put the update in the queue and update the last_queued_dt
        else:
            self.update_queue.append(update)
            self.last_queued_dt = now

        # if the queue is not empty we check how much time is passed, if more
        # than 60s without the last_id+1 message have passed we process the
        # updates, clear the queue and update last_id and last_queued_dt
        # accordingly
        if self.update_queue:
            delta = now - self.last_queued_dt  # type: ignore

            if delta.days > 0 or delta.seconds > 60:
                while len(self.update_queue) > 0:
                    next_update = self.update_queue.pop()
                    await self.queue_all_handlers(next_update)
                self.last_id = None
                self.last_queued_dt = None

    def queue_task(self, coro_or_future:
                   'Union["Future[Any]", Awaitable[Any]]'
                   ) -> None:
        """
        Wraps a coroutine/future in a task and queues it.

        :param coro_or_future: The coroutine/future to be queued
        :return: None
        """

        h = asyncio.ensure_future(coro_or_future)  # type: Future[Any]
        self.task_queue.append(h)

    async def run_queued_tasks(self) -> None:
        """
        Runs **all** the tasks until the queue is empty

        :return: None
        """

        while self.task_queue:
            try:
                await asyncio.gather(*self.task_queue)
            except Exception as e:
                # must be handled by an attached callback, if the exception
                # is not silenced in this way here it will propagate anyway
                pass

            self.task_queue = [
                task for task in self.task_queue if not task.done()
            ]

    def log_exception(self, update: Update, exception: Exception,
                      when: ExceptionThrownWhen) -> None:
        """
        Logs the exception and calls the after_exception function if it exists.
        N.B.: this should be used only to log *externally* originated exception

        :param update: The update whose processing triggered the exception
        :param exception: The exception object
        :param when: The enum containing info about when the Exception was
            thrown

        :return: None
        """

        _when = str(ExceptionThrownWhen(when).name)
        error = 'Exception {exc}\n occurred when {when}\n during handling of ' \
                'update:\n {update}'\
            .format(exc=str(exception), when=_when, update=json.dumps(update))

        self.logger.error(error, exc_info=True)
        if self.after_exception:
            self.queue_task(self.after_exception(update, exception, _when))

    def queue_handler_list(self, update: Update,
                           handlers: List[HandlerDict]) -> None:
        """
        Executes ``handler['func']`` if ``handler['match']`` returns True and
        the handler limit has not been reached yet.

        :param update: The update (a dict) received from the Telegram webhook
        :param handlers: A list of dicts containing the func and match keywords
            described above
        :return: None
        """

        for handler in handlers:
            if self.max_handlers != -1 and \
                    self.current_handlers >= self.max_handlers:
                break

            if handler['match'](update):
                h = asyncio.ensure_future(
                    handler['func'](update)
                )  # type: Future[Any]

                def error_callback(future: 'Future[Any]') -> None:
                    try:
                        future.result()
                    except Exception as e:
                        when = ExceptionThrownWhen.executing_handler
                        self.log_exception(update, e, when)

                h.add_done_callback(error_callback)
                self.task_queue.append(h)
                self.current_handlers += 1

    async def queue_all_handlers(self, update: Update) -> None:
        """
        Performs the (optional) update check and if it's passed scans all the
        handlers (until ``max_handlers`` limit is reached) to see if the
        message matches them, calling them if it happens.
        To see more info on handlers check the ``add_handler`` decorator docs
        below.

        :param update: The update (a dict) received from the Telegram webhook
        :return: None
        """

        self.current_handlers = 0

        try:
            check = await self.check_update(update) \
                if self.check_update else True
        except Exception as e:
            when = ExceptionThrownWhen.checking_update
            self.log_exception(update, e, when)
            return

        self.queue_handler_list(update, self.ignore_check_handlers)

        if check:
            self.queue_handler_list(update, self.handlers)

        await self.run_queued_tasks()

        self.last_id = update['update_id']

    async def queue_all_handlers_recursive(self, update: Update) -> None:
        """
        Wraps queue_all_handlers to call it recursively if the following update
        can be processed.

        :param update: The update (a dict) received from the Telegram webhook
        :return: None
        """
        await self.queue_all_handlers(update)

        if self.update_queue and \
                self.update_queue[-1]['update_id'] == \
                self.last_id + 1:  # type: ignore

            next_update = self.update_queue.pop()
            await self.queue_all_handlers_recursive(next_update)

    def add_handler(self, match: Callable[[Update], bool],
                    ignore_check: bool = False,
                    *args: str, **kwargs: str
                    ) -> Callable[[HandlerFn], HandlerFn]:
        """
        Adds the decorated function as handler together with the given params.
        The function must take as param (at least) the update, while no
        return value is required.

        :param match: A function that takes the update as param
        :param ignore_check: A boolean (default False) that allows function to
            escape the check_update function
        :param args: Args passed to the decorated function before adding it as
            a handler (these will *not* be dynamic)
        :param kwargs: Kwargs passed to the decorated function (same as args)
        :return: The decorated function.
        """

        def wrapper(func: HandlerFn) -> HandlerFn:
            handler = {
                'func': functools.partial(func, *args, **kwargs),
                'match': match
            }  # type: HandlerDict

            if ignore_check:
                self.ignore_check_handlers.append(handler)
            else:
                self.handlers.append(handler)

            async def wrapped(update: Update) -> Optional[Any]:
                return await func(update)

            return wrapped

        return wrapper
