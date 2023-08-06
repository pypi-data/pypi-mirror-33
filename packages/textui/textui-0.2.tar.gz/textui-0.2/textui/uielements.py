"""
This module contains the low level text UI elements for the package textui.

This module contains the functions that actually handle user input. Each function is
configured so that the user input occurs within a while True loop. Input checking is
done on the user input and the loop will not exit if an invalid value was given.

You are welcome to use these functions directly in your programs if you do not wish
to use the menu construct classes also provided in the textui package.
"""
from __future__ import print_function, division, absolute_import
# If comparing to the int type becomes a compatibility issue, try this. Requires installing the builtins package for
# Python 2 (http://python-future.org/compatible_idioms.html)
# from builtins import int

from collections import OrderedDict
import copy
import datetime as dt
import re
import sys

from .uiutils import print_in_columns
from .uierrors import UIErrorWrapper, UITypeError, UIValueError, UIOptNoneError


if sys.version_info.major == 2:
    text_input = raw_input
    from backports.shutil_get_terminal_size import get_terminal_size
elif sys.version_info.major == 3:
    text_input = input
    from shutil import get_terminal_size
else:
    raise NotImplementedError('No text input function defined for Python version {}'.format(sys.version_info.major))


def user_input_list(prompt, options, returntype="value", currentvalue=None, emptycancel=True, printcols=True, **printcolargs):
    """This function provides the user a list of choices to choose from, the user selects one by its number

    :param prompt: The text prompt to display for the user
    :type prompt: str

    :param options: The list of options to present
    :type options: list or tuple

    :param returntype: optional, can be "value" or "index", "value" is default. If set to "value", the return value
        will be the value of the option chosen. If set to "index", the return value will be the index of the list
        chosen.
    :type returntype: str

    :param currentvalue: optional, defaults to None. Sets what the current value of this option is. If one is given, it
        will be marked with a * in the list.

    :param emptycancel: optional, defaults to ``True``. If ``True``, then this function will return None if no
        answer is chosen (but not if an invalid selection is chosen). A message indicating that an empty answer will
        cancel is added to the prompt. If ``False``, the list of options will be re-presented if no answer given.
    :type emptycancel: bool

    :param printcols: optional, controls whether the individual options should be spread out across the terminal in
        columns (``True``) or all printed in one column (``False``).
    :type printcols: bool

    :param printcolargs: keyword arguments to be passed through to :func:`textui.uiutils.print_in_columns`. Only has
        an effect if ``printcols`` is ``True``.

    :return: either the value or index of the user choice (see returntype) or the type None.
    """

    # Input checking
    if type(prompt) is not str:
        UIErrorWrapper.raise_error(UITypeError("prompt must be a string"))
    if type(options) is not list and type(options) is not tuple:
        UIErrorWrapper.raise_error(UITypeError("options must be a list or tuple"))
    if type(returntype) is not str or returntype.lower() not in ["value", "index"]:
        UIErrorWrapper.raise_error(UITypeError("returntype must be one of the strings 'value' or 'index'"))
    if type(emptycancel) is not bool:
        UIErrorWrapper.raise_error(UITypeError("emptycancel must be a bool"))

    print(prompt)
    if emptycancel:
        print("A empty answer will cancel.")
    if currentvalue is not None:
        print("The current value is marked with a *")

    entries = []
    for i in range(1, len(options)+1):
        if currentvalue is not None and options[i-1] == currentvalue:
            currstr = "*"
        else:
            currstr = " "
        entries.append("  {2}{0}: {1}".format(i, options[i-1], currstr))

    if printcols:
        print_in_columns(entries, **printcolargs)
    else:
        print('\n'.join(entries))

    while True:
        userans = text_input("Enter 1-{0}: ".format(len(options)))
        if len(userans) == 0:
            if emptycancel:
                return None
            else:
                continue

        try:
            userans = int(userans)
        except ValueError:
            print("Input invalid")
        else:
            if userans > 0 and userans <= len(options):
                break

    if returntype.lower() == "value":
        return options[userans-1]
    elif returntype.lower() == "index":
        return userans - 1
    else:
        UIErrorWrapper.raise_error(UIValueError("Value '{0}' for keyword 'returntype' is not recognized".format(returntype)))


