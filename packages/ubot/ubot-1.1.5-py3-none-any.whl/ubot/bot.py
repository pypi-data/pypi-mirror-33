import asyncio
import functools
import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .requests import get_pool_manager
from .types import HandlerDict, HandlerFn, Update


class UpdateQueue(list):  # type: ignore
    """ A modified list, always sorted by descending update_id"""

    def append(self, item: Update) -> None:
        if item not in self:
            super(UpdateQueue, self).append(item)
            super(UpdateQueue, self).sort(
                key=lambda x: x['update_id'], reverse=True)


class Bot(object):
    def __init__(self,
                 token: str,
                 max_handlers: int = -1,
                 before_update: Optional[Callable[[Update], Awaitable[Any]]]
                 = None,
                 check_update: Optional[Callable[[Update], Awaitable[Any]]]
                 = None,
                 after_error: Optional[Callable[[Update, str], Awaitable[Any]]]
                 = None
                 ) -> None:
        """
        The Class(TM).

        :param token: The Telegram-given token
        :param max_handlers:  The max number of handler that can be processed
            (default = -1 -> infinite)
        :param before_update: A function called before processing each update
            (default = None)
        :param check_update: A function called as validator before the update,
            if return value is falsy the update is not queued (default = None)
        :param after_error: A function called after the error (e.g. to report
            it on a telegram chat, to send you a mail with the error, ecc..)
            (default = None)
        """

        self.token = token
        self.max_handlers = max_handlers
        self.before_update = before_update
        self.check_update = check_update
        self.after_error = after_error

        self.http = get_pool_manager()
        self.logger = logging.getLogger('Bot')
        self.base_url = f'https://api.telegram.org:443/bot{self.token}/'
        self.handlers: List[HandlerDict] = []
        self.ignore_check_handlers: List[HandlerDict] = []
        self.last_id: Optional[int] = None
        self.last_dt: Optional[datetime] = None
        self.update_queue = UpdateQueue()
        self.current_handlers: int = 0

        self.logger.info(f'set webhook with a GET on {self.base_url}'
                         f'setWebhook?url="insert webhook url here"')

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

        url = f'{self.base_url}{endpoint}'
        loop = asyncio.get_event_loop()

        res = await loop.run_in_executor(None, functools.partial(
            self.http.request, method, url, fields=fields))

        self.logger.info(f'Response to {method} on {url}  has status: '
                         f'{res.status} and body: {res.data}')

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

        now = datetime.now()

        # no last_id or next id immediately follows last one -> ready for
        # handling
        if self.last_id is None or \
                update['update_id'] == self.last_id + 1:
            await self.queue_all_handlers_recursive(update)

        # else we put the update in the queue and update the last_dt
        else:
            self.update_queue.append(update)
            self.last_dt = now

        # if the queue is not empty we check how much time is passed, if more
        # than 60s without the last_id+1 message have passed we process the
        # updates, clear the queue and update last_id and last_dt accordingly
        if self.update_queue:
            delta = now - self.last_dt  # type: ignore

            if delta.days > 0 or delta.seconds > 60:
                while len(self.update_queue) > 0:
                    next_update = self.update_queue.pop()
                    await self.queue_all_handlers(next_update)
                self.last_id = None
                self.last_dt = None

    async def queue_handler_list(self, update: Update,
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
            try:
                if self.max_handlers != -1 and \
                        self.current_handlers >= self.max_handlers:
                    break

                if handler['match'](update):
                    h = asyncio.ensure_future(handler['func'](update))
                    await h
                    self.current_handlers += 1

            except Exception as e:
                exc = str(e)
                self.logger.exception(f'Error while executing handler: {exc}',
                                      exc_info=True)
                if self.after_error:
                    await self.after_error(update, exc)

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
            exc = str(e)
            self.logger.exception(f'Error while executing check: {exc}',
                                  exc_info=True)
            if self.after_error:
                await self.after_error(update, exc)

        if check:
            self.queue_handler_list(update, self.handlers)

        self.queue_handler_list(update, self.ignore_check_handlers)

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
            handler: HandlerDict = {
                'func': functools.partial(func, *args, **kwargs),
                'match': match
            }

            if ignore_check:
                self.ignore_check_handlers.append(handler)
            else:
                self.handlers.append(handler)

            async def wrapped(update: Update) -> Optional[Any]:
                return await func(update)

            return wrapped

        return wrapper
