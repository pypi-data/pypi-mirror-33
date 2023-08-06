from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# If comparing to the int type becomes a compatibility issue, try this. Requires installing the builtins package for
# Python 2 (http://python-future.org/compatible_idioms.html)
# from builtins import int

from .uierrors import UIValueError, UITypeError, UICallbackError, UIErrorWrapper
from .uielements import user_input_date, user_input_value, user_input_list, user_input_yn, user_onoff_list

class _MenuItem(object):
    def __init__(self, name_in, callback_in):
        self.name = name_in
        # This should be an instance of _CallBack
        self.callback = callback_in

class _CallBack(object):
    def __init__(self, fxn, parent_menu, *args):
        self.return_fxn = fxn
        self.parent = parent_menu
        self.extra_fxns = args

    def execute(self):
        for fxn in self.extra_fxns:
            fxn()
        return self.return_fxn()

    def get_menu_hierarchy(self):
        hierarchy = []
        next_menu = self.parent
        while next_menu is not None:
            hierarchy.insert(0, next_menu.name)

        return hierarchy


class Program(object):
    def __init__(self, main_menu):
        if type(main_menu) is not Menu:
            UIErrorWrapper.raise_error(UITypeError("main_menu must be an instance of Menu"))
        self.next_callback = _CallBack(main_menu.interact, None)
        self.main_loop()

    def main_loop(self):
        while True:
            new_callback = self.next_callback.execute()
            if type(new_callback) is not _CallBack:
                UIErrorWrapper.raise_error(UICallbackError(self.next_callback))
            else:
                self.next_callback = new_callback


class Menu(object):
    def __init__(self, menu_name, parent_in=None):
        self.name = menu_name
        self.parent = parent_in
        # If we are the child of another menu, then the final option
        # in the menu should be to go up one level. If we are the
        # top menu, then it should be to quit.
        self.menu_items = []
        if self.parent is None:
            self._add_item("Quit", self._quit_program)
        else:
            self._add_item("Up one level", self._up_one_level)

    def interact(self):
        ind = user_input_list("=== {0} ===".format(self.name),
                              self.__item_names(),
                              returntype="index")
        return self.menu_items[ind].callback

    def _add_item(self, name, callback):
        """
        _add_item is the internal method call used to add a menu item to this Menu.
        Using this in typical menu building is not recommended because it REQUIRES that
        your callback function return an instance of _Callback when it completes. This
        can add some flexibility (if you want to have a function go somewhere else than the
        calling Menu when it finishes) but requires you to take responsibility for that.
        :param name: the name of the menu item, as a string
        :param callback: a function which returns an instance of _Callback
        :return: none
        """
        if type(name) is not str:
            UIErrorWrapper.raise_error(UITypeError("name must be a string"))
        if not callable(callback) and not isinstance(callback, _CallBack):
            UIErrorWrapper.raise_error(UITypeError("callback must be a function or an instance of textui.uibuilder.Callback"))

        if isinstance(callback, _CallBack):
            callback_inst = callback
        else:
            callback_inst = _CallBack(callback, self)
        item = _MenuItem(name, callback_inst)
        # The new item will be next to last (quit or go up one level is always last)
        self.menu_items.insert(-1, item)

    def add_submenu(self, submenu_title, menu_item_name=None):
        """
        add_submenu creates a new instance of Menu with this Menu as the parent,
        adds it as the next-to-last option in this Menu, and returns the new instance of Menu.
        :param submenu_title: The title of the submenu, passed as the first argument to Menu()
        :param menu_item_name: optional, if given, will be used as the item name in the current
        menu, if not given, the submenu_title is used both as the menu title and the item name
        :return: instance of Menu
        """
        if not isinstance(submenu_title, str):
            UIErrorWrapper.raise_error("submenu_title must be a string")

        if menu_item_name is None:
            menu_item_name = submenu_title
        elif not isinstance(menu_item_name, str):
            UIErrorWrapper.raise_error("menu_item_name must be a string, if given")

        smenu = Menu(submenu_title, self)
        self._add_item(menu_item_name, smenu.interact)
        return smenu

    def attach_submenu(self, submenu, menu_item_name=None):
        """
        attach_submenu takes an existing instance of Menu and binds it as an option in this Menu.
        :param submenu: the Menu to attach to the current menu
        :param menu_item_name: if given, overrides the name used in the options list of this menu.
        If not given, the menu item is given the value of submenu.name
        :return: none
        """
        if not isinstance(submenu, Menu):
            UIErrorWrapper.raise_error(TypeError('submenu must be an instance of textui.uibuilder.Menu'))
        if menu_item_name is None:
            menu_item_name = submenu.name
        elif not isinstance(menu_item_name, str):
            UIErrorWrapper.raise_error(TypeError('menu_item_name must be a string'))

        if submenu.parent is not None:
            UIErrorWrapper.warn('While attaching menu "{0}" to "{1}": {0} already has a parent which will be overwritten'
                                .format(submenu.name, self.name))
        submenu.parent = self
        self._add_item(menu_item_name, submenu.interact)

    def attach_custom_fxn(self, menu_item_name, callback_fxn):
        """
        attach_custom_fxn is the usual way to add functions that actually DO SOMETHING to a menu,
        rather than adding a submenu.
        :param menu_item_name: the name that the item should have in the Menu, as a string
        :param callback_fxn: the function that should execute when this menu item is selected,
        it must require no arguments and return nothing.
        :return: none
        """
        if not isinstance(menu_item_name, str):
            UIErrorWrapper.raise_error(TypeError('menu_item_name must be a string'))
        if not callable(callback_fxn):
            UIErrorWrapper.raise_error(TypeError('callback_fxn must be a function'))

        self._add_item(menu_item_name, _CallBack(self.interact, self, callback_fxn))

    def __item_names(self):
        return [item.name for item in self.menu_items]

    def _up_one_level(self):
        return _CallBack(self.parent.interact, self)

    def _quit_program(self):
        exit(0)