def user_input_date(prompt, currentvalue=None, emptycancel=True, req_time_part='day', smallest_allowed_time_part=None):
    """Request that the user input a date.

    :param prompt: A string printed as the prompt; it should describe what date is
        being requested.
    :type prompt: str
    :param currentvalue: optional, if given, will print out the current value given. Useful when setting an option so
        that the user knows what the current value is.
    :type currentvalue: datetime.date or datetime.datetime
    :param emptycancel: optional, defaults to True. A boolean determining whether an
        empty answer will cause this function to return None. If false, the user must enter
        a valid date to exit (not recommended for most cases).
    :type emptycancel: bool
    :param req_time_part: optional, defaults to 'day'. A string describing the largest
        required time part, must be one of: 'year', 'month', 'day', 'hour', 'minute', 'second'.
        If this is set to 'minute' for example, then the user must input at least year, month,
        day, hour, and minute, or it will be rejected.
    :type req_time_part: str
    :param smallest_allowed_time_part: optional, defaults to None. A string describing
        the smallest piece of time the user is allowed to specify. Must be one of the same strings
        as allowed for req_time_part, and must be the same or smaller piece of time than req_time_part.
        For example, if this is set to 'minute', then the user may not include seconds in their
        answer. If left as None, then it will be automatically set to the same as req_time_part,
        effectively giving the user only one choice for how specific to make their time.
    :type smallest_allowed_time_part: str
    :return: A datetime.datetime instance, or None.
    """

    # Prompts the user for a date in yyyy-mm-dd or yyyy-mm-dd HH:MM:SS format. Only input is a prompt describing
    # what the date is. Returns a datetime object. The currentvalue keyword can be used to display the current
    # setting, but it must be a datetime object as well. Returns none if user ever enters an empty string.
    if currentvalue is not None and type(currentvalue) is not dt.datetime and type(currentvalue) is not dt.date:
        UIErrorWrapper.raise_error(UITypeError("If given, currentvalue must be a datetime.date or datetime.datetime instance"))
    elif type(currentvalue) is dt.date:
        currentvalue = dt.datetime(currentvalue.year, currentvalue.month, currentvalue.day)

    if type(emptycancel) is not bool:
        UIErrorWrapper.raise_error(UITypeError("If given, emptycancel must be a bool"))

    # Must give the time formats as a list of tuples (instead of keyword-value pairs) to preserve order because
    # at least in Python 2 **kwargs becomes a regular dict() and so loses order before OrderedDict even sees it.
    time_formats = OrderedDict([('year', '%Y'), ('month', '%Y-%m'), ('day', '%Y-%m-%d'),
                                ('hour', '%Y-%m-%d %H'), ('minute', '%Y-%m-%d %H:%M'), ('second', '%Y-%m-%d %H:%M:%S')])
    if req_time_part not in time_formats:
        UIErrorWrapper.raise_error(UITypeError('req_time_part must be one of: {}'.format(', '.join(time_formats.keys()))))
    elif smallest_allowed_time_part not in time_formats and smallest_allowed_time_part is not None:
        UIErrorWrapper.raise_error(UITypeError('smallest_allowed_time_part must be one of: {}'.format(', '.join(time_formats.keys()))))
    else:
        key_ind = time_formats.keys().index(req_time_part)
        if smallest_allowed_time_part is None:
            smallest_ind = key_ind + 1
        else:
            smallest_ind = time_formats.keys().index(smallest_allowed_time_part)+1

        if smallest_ind <= key_ind:
            UIErrorWrapper.raise_error(UIValueError('req_time_part must be a larger piece of time than smallest_allowed_time_part'))
        allowed_time_fmts = time_formats.values()[key_ind:smallest_ind]
        allowed_fmts_str = ', '.join([_human_readable_time_format(fmt) for fmt in allowed_time_fmts])

    print(prompt)
    print("Enter in one of the formats: {}".format(allowed_fmts_str))
    if len(allowed_time_fmts) > 1:
        print("Any omitted parts will be set to 0 or 1, as appropriate")

    if emptycancel:
        print("Entering nothing will cancel")

    if currentvalue is not None:
        print("Current value is {0}".format(currentvalue))

    while True:
        userdate = text_input("--> ")
        userdate = userdate.strip()
        if len(userdate) == 0:
            if emptycancel:
                return None
            else:
                print("You must enter a value")
                continue

        matching_fmt = None
        for fmt in allowed_time_fmts:
            if len(userdate) == len(_human_readable_time_format(fmt)):
                matching_fmt = fmt
                break

        if matching_fmt is None:
            print('Wrong number of characters. Allowed formats are: {}'.format(allowed_fmts_str))
            continue

        try:
            dateout = dt.datetime.strptime(userdate, matching_fmt)
        except ValueError:
            print('Cannot understand "{}" as "{}"'.format(userdate, matching_fmt))

        # If we get here, nothing went wrong
        return dateout


