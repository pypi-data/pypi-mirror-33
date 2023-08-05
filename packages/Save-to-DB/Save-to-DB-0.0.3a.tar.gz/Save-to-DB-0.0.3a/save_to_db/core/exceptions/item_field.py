""" This module contains exceptions for
:py:class:`~save_to_db.core.item_base.ItemBase` related to fields usage.
"""


class ItemFieldError(ValueError):
    """ General exception for :py:class:`~save_to_db.core.item_base.ItemBase`
    field usage.
    """


class CircularReferenceError(ItemFieldError):
    """ Raised when there is a circular reference among items. """
