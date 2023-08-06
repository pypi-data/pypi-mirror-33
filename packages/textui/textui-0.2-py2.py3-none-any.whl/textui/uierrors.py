"""

"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# If comparing to the int type becomes a compatibility issue, try this. Requires installing the builtins package for
# Python 2 (http://python-future.org/compatible_idioms.html)
# from builtins import int

import sys
import traceback
import warnings
import pdb


class UIErrorWrapper:
    """
    Wrapper class used to control exception raising in UI functions.

    This class is used to wrap UI error calls so that they can be deactivated
    when a UI driven program is released to users. Developers using the textui
    package can thus control how exceptions and warnings deliberately issued
    by textui are handled using the following class propeties:

        do_throw_both: default ``True``, if set to ``False`` suppresses both exceptions
        and warnings issued by the UI functions.

        do_throw_exceptions, do_throw_warnings: default ``True``, these allow control
        of exceptions and warnings separately. If set to ``False``, they suppress
        their respective messages.

        do_soft_exit: default ``False``, if set to ``True`` a simple message is displayed
        prior to exiting rather than a full stack trace that might alarm users.

        err_log_stream: defaults to ``sys.stderr``, this can be set to other files or
        streams to, for example, allow you to send error messages to a log file
        that users can send in.

    The recommended use is that you set these in the top level of your program after
    any import statements (this prevents your settings from being overwritten by
    imported modules). Ideally, you could control this using some environmental
    variable or command line switch so that users could turn on error messages for
    debugging reports, as::

        from textui.uierrors import UIErrorWrapper
        mydebug_flag = os.getenv('MY_DEBUG') > 0
        if mydebug_flag:
            UIErrorWrapper.do_soft_exit = False
            # Warnings are not covered by the soft exit
            UIErrorWrapper.do_throw_warnings = True
        else:
            UIErrorWrapper.do_soft_exit = True
            UIErrorWrapper.do_throw_warnings = False

    Caution is recommended when setting ``do_throw_both`` or ``do_throw_exceptions`` to ``False``
    as this will turn off error checking in direct input to the UI functions (that
    is, input in your code, not the user input) which may simply lead to weirder errors
    deeper in the code.


    For those working on textui itself, any exceptions or warnings should be issued
    though this class using the class methods ``raise_error`` and ``warn``.
    """
    do_throw_both = True
    do_throw_exceptions = True
    do_throw_warnings = True

    do_soft_exit = False

    err_log_stream = sys.stderr

    def __init__(self, err):
        pass

    @classmethod
    def raise_error(cls, err):
        """
        (classmethod) Wrapper method to raise exceptions only if the wrapper class is set to do so

        Call this method with the instance of the exception to raise, as in
        ``UIErrorWrapper.raise_error(UITypeError("message to issue with error"))``
        Its behavior is modified by the class properties ``do_throw_both``,
        ``do_throw_exceptions``, and ``do_soft_exit``. See class docstring for details.

        :param err: the instance of the exception to raise
        :type err: Exception

        :return: nothing.
        """
        if cls.do_throw_both and cls.do_throw_exceptions:
            if not cls.do_soft_exit:
                print("Error thrown using UIErrorWrapper", file=cls.err_log_stream)
                raise(err)
            else:
                print("")
                print("*******************************")
                print("An internal error has occurred.")
                print("This program will exit. Contact")
                print("the author with a bug report.")
                print("*******************************")
                print("")
                sys.exit(1)

    @classmethod
    def warn(cls, msg):
        """
        (classmethod) Wrapper method to issue warnings only if the wrapper class is set to do so

        Call this method with the message of the warning to issue, as
        in ``UIErrorWrapper.warn("warning message to issue")``
        Its behavior is modified by the class properties ``do_throw_both``
        and ``do_throw_warnings``, see class docstring for details.

        :param msg: The warning message to issue as a string
        :type msg: str

        :return: nothing.
        """
        if cls.do_throw_both and cls.do_throw_warnings:
            warnings.warn(msg)


class UIError(Exception):
    """
    Parent class for any errors thrown by the UI functions, thus users can catch
    these errors with ``try: except UIError:`` to allow a program using this package
    to exit gracefully or otherwise handle the error.
    """
    pass


class UITypeError(UIError):
    """
    A subclass of UIError intended for errors about a variable being the wrong type
    """
    pass


class UIValueError(UIError):
    """
    A subclass of UIError intended for errors about a variable having the wrong value.
    """
    pass


class UIOptNoneError(UIError):
    """
    A subclass of UIError intended specifically for the ``opt_user_*`` functions in the
    :mod:`textui.uielements` module, to be raised when these functions receive a ``None``
    type from their respective ``user_*`` function.
    """
    pass


class UITermError(UIError):
    pass


class UICallbackError(UIError):
    def __init__(self, callback):
        message = "A callback has not returned a new _CallBack instance.\n" \
                  "See above the traceback for the menu hierarchy leading to the bad call"
        super(UICallbackError, self).__init__(message)
        hierarchy = callback.get_menu_hierarchy()
        for i in range(len(hierarchy)):
            mstr = "  "*i + "--> " + hierarchy[i]
            print(mstr)