def _human_readable_time_format(fmt):
    """Converts strptime format string into something a little more human readable

    :param fmt: the strptime format string
    :type fmt: str
    :return: the human-readable string
    """
    translation_dict = {'%Y': 'yyyy', '%m': 'mm', '%d': 'dd', '%H': 'HH', '%M': 'MM', '%S': 'SS'}
    for k, v in translation_dict.items():
        fmt = fmt.replace(k, v)
    return fmt


def user_input_value(prompt, testfxn=None, testmsg=None, currval=None,
                     returntype=str, emptycancel=True):
    """Ask the user to input a value.

    :param prompt: The prompt to give the user
    :type prompt: str

    :param testfxn: optional, if given, should be a function that returns a boolean value.
        Used to test if the value the user gave is valid. This can be a pre-defined function
        or one created using the lambda syntax. This will be called after the user input is
        converted to the returntype given (see below)
    :type testfxn: function

    :param testmsg: optional, if given, should be a message that describes the conditions
        required by testfxn. If testfxn is given, this really should be as well, or the user
        will just see "That is not an allowed value", which isn't very helpful.
    :type testmsg: str

    :param currval: optional, the current value of the option. If given, the value will
        be printed after the prompt

    :param returntype: optional, must be a type which can be used as a function to convert
        a string to that type, e.g. int, bool, float, list. If the type is bool, this function
        will require the user to enter T or F (or nothing if emptycancel is True). If not given,
        the user input will be returned as a string.
    :type returntype: str

    :param emptycancel: optional, defaults to True. If True, then the user
        can enter an empty string, which will make this function return None.
    :type emptycancel: bool

    :return: The user input value as the type specified by returntype, or None if emptycancel
        is True and the user does not enter a value.
    """

    if type(prompt) is not str:
        UIErrorWrapper.raise_error(UITypeError("prompt must be a string"))
    if testfxn is not None and not isinstance(testfxn, type(lambda: 0)):
        # There does not seem to be a "function" type like there is an int or float type
        # so we'll just compare vs a simple lambda function. This should return true for
        # a lambda function or a defined function.
        UIErrorWrapper.raise_error(UITypeError("testfxn must be a function"))
    if testmsg is not None and type(testmsg) is not str:
        UIErrorWrapper.raise_error(UITypeError("testmsg must be a string"))
    if testmsg is None and testfxn is not None:
        UIErrorWrapper.warn("If you specify a testfxn but no testmsg it will not be clear to the user what is wrong")
    if type(emptycancel) is not bool:
        UIErrorWrapper.raise_error(UITypeError("If given, emptycancel must be a bool"))

    if testfxn is None:
        testfxn = lambda value: True
    if testmsg is None:
        testmsg = 'That is not an allowed value'

    print(prompt)
    if currval is not None:
        print("The current value is {0}".format(currval))

    while True:
        if returntype is bool:
            userans = text_input("T/F: ").lower().strip()
            if userans == "t":
                return True
            elif userans == "f":
                return False
            elif len(userans) == 0:
                return None
            else:
                print("Option is a boolean. Must enter T or F.")
        else:
            userans = text_input("--> ").strip()
            if len(userans) == 0 and emptycancel:
                return None
            elif len(userans) == 0 and not emptycancel:
                print("Cannot enter an empty value.")
            else:
                try:
                    userans = returntype(userans)
                except ValueError:
                    print("Could not convert your input to {0}, try again".format(returntype.__name__))
                else:
                    if testfxn(userans):
                        return userans
                    else:
                        print(testmsg)


