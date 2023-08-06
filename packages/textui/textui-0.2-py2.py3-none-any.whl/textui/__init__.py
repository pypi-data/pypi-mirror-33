"""
textui: Python text UI, a text based user interface package

A note on error handling: many of the functions in this packages throw exceptions if
your input (not the user input) is of the wrong type. You may not wish such errors to
occur when the program is in use by the end user. There are several ways to handle this.

    1) Any UIErrors are not raised directly but via the UIErrorWrapper class in the
    submodule uierrors. This class can be set to do a "soft exit" when exceptions are
    raised, meaning that it will print a simple "internal error" message and exit. To
    enable this behavior, one would do this:

        from textui.uierrors import UIErrorWrapper
        UIErrorWrapper.do_soft_exit = True

    2) Any error deliberately thrown by one of these functions is a subclass of UIError
    contained in the uierrors submodule of textui. You could wrap any calls to this
    package in a try, except block checking for exceptions of the UIError type and
    use that to exit gracefully. This will not catch other, deeper Python exceptions.
    UIErrors itself derives from Exception, so you could also catch any exception and
    exit gracefully.

    3)  The UIErrorWrapper class has other class properties like do_soft_exit which

"""