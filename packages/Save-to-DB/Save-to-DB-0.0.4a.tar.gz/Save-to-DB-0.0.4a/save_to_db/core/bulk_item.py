from copy import copy
from .item import ItemBase
from .utils.item_path import item_path_decorator



class BulkItem(ItemBase):
    """ This class deals with instances of :py:class:`~.item.Item` in chunks.
    It can create or update multiple database rows using single query, e.g. it
    can persist multiple items at once.
    
    :param item_cls: A subclass of :py:class:`~.item.Item` that
        this class deals with.
    :param \*\*kwargs: Values that will be saved as **default** item data.
    """
    
    #--- special methods -------------------------------------------------------
    
    def __init__(self, item_cls, **kwargs):
        self.item_cls = item_cls
        self.bulk = []
        
        self.data = {}
        for key, value in kwargs.items():
            self[key] = value  # this will trigger `__setitem__` function
        
    
    def __setitem__(self, key, value):
        real_key = self.item_cls._get_real_keys(key, as_string=True)
        self.data[real_key] = value
        
    
    def __getitem__(self, key):
        real_keys = self.item_cls._get_real_keys(key)
        return self._get_direct(real_keys)
    
    
    def _get_direct(self, real_keys):
        real_key = '__'.join(real_keys)
        if real_key in self.data:
            return self.data[real_key]
        
        item_cls = self.item_cls
        for real_key in real_keys:
            if real_key in item_cls.relations:
                item_cls = item_cls.relations[real_key]['item_cls']
            else:
                raise KeyError(real_key)
        
        self.data[real_key] = item_cls.__genitem(real_keys[-1])
        return self.data[real_key]
    
    
    def __delitem__(self, key):
        real_key = self.item_cls._get_real_keys(key, as_string=True)
        del self.data[real_key]
    
    
    def __contains__(self, key):
        try:
            real_keys = self.item_cls._get_real_keys(key)
        except KeyError:
            return False
        return self._contains_direct(real_keys)
    
    
    def _contains_direct(self, real_keys):
        return '__'.join(real_keys) in self.data
    
    
    def slice(self, start=0, stop=None, step=1):
        """ Returns copy of the bulk item with only certain items.
        
        :param start: Index of the first item (inclusive) in the bulk to add to
            the new bulk.
        :param stop: Index of the last item (not inclusive) in the bulk to add
            to the new bulk.
        :param step: Specifies by how much to increment index each time
            when moving from `start` to `stop`.
        """
        if stop is None:
            stop = len(self.bulk)
        new_bulk = self.item_cls.Bulk()
        new_bulk.data = copy(self.data)
        new_bulk.add(*self.bulk[start:stop:step])
        
        return new_bulk
    
    
    #--- utility methods -------------------------------------------------------
    
    def to_dict(self):
        return self._to_dict()
        
        
    @item_path_decorator
    def _to_dict(self, _item_path=None):
        dict_items = []
        for item in self.bulk:
            dict_wrapper = item._to_dict(_item_path=_item_path)
            dict_items.append(dict_wrapper)
        
        defaults = {}
        for key, value in self.data.items():
            if not isinstance(value, ItemBase):
                defaults[key] = value
            else:
                defaults[key] = value._to_dict(_item_path=_item_path)
        
        result = {
            'defaults': defaults,
            'bulk': dict_items,
        }
        
        return result
    
    
    def load_dict(self, data):
        # defaults
        for key, value in data['defaults'].items():
            # getting relation class
            cur_cls = self.item_cls
            for cur_key in key.split('__'):
                if cur_key in cur_cls.relations:
                    cur_cls = cur_cls.relations[cur_key]['item_cls']
                else:
                    cur_cls = None
                    break
            if cur_cls:  # relation
                self[key] = cur_cls().load_dict(value)
            else:
                self[key] = value
        
        # bulk
        for dict_wrapper in data['bulk']:
            self.add(self.item_cls().load_dict(dict_wrapper))
        
        return self
    
    
    #--- properties ------------------------------------------------------------
    
    @property
    def model_cls(self):
        """ Property that returns `model_cls` attribute of the `item_cls`
        class.
        """
        return self.item_cls.model_cls
    
    
    #--- main methods ----------------------------------------------------------
    
    def add(self, *items):
        """ Adds `item` to the bulk.
        
        :param \*item: List of instances of :py:class:`~.item_base.ItemBase`
            class to be added to the bulk.
        """
        for item in items:
            if item not in self.bulk:
                self.bulk.append(item)
    
    
    def gen(self, *args, **kwargs):
        """ Creates a :py:class:`~.item.Item` instance and adds it to the bulk.
        
        :param \*args: Positional arguments that are passed to the item
            constructor.
        :param \*\*kwargs: Keyword arguments that are passed to the item
            constructor.
        :returns: :py:class:`~.item.Item` instance.
        """
        item = self.item_cls(*args, **kwargs)
        self.add(item)
        return item
    
    
    def remove(self, *items):
        """ Removes `item` from the bulk.
        
        :param \*items: List of instances of :py:class:`~.item_base.ItemBase`
            class to be removed from the bulk.
        """
        for item in items:
            if item in self.bulk:
                self.bulk.remove(item)
    
    
    def as_list(self):
        return self.bulk
    
    
    def is_single_item(self):
        return False
    
    
    def is_bulk_item(self):
        return True
    
    
    def process(self):
        """ Converts all set values to proper data types and sets default values
        to all items in the bulk.
        """
        return self._process()
    
    
    @item_path_decorator
    def _process(self, _item_path=None):
        for key, value in self.data.items():
            if not isinstance(value, ItemBase):
                self.data[key] = self.item_cls.process_field(key, value,
                                                             aliased=False)
            else:
                self.data[key]._process(_item_path=_item_path)

            for item in self.bulk:
                if key not in item:
                    item[key] = self.data[key]
        
        for item in self.bulk:
            item._process(_item_path=_item_path)
        

        
        