def user_input_yn(prompt, default="y"):
    """Prompts the user with a yes/no question, returns True if answer is yes, False if answer is no.

    This is similar to user_input_value with a bool
    return type, but handles it differently if the user does not enter a
    value; this function will return the default value rather than a None type
    or forcing the user to enter something

    :param prompt: The prompt string that the user should be shown
    :type prompt: str
    :param default: optional, must be either the string "y" or "n". Sets the
        default answer.
    :type default: bool
    :return: bool
    """

    if type(prompt) is not str:
        UIErrorWrapper.raise_error(UITypeError("prompt must be a string"))
    if type(default) is not str or default not in "YyNn":
        UIErrorWrapper.raise_error(UITypeError("default must be the string 'y' or 'n'"))

    while True:
        if default in "Yy":
            defstr = " [y]/n"
            defaultans = True
        else:
            defstr = " y/[n]"
            defaultans = False
        userans = text_input(prompt + defstr + ": ")

        if userans == "":
            return defaultans
        elif userans.lower() == "y":
            return True
        elif userans.lower() == "n":
            return False
        else:
            print("Enter y or n only. ", end="")


def user_onoff_list(prompt, options, currentstate=None, feedback_level=2, returntype="opts", printcols=True, **printcolargs):
    """Provides a list of toggleable options to the user

    Will print the prompt followed by the list of options provided. The user
    can interactively toggle each option on or off.

    :param prompt: A string prompting the user what to do. Will be followed
        by further instructions on what user inputs are valid.
    :type prompt: str

    :param options: A list or tuple of strings of the option names
    :type options: list or tuple

    :param currentstate: optional, describe the current state of the options (on or off).
        If not given, all default to False. Must be the same length as options. Is shallow
        copied internally so it will not change the values in the calling function.
    :type currentstate: list of bools

    :param feedback_level: optional, an integer describing how much feedback
        to give the user. Defaults to 2, meaning that this function will print
        out what user input it could not parse. Set to 0 to turn this off (1
        reserved against future intermediate levels of feedback).
    :type feedback_level: int

    :param returntype: optional, a string determining what is returned. Default is "opts",
        which returns a list of the subset of options selected. May also be "bools", meaning
        that a list of booleans the same length as options is returned, True for what options
        the user selected.
    :type returntype: str

    :param printcols: optional, controls whether the individual options should be spread out
        across the terminal in columns (``True``) or all printed in one column (``False``).
    :type printcols: bool

    :param printcolargs: keyword arguments to be passed through to :py:func:`textui.uiutils.print_in_columns`. Only has
        an effect if ``printcols`` is ``True``.

    :return: a list of options selected (returntype == "opts"), or a list of bools with the new
        states of the options (returntype == "bools"), or None if the user cancels.
    """
    if type(prompt) is not str:
        UIErrorWrapper.raise_error(UITypeError("prompt must be a string"))
    if type(options) is not list and type(options) is not tuple:
        UIErrorWrapper.raise_error(UITypeError("options must be a list or tuple"))
    elif not all([type(x) is str for x in options]):
        UIErrorWrapper.raise_error(UITypeError("options must be a list or tuple of strings"))
    if currentstate is None:
        currentstate = [False]*len(options)
    elif type(currentstate) is not list or not all([type(x) is bool for x in currentstate]):
        UIErrorWrapper.raise_error(UITypeError("currentstate must be a list of bools, if given"))
    elif len(currentstate) != len(options):
        UIErrorWrapper.raise_error(UIValueError("currentstate must be the same length as options, if given"))
    else:
        # Do not allow this function to modify the state in the calling workspace
        currentstate = copy.copy(currentstate)

    prompt += "\nEnter the number or multiple numbers separated by a space to toggle,\n" \
        "'a' or 'all' to toggle all, 'on' to set all on, 'off' to set all off,\n" \
        "'r' to accept and return, or 'c' to cancel and return.\n" \
        "Active options are marked with a *:"

    print(prompt)
    while True:
        entries = []
        for i in range(len(options)):
            if currentstate[i]:
                state_str = "[*]"
            else:
                state_str = "[ ]"
            entries.append("{0}: {1} {2}".format(i+1, options[i], state_str))

        if printcols:
            print_in_columns(entries, **printcolargs)
        else:
            print('\n'.join(entries))

        user_ans = text_input("(Type 'm' to see initial message again) --> ")
        opt_inds = []
        bad_opts = []
        if user_ans.lower() == "m":
            print("")
            print(prompt)
            continue
        elif user_ans.lower() == "r":
            if returntype == "bools":
                return currentstate
            elif returntype == "opts":
                return [opt for i, opt in enumerate(options) if currentstate[i]]
            else:
                UIErrorWrapper.raise_error(NotImplementedError('No return method implemented for returntype == "{}"'.format(returntype)))
        elif user_ans.lower() == "c":
            return None
        elif user_ans.lower() == "all" or user_ans.lower() == "a":
            # Python3 range compatible
            opt_inds = range(len(options))
        elif user_ans.lower() == "on":
            opt_inds = [i for i in range(len(options)) if not currentstate[i]]
        elif user_ans.lower() == "off":
            opt_inds = [i for i in range(len(options)) if currentstate[i]]
        else:
            user_ans = re.split("\s+", user_ans)
            for u_part in user_ans:
                try:
                    u_list = [int(u)-1 for u in u_part.split('-')]
                except ValueError as err:
                    # If the input cannot be parsed as an int, move on
                    bad_opts.append(u_part)
                else:
                    if len(u_list) == 1:
                        opt = u_list
                    else:
                        opt = [x for x in range(u_list[0], u_list[1] + 1)]

                    if all([o >= 0 and o < len(options) for o in opt]):
                        opt_inds += opt
                    else:
                        bad_opts.append(u_part)

        if feedback_level > 1 and len(bad_opts) > 0:
            print("Could not parse {0},\n"
                  "out of range or not a number".format(", ".join(bad_opts)))

        for i in opt_inds:
            currentstate[i] = not currentstate[i]


