
class ItemClsManager(object):
    """ This class manages all known item classes
    (see :py:class:`~.item.Item` base class). Normally only one instance of
    this class is used.
    
    :param autogenerate: If `True` then getting a missing item by model class
        will generate a new item class with all parameters auto configured.
    """
    
    def __init__(self, autogenerate=False):
        self._registry = set()
        self.autogenerate = autogenerate
    
    
    def register(self, *item_classes):
        """ Adds an item class to the registry.
        
        :param \*item_classes: List of subclasses of :py:class:`~.item.Item`
            class to add to the registry.
        """
        self._registry.update(item_classes)
        
        
    def unregister(self, *item_classes):
        """ Removes an item class from the registry.
        
        :param \*item_classes: List of subclasses of :py:class:`~.item.Item`
            class to remove form the registry.
        """
        self._registry -= set(item_classes)
    
    
    def clear(self):
        """ Removes all items from the registry. """
        self._registry.clear()
    
    
    def get_by_path(self, path, relative_to=None):
        """ Gets item classes using `path` (module path and class name separated
        by dot).
        
        :param path: Item path. Multiple initial dots allowed, e.g.
            `'...some_module.SomeClass'`.
        :param relative_to: In case `path` argument is relative, this arguments
            contains a path it is relative to.
        :return: List of item classes.
        """
        
        result = []
        # if path is relative or just a class name
        if path.startswith('.') or '.' not in path:
            
            if path.startswith('.'):
                if relative_to is None:
                    raise Exception('Relative path not allowed without setting '
                                    '`relative_to` argument.')
                stripped_path = path.lstrip('.')
                dot_count = len(path) - len(stripped_path)
                if dot_count > 1:
                    path_parts = relative_to.split('.')[:-(dot_count-1)]
                    relative_to = '.'.join(path_parts)
            else:
                stripped_path = path
            
            if relative_to:
                path = '{}.{}'.format(relative_to, stripped_path)      
        
        search_by_name = '.' not in path
        for item_cls in self._registry:
            # by name
            if search_by_name:
                if item_cls.__name__ == path:
                    result.append(item_cls)
                    continue
            
            # by path
            item_path = '{}.{}'.format(item_cls.__module__,
                                       item_cls.__name__)
            if item_path == path:
                result.append(item_cls)
                
        return result
    
    
    def __autogenerate_item_cls(self, model_cls):
        from .item import Item  # circular reference
        
        return Item._Auto(model_cls, metadata={
                    'autogenerated_item_cls': True,
                })
    
    
    def get_by_model_cls(self, model_cls):
        """ Gets item classes using ORM model class.
        
        :param model_cls: An ORM model class that an item is using to persist
            data.
        :return: List of item classes.
        """
        result = []
        for item_cls in self._registry:
            if item_cls.model_cls is model_cls:
                result.append(item_cls)
        
        if not result and self.autogenerate:
            result.append(self.__autogenerate_item_cls(model_cls))
        return result
    
    
    def autocomplete_item_classes(self):
        """ If `self.autogenerate` is `True` then auto generates missing item
        classes for models classes that are needed for already registered item
        classes via relations.
        """
        if not self.autogenerate:
            return
        
        # generating all missing items
        while True:
            regestry_copy = self._registry.copy()
            for item_cls in regestry_copy:
                item_cls.complete_setup()
                for relation in item_cls.relations.values():
                    relation['item_cls'].complete_setup()
            if regestry_copy == self._registry:
                break
            
        
    def __repr__(self):
        return '<{}()>'.format(self.__class__.__name__)


#: normally only this instance of :py:class:`~ItemClsManager` is used.
item_cls_manager = ItemClsManager()
