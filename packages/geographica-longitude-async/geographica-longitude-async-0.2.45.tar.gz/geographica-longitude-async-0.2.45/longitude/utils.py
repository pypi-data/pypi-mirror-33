import asyncio
import threading

from functools import partial, wraps
from collections import Sized, Iterable

from longitude.exceptions import InvalidAttribute


def chain_fns(*fns):
    def fn_chain(*args, **kwargs):

        for fninfo in fns:

            fn_args = []
            fn_kwargs = {}

            if isinstance(fninfo, tuple):

                if len(fninfo) == 0:
                    fn = lambda x: x
                else:
                    fn = fninfo[0]

                if len(fninfo)>1:
                    fn_args = fninfo[1]

                if len(fninfo)>2:
                    fn_kwargs = fninfo[2]
            else:
                fn = fninfo

            fn_args = list(args) + fn_args
            kwargs.update(fn_kwargs)
            fn_kwargs = kwargs

            args = [fn(*fn_args, **fn_kwargs)]
            kwargs = {}

        return args[0]

    return fn_chain


def try_or_none(fn, allow=(BaseException)):
    def do_try_fn(value):
        try:
            return fn(value)
        except allow:
            return None

    return do_try_fn


def try_list(fn):
    def do_try_list(value):
        if isinstance(value, str):
            value = str.split(',')

        return list(map(
            lambda x: fn(x),
            value
        ))

    return do_try_list


def parse_spec_on_missing_default(key):
    raise InvalidAttribute(key, message='Missing attribute {}.')


def parse_spec_on_value_success_default(key, value):
    yield (key, value)


def parse_spec(
    spec,
    values,
    on_value_success=None,
    on_missing=None
):
    if on_value_success is None:
        on_value_success = parse_spec_on_value_success_default

    if on_missing is None:
        on_missing = parse_spec_on_missing_default

    for conf_param in spec:

        if len(conf_param) not in (2, 3):
            raise RuntimeError('Configuration param %s must have 2 or 3 elements.' % str(conf_param))

        config_param_name, ctype = conf_param[:2]

        if len(conf_param) == 3:
            default = conf_param[2]
        else:
            default = None

        value = values.get(config_param_name, default)

        if value is None:
            on_missing(config_param_name)

        if ctype == bool:
            value = value if isinstance(value, bool) else \
                value == '1'
        else:
            value = ctype(value)

        if value is None and default is not None:
            value = default

        if value is None:
            on_missing(config_param_name)

        on_value_success(config_param_name, value)


def compile_spec(
    spec,
    on_value_success=None,
    on_missing=None
):
    return partial(
        parse_spec,
        spec,
        on_value_success=on_value_success,
        on_missing=on_missing
    )


def is_list_or_tuple(val, length=None):
    is_list_or_tuple = \
        (not isinstance(val, str)) and \
        isinstance(val, Sized) and \
        isinstance(val, Iterable) and \
        ((length is None) or len(val) == length)

    return is_list_or_tuple


def sync_worker(task_queue, have_fn):
    asyncio.set_event_loop(asyncio.new_event_loop())

    while True:
        if len(task_queue) == 0:
            have_fn.acquire(blocking=True)

        fn_finished_lock, fn_result, fn, args, kwargs = task_queue.pop()

        try:
            fn_result.result = asyncio.get_event_loop()\
                .run_until_complete(fn(*args, **kwargs))
        except BaseException as e:
            fn_result.error = e

        fn_finished_lock.release()


def sync_worker_init():

    class WorkerResult:
        result = None
        error = None

    task_queue = []
    have_fn = threading.Lock()
    have_fn.acquire()

    th = threading.Thread(
        name='SyncEventLoopThread',
        target=sync_worker,
        args=(task_queue, have_fn),
        daemon=True
    )

    th.start()

    def sync_worker_run(fn, args, kwargs):
        fn_finished_lock = threading.Lock()
        fn_finished_lock.acquire()
        fn_result = WorkerResult()
        task_queue.append(
            (fn_finished_lock, fn_result, fn, args, kwargs)
        )

        if len(task_queue) == 1:
            have_fn.release()

        fn_finished_lock.acquire(blocking=True)

        if fn_result.error:
            raise fn_result.error from None

        return fn_result.result

    return sync_worker_run


run_sync = sync_worker_init()


def allow_sync(fn):
    @wraps(fn)
    def add_sync_option(*args, **kwargs):
        call_sync = kwargs.pop('sync', None)

        if isinstance(call_sync, bool) and call_sync:
            res = run_sync(fn, args, kwargs)

            return res
        else:
            return fn(*args, **kwargs)

    return add_sync_option
