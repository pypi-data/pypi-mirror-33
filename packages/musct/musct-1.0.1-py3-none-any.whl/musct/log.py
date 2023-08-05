import os
import sys

from yaml import YAMLError

from musct.reference import PROG_NAME


class ErrorLogger:
    _verbose = True

    def set_verbose(self, verbose):
        self._verbose = verbose

    def print_debug(self, msg: str, file=sys.stderr):
        if self._verbose:
            print(msg, file=file)

    def print_warn(self, msg: str, file=sys.stderr):
        if self._verbose:
            print("%s: warn: %s" % (PROG_NAME, msg), file=file)
        else:
            print(msg, file=file)

    def print_err(self, msg: str, file=sys.stderr):
        if self._verbose:
            print("%s: error: %s" % (PROG_NAME, msg), file=file)
        else:
            print(msg, file=file)

    def print_critical_err(self, msg: str, status=-1, file=sys.stderr):
        if self._verbose:
            print("%s: fatal: %s" % (PROG_NAME, msg), file=file)
        else:
            print(msg, file=file)
        exit(status)

    def print_yaml_err(self, filepath: str, err: YAMLError, should_exit=True, file=sys.stderr):
        print(format_yaml_err(filepath, err), file=file)
        if should_exit:
            exit(os.EX_CONFIG)


def format_yaml_err(filepath: str, err: YAMLError):
    if hasattr(err, 'problem_mark'):
        mark = err.problem_mark
        return "%s: syntax error: %s: (%s:%s)" % (PROG_NAME, filepath, mark.line + 1, mark.column + 1)
    return "%s: %s" % (filepath, err)


logger = ErrorLogger()