def _optional_input(user_input_fxn, prompt, value, do_ask_fxn, input_valid_fxn, input_invalid_msg, *args, **kwargs):
    """
    Internal function that maintains the functionality common to all the opt_* functions.
    :return:
    """
    if do_ask_fxn(value):
        return user_input_fxn(prompt, *args, **kwargs)
    elif not input_valid_fxn(value):
        UIErrorWrapper.raise_error(UIValueError(input_invalid_msg.format(value=value)))
    else:
        return value


def _get_do_ask_fxn(ask_fxn):
    def _default_do_ask_fxn(value):
        return value is None

    if ask_fxn is None:
        return _default_do_ask_fxn
    else:
        return ask_fxn


def opt_user_input_list(prompt, value, options, do_ask_test=None, invalid_msg=None, error_on_none=True, **kwargs):
    """
    Wrapper around user_input_list that calls it only if an interactive choice is necessary.

    This function takes mostly the same arguments as user_input_list, but in addition takes an existing value and
    tests if that value indicates that a choice needs to be made, or if not, that it is a valid option. Typically,
    this would be used inside a function that has optional arguments that, if not given, should be asked interactively
    of the user.

    :param prompt: A string that is the prompt that will be given if the user needs to make an interactive choice
    :type prompt: str

    :param value: the current value that will be tested if it means the user should be asked to choose an option or
        if it is valid

    :param options: a list of allowed options, passed to user_input_list if needed.
    :type options: list

    :param do_ask_test: optional, a function that should take one input (value) and return True if user_input_list
        should be called to ask the user what value to use. By default, tests if value is None (i.e. will call
        user_input_list if value is None).
    :type do_ask_test: function

    :param invalid_msg: optional, the message for the UIValueError raised if user_input_list is not called but value
        is not in the options list. This can have two formatting markers, {value} and {opts}. {value} will be replaced
        with the value given, {opts} will be replaced with a comma separated list of allowed options.
    :type invalid_msg: str

    :param error_on_none: optional, default True, meaning that if the user fails to provide a value, a UIOptNoneError
        is raised.
    :type error_on_none: bool

    :param kwargs: additional keyword arguments recognized by user_input_list.

    :return: the value selected, or the value given if user_input_list is not called. Raises a ValueError if value
        is not in options and user_input_list is not called.
    """

    do_ask_test = _get_do_ask_fxn(do_ask_test)

    input_valid_fxn = lambda value: value in options
    if invalid_msg is None:
        invalid_msg = 'The value {{value}} is invalid. It must be one of: {opts}'.format(opts=', '.join(options))
    else:
        invalid_msg = invalid_msg.format(value='{value}', opts=', '.join(options))

    response = _optional_input(user_input_list, prompt, value, do_ask_test, input_valid_fxn, invalid_msg, options, **kwargs)

    if response is None and error_on_none:
        UIErrorWrapper.raise_error(UIOptNoneError('The user failed to provide a value'))

    if 'returntype' in kwargs and kwargs['returntype'] == 'index' and response in options:
        response = options.index(response)

    return response


