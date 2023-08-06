

import logging.config

from pyjuhelpers.timer import Timer

logging.getLogger(__name__).addHandler(logging.NullHandler())


defaultConf={
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)8s %(message)s'
        },
        'debug': {
            'format': '[%(process)d] [%(asctime)s] [%(relativeCreated)18s][%(levelname)6s] [%(message)s]  [%(filename)s:%(lineno)s]'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'console_debug': {
            'level': 'DEBUG',
            'formatter': 'debug',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'debug',
            'filename': 'debug.log',
            'mode': 'a',
            'maxBytes': 103116800, #50MB
            'backupCount': 5,
            "encoding": "utf8"
        },
    },
    'root': {
            'handlers': ['console'],
            'level': 'WARNING',

    }

}
import copy

infoConf=copy.deepcopy(defaultConf)
infoConf['root']['handlers']=['console']
infoConf['root']['level']='INFO'


debugConf=copy.deepcopy(defaultConf)
debugConf['root']['handlers']=['console_debug']
debugConf['root']['level']='DEBUG'


fileConf=copy.deepcopy(defaultConf)
fileConf['root']['handlers']=['console','file']
fileConf['root']['level']='DEBUG'
fileConf['handlers']['console']['level']='WARNING'

import structlog

structlog.configure(#
    processors=[
        #structlog.stdlib.filter_by_level,
        #structlog.stdlib.add_logger_name,
        #structlog.stdlib.add_log_level,

        structlog.stdlib.PositionalArgumentsFormatter(),
        #structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),

        structlog.dev.ConsoleRenderer(colors=False)

        ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
#print(structlog.get_config())

import time


def get_func_param(decorated_function, dec_fn_args, dec_fn_kwargs):
    arg_names = decorated_function.__code__.co_varnames[:decorated_function.__code__.co_argcount]
    args = dec_fn_args[:len(arg_names)]
    defaults = decorated_function.__defaults__ or ()
    args = args + defaults[len(defaults) - (decorated_function.__code__.co_argcount - len(args)):]
    params = list(zip(arg_names, args))
    args = dec_fn_args[len(arg_names):]
    if args:
        params.append(('args', args))

    param_dict = {}
    for p in params:
        param_dict[p[0]] = repr(p[1])
    if dec_fn_kwargs:
        for k, v in dec_fn_kwargs.items():
            param_dict[k] = repr(v)

    return param_dict

def log_func_detail(logger, log_time=False, time_key=None, level=logging.DEBUG):
    def log_function_entry_and_exit(decorated_function):
        """
        Function decorator logging entry + exit and parameters of functions.

        Entry and exit as logging.info, parameters as logging.DEBUG.
        """
        from functools import wraps


        @wraps(decorated_function)
        def wrapper(*dec_fn_args, **dec_fn_kwargs):

            func_name = decorated_function.__name__
            param_dict = get_func_param(decorated_function, dec_fn_args,dec_fn_kwargs)


            logger.log(level,"{}".format(func_name), **param_dict)
            # Execute wrapped (decorated) function:

            start=time.time()
            if log_time or time_key:
                _time_key = time_key if time_key else func_name

                with Timer(key=_time_key, store=True) as t:
                    out = decorated_function(*dec_fn_args, **dec_fn_kwargs)
            else:
                out = decorated_function(*dec_fn_args, **dec_fn_kwargs)
            end = time.time()
            if log_time:
                param_dict['elapsed']=((end-start)*1000)
                logger.log(level,"DONE {}".format(func_name), **param_dict)

            return out
        return wrapper
    return log_function_entry_and_exit