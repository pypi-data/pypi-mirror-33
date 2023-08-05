import logging
import sys
import traceback
import logging.handlers

CONFIG = {
    'DEVELOP': False  # For debugging purposes
}


def _get_syslog_handler():
    """ Return the syslog handler. """
    handler = logging.handlers.SysLogHandler()
    formatter = logging.Formatter('%(name)s %(message)s')
    handler.formatter = formatter
    return handler


def _get_except_hook(log):
    """ Log unhandled exceptions. """
    def log_except_hook(exc_type, exc_value, exc_traceback, log=log):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        log.error("Uncaught exception: {}".format(traceback.format_exception(exc_type, exc_value,
                                                                             exc_traceback)))
    return log_except_hook


def get_logger(logname, level=logging.DEBUG):
    """ Return a logger for this logname. """
    log = logging.getLogger(logname)
    log.setLevel(level)
    if not CONFIG['DEVELOP']:
        if not any(isinstance(h, logging.handlers.SysLogHandler) for h in log.handlers):
            # SysLogHandler is not yet registered
            log.addHandler(_get_syslog_handler())
    return log


def configure_logging(logname='default', is_develop=False, loglevel=logging.DEBUG):
    """ Set up the log handler and add a hook for unhandled exceptions. """
    CONFIG['DEVELOP'] = is_develop
    log = get_logger(logname, level=loglevel)
    if is_develop:
        logging.basicConfig(level=loglevel)
    else:
        sys.excepthook = _get_except_hook(log)
    return log
