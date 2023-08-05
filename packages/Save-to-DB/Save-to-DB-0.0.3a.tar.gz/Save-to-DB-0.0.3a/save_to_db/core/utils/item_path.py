from functools import wraps
from ..exceptions.item_field import CircularReferenceError



def item_path_decorator(func):
    """ A decorator that's used to decorate item methods that except
    `_item_path` argument in order to detect circular references.
    
    `_item_path` is a list that adds item in the beginning of a methods and
    then removes the item from the list. The list is being passed to the same
    method when dealing with referenced items. If an item already in the list
    at the beginning then it means that circular reference has occurred and
    :py:class:`~save_to_db.core.exceptions.item_field.CircularReferenceError`
    is raised.
    """
    
    @wraps(func)
    def decorated(self, *args, _item_path=None, **kwargs):
        if _item_path is None:
            _item_path = []
        if self in _item_path:
            raise CircularReferenceError(self)
        _item_path.append(self)
        
        result = func(self, *args, _item_path=_item_path, **kwargs)
        _item_path.pop()
        return result
    
    return decorated