def opt_user_input_date(prompt, value, do_ask_test=None, is_valid_test=None, invalid_msg=None, error_on_none=True, **kwargs):
    """
    Wrapper around user_input_date that calls it only if an interactive input is necessary.

    :param prompt: A string that is the prompt that will be given if the user needs enter a date
    :type prompt: str

    :param value: the current value of the date.

    :param do_ask_test: optional, a function that should take one input (value) and return True if user_input_date
        should be called to ask the user what value to use. By default, tests if value is None (i.e. will call
        user_input_date if value is None).
    :type do_ask_test: function

    :param is_valid_test: optional, if given, it must be a function that takes one input (value) and returns a boolean
        indicating if value is valid. By default, this checks that value is an instance of datetime.date or datetime.datetime.
    :type is_valid_test: function

    :param invalid_msg: optional, the error message that will be given in is_valid_test(value) returns False.
        If is_valid_test is given, this must also be given.
    :type invalid_msg: str

    :param error_on_none: optional, default True, meaning that if the user fails to provide a value, a UIOptNoneError
        is raised.
    :type error_on_none: bool

    :param kwargs: additional keyword arguments to pass through to user_input_date.

    :return: the date, either given as value or chosen by the user.
    """
    do_ask_test = _get_do_ask_fxn(do_ask_test)
    if is_valid_test is None:
        is_valid_test = lambda value: isinstance(value, (dt.date, dt.datetime))
    elif is_valid_test is not None and invalid_msg is None:
        UIErrorWrapper.raise_error(UIValueError('If is_valid_test is given, invalid_msg should be to so that the error '
                                                'message matches the test'))
    elif invalid_msg is None:
        invalid_msg = 'The given value must be an instance of datetime.date or datetime.datetime' if invalid_msg is None else invalid_msg

    response = _optional_input(user_input_date, prompt, value, do_ask_test, is_valid_test, invalid_msg, **kwargs)
    if response is None and error_on_none:
        UIErrorWrapper.raise_error(UIOptNoneError('The user failed to provide a value'))

    return response


def opt_user_input_value(prompt, value, do_ask_test=None, is_valid_test=None, invalid_msg=None, error_on_none=True, **kwargs):
    """
    Wrapper around user_input_value that calls it only if an interactive input is necessary

    :param prompt: A string that is the prompt that will be given if the user needs enter a value
    :type prompt: str

    :param value: the current value

    :param do_ask_test: optional, a function that should take one input (value) and return True if user_input_value
        should be called to ask the user what value to use. By default, tests if value is None (i.e. will call
        user_input_value if value is None).
    :type do_ask_test: function

    :param is_valid_test: optional, if given, it must be a function that takes one input (value) and returns a boolean
        indicating if value is valid. If not given, no check of the value will be done. This will also be passed through to
        user_input_value as testfxn, ensuring that the criteria for the given value is the same in both.
    :type is_valid_test: function

    :param invalid_msg: optional, the error message that will be given in is_valid_test(value) returns False.
        If is_valid_test is given, this must also be given. This will be passed through to user_input_valid as testmsg
        so that the error message is consistent.
    :type invalid_msg: str

    :param kwargs: additional keyword arguments to pass through to user_input_value, except testfxn and testmsg,
        which are already handled by is_valid_test and invalid_msg, respectively.

    :param error_on_none: optional, default True, meaning that if the user fails to provide a value, a UIOptNoneError
        is raised.
    :type error_on_none: bool

    :return: the value, either input as value or entered by the user.
    """
    do_ask_test = _get_do_ask_fxn(do_ask_test)
    if is_valid_test is not None and invalid_msg is None:
        UIErrorWrapper.raise_error(UIValueError('If is_valid_test is given, invalid_msg must be as well'))
    elif is_valid_test is None:
        is_valid_test = lambda val: True

    # Explicitly make testfxn and testmsg for user_input_value the same as the valid test and message used by this
    # function
    response = _optional_input(user_input_value, prompt, value, do_ask_test, is_valid_test, invalid_msg,
                           testfxn=is_valid_test, testmsg=invalid_msg, **kwargs)
    if response is None and error_on_none:
        UIErrorWrapper.raise_error(UIOptNoneError('The user failed to provide a value'))

    return response


