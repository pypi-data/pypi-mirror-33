# -*- coding: utf-8 -*-
import os
import six

from . import cdbg_native
from .exts.cloud_debug_python.module_explorer import GetCodeObjectAtLine, _GetModuleCodeObjects, _GetLineNumbers

from rook.lib.logger import logger

from ..exceptions import RookBdbCodeNotFound, RookBdbSetBreakpointFailed

_flags = None
cdbg_native.InitializeModule(_flags)


class Bdb(object):
    def __init__(self):
        self.fncache = {}
        self._cookies = {}
        self.user_line = None

    def set_trace(self):
        # Not needed
        pass

    def canonic(self, filename):
        if filename[0] == "<" and filename[-1] == ">":
            return filename
        canonic = self.fncache.get(filename)
        if not canonic:
            canonic = os.path.abspath(filename)
            canonic = os.path.normpath(canonic)
            self.fncache[filename] = canonic
        return canonic

    def ignore_current_thread(self):
        # Not needed
        pass

    def set_break(self, module, filename, lineno):
        status, code_object = GetCodeObjectAtLine(module, lineno)
        if not status:
            if hasattr(module, '__file__'):
                logger.debug("CodeNotFound module filename %s", module.__file__)

            for cobj in _GetModuleCodeObjects(module):
                logger.debug("Name: %s", cobj.co_name)
                for cline in _GetLineNumbers(cobj):
                    logger.debug("Name: %s, Line %d", cobj.co_name, cline)

            raise RookBdbCodeNotFound(alternatives=code_object,
                                      filename=filename,
                                      module_filename=module.__file__ if hasattr(module, '__file__') else "",
                                      line=lineno)

        # Install the breakpoint
        cookie = cdbg_native.SetConditionalBreakpoint(code_object, lineno, None, self._callback)
        if not cookie:
            raise RookBdbSetBreakpointFailed()

        self._cookies[filename, lineno] = cookie

    def clear_break(self, filename, lineno):
        pos = filename, lineno
        try:
            cookie = self._cookies[pos]
        except KeyError:
            return

        cdbg_native.ClearConditionalBreakpoint(cookie)
        del self._cookies[pos]

    def clear_all_breaks(self):
        for cookie in six.itervalues(self._cookies):
            cdbg_native.ClearConditionalBreakpoint(cookie)

        self._cookies = {}

    def close(self):
        pass

    def _callback(self, event, frame):

        if event != cdbg_native.BREAKPOINT_EVENT_HIT:
            logger.error("Unexpected event- %d", event)
            return

        if frame and self.user_line:
            self.user_line(frame)

    def fixed_line_number(self, frame):
        if six.PY3:
            # Wrong line numbers were fixed for Python3 but not for Python2 🤷‍♂️‍️
            return frame.f_lineno

        first_line = frame.f_code.co_firstlineno
        current_line = frame.f_lineno
        lnotab = frame.f_code.co_lnotab

        if not lnotab:
            return current_line

        line = first_line

        for i in range(0, len(lnotab), 2):
            line_delta = ord(lnotab[i + 1])

            if line == current_line:
                j = i

                while j < len(lnotab):
                    if line_delta == 0:
                        j += 2
                        line_delta = ord(lnotab[j + 1])
                    else:
                        return line + line_delta

            line += line_delta

        return current_line
