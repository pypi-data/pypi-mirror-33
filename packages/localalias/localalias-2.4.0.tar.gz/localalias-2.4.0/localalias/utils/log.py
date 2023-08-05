"""Loggers and utilities related to logging.

Attributes:
    logger: main logging.Logger object.
"""

import logging

import localalias.utils.xdg as xdg

logger = logging.getLogger("localalias")


def init_logger(*, debug=False, verbose=False):
    """Initializes the main logger."""
    _add_vdebug_level(logging)
    root = logging.getLogger()

    if debug:
        if verbose:
            level = logging.VDEBUG
        else:
            level = logging.DEBUG
    else:
        level = logging.INFO

    root.setLevel(level)

    sh = logging.StreamHandler()
    formatter = _getFormatter()
    sh.setFormatter(formatter)
    sh.setLevel(level)
    root.addHandler(sh)

    if debug:
        logfile_path = '{}/debug.log'.format(xdg.getdir('data'))
        fh = logging.FileHandler(logfile_path)
        formatter = _getFormatter(verbose=True)
        fh.setFormatter(formatter)
        fh.setLevel(level)
        root.addHandler(fh)
        root.debug('Debug mode enabled.')


def _add_vdebug_level(logging):
    """Adds custom logging level for verbose debug logs."""
    VDEBUG_LEVEL_NUM = 5
    logging.addLevelName(VDEBUG_LEVEL_NUM, "VDEBUG")

    def vdebug(self, message, *args, **kwargs):
        if self.isEnabledFor(VDEBUG_LEVEL_NUM):
            self._log(VDEBUG_LEVEL_NUM, message, args, **kwargs)

    logging.Logger.vdebug = vdebug
    logging.VDEBUG = VDEBUG_LEVEL_NUM


def _getFormatter(*, verbose=False):
    """Get log formatter.

    Args:
        verbose: True if a more verbose log format is desired.

    Returns:
        logging.Formatter object.
    """
    base_formatting = '[%(levelname)s] %(message)s'

    if verbose:
        formatter = logging.Formatter('[%(process)s] (%(asctime)s) {}'.format(base_formatting),
                                      datefmt='%Y-%m-%d %H:%M:%S')
    else:
        formatter = logging.Formatter(base_formatting)

    return formatter