def opt_user_input_yn(prompt, value, do_ask_test=None, **kwargs):
    """
    Wrapper around user_input_yn that calls it only if an interactive choice is required.

    :param prompt: A string that is the prompt that will be given if the user needs to choose interactively
    :type prompt: str

    :param value: the current value. If it does not pass do_ask_test and is not a boolean, an error will be raised

    :param do_ask_test: optional, a function that should take one input (value) and return True if user_input_yn
        should be called to ask the user what value to use. By default, tests if value is None (i.e. will call
        user_input_yn if value is None).
    :type do_ask_test: function

    :param kwargs: additional keyword arguments to pass through to user_input_yn

    :return: the value, either input as value or chosen by the user.
    """
    do_ask_test = _get_do_ask_fxn(do_ask_test)
    invalid_msg = 'The given value must be a boolean'
    return _optional_input(user_input_yn, prompt, value, do_ask_test, lambda x: isinstance(x, bool), invalid_msg, **kwargs)


def opt_user_onoff_list(prompt, value, options, do_ask_test=None, returntype='opts', value_name='The value', **kwargs):
    """
    Wrapper around user_onoff_list that calls it only if an interactive choice is required.

    :param prompt: A string that is the prompt that will be given if the user needs to choose interactively
    :type prompt: str

    :param value: the current value. If this does not pass do_ask_test, then it must be a list or tuple, of what depends
        on returntype

    :param options: the list of options to choose from.
    :type options: list

    :param do_ask_test: optional, a function that should take one input (value) and return True if user_onoff_list
        should be called to ask the user what value to use. By default, tests if value is None (i.e. will call
        user_onoff_list if value is None).
    :type do_ask_test: function

    :param returntype: optional, either the string "opts" or "bools". The default is "opts", which is the reverse of
        user_onoff_list; it is assumed that this function is more likely to be used if a list of options is more likely to
        be passed as an argument than a list of booleans.
    :type returntype: str

    :param value_name: optional, but recommended: this will be inserted into the error message raised if value does not
        pass do_ask_test and is not the right format for the value of returntype as the name of the parameter that is wrong.
        Otherwise, it just say "The value", which isn't very informative for your user.
    :type value_name: str

    :param kwargs: additional keyword arguments to pass through to user_onoff_list, except returntype, which
        is already passed automatically.

    :return: either a list of booleans the same length as options or a list of the subset of options selected,
        depending on the value of returntype. Will either be the input value, or the user's choice.
    """
    do_ask_test = _get_do_ask_fxn(do_ask_test)

    def opt_valid_test(val):
        if not isinstance(val, (list, tuple)):
            return False
        else:
            return all([v in options for v in val])

    def bool_valid_test(val):
        if not isinstance(val, (list, tuple)):
            return False
        else:
            return all([isinstance(v, bool) for v in val]) and len(val) == len(options)

    if returntype == 'opts':
        is_valid_test = opt_valid_test
        invalid_message = '{} must be a list or tuple containing a subset of the following: {}'.format(
            value_name, ', '.join(options)
        )
    elif returntype == 'bools':
        is_valid_test = bool_valid_test
        invalid_message = '{} must be a list or tuple of booleans the same length as options ({})'.format(value_name, len(options))
    else:
        UIErrorWrapper.raise_error(ValueError('returntype == "{}" is not permitted'.format(returntype)))

    return _optional_input(user_onoff_list, prompt, value, do_ask_test, is_valid_test, invalid_message, options, **kwargs)
