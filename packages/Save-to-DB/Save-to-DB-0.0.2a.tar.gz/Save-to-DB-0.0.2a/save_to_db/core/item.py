import re
from datetime import date, datetime, time

from save_to_db.adapters.utils.column_type import ColumnType

from .item_base import ItemBase
from .item_metaclass import ItemMetaclass

from .bulk_item import BulkItem

from .utils.item_path import item_path_decorator


#: regex for preparing strings to be converted into numeric values
_number_regex = re.compile(r'[^0-9\.]')


class Item(ItemBase, metaclass=ItemMetaclass, no_setup=True):
    """ This class is used to collect data for a single item (possibly with
    foreign keys) and then create or update corresponding rows in a database.
    
    **To configure an item class use next class variables:**
    
    :cvar model_cls: Reference to an ORM model class.
    
    :cvar defaults: Dictionary with default field values. Value can be
        either raw value or a callable that accepts an item as an argument
        and returns field value.
          
        .. note::
            Currently values for relation fields not allowed.
        
    :cvar creators: List of groups (sets) of fields and
        relations, if all fields and relations from at least one group are
        set then an item can be created.
        
    :cvar getters: List of groups (sets) of fields and
        relations, if all fields and relations from at least one group are
        set then an item can be loaded from database.
        
        .. warning::
            `getters` cannot contain x-to-many relations.
    
    :cvar nullables: Set of fields which, if a value is not set in an
        item upon saving, must be set to null or, in case of x-to-many
        relationship, the value must be set to an empty list.
        
    :cvar relations:  dictionary describing foreign keys,
        example:
            
            .. code-block:: Python   
            
                relations = {
                    'one': {
                        'item_cls': ItemClassOne,
                        'replace_x_to_many': False,  # default value
                    }
                    'two': ItemClassTwo,  # if we only interested in class
                }
        
        Keys are the fields that reference other items (foreign key columns
        in database) and values are dictionaries with next keys and values:
          
            - 'item_cls' - item class used to create foreign key item;
            - 'replace_x_to_many' - Only applicable to x-to-many
              relationships. If `True` then saving item to
              database removes old values for the field from database.
              Default: `False`.
    
    :cvar conversions: Dictionary that describes how string values must be
        converted to proper data types. Default `conversions` value:
          
        .. code-block:: Python
          
            conversions = {
                'decimal_separator': '.',
                'boolean_true_strings': ('true', 'yes', 'on', '1', '+'),
                'boolean_false_strings': ('false', 'no', 'off', '0', '-'),
                # format for dates and times used as an argument for
                # `datetime.datetime` function
                'date': '%Y-%m-%d',
                'time': '%H:%M:%S',
                'datetime': '%Y-%m-%d %H:%M:%S',
            }
        
        In case of absence of a value from `conversions` dictionary default
        value will be used.
        
    :cvar allow_multi_update: If `True` then an instance of this class can
        update multiple models. Default: `False`.
        
        .. note::
            Can be overwritten on individual instances.
    """
    
    #--- special methods -------------------------------------------------------
    
    def __genitem(self, key):
        """ Generates an item for the given relation key.
        
        :param key: Relation key for which to create related item instance. 
        """
        relation = self.relations[key]
        if relation['relation_type'].is_x_to_many():
            item = relation['item_cls'].Bulk()
        else:
            item = relation['item_cls']()
        return item
    
    
    def __setitem__(self, key, value):
        if not self.is_valid_key(key):
            raise KeyError(key)
        
        if '__' not in key:
            self.data[key] = value
            return
        
        this_key, that_key = key.split('__', 1)
        if this_key not in self.data:
            self.data[this_key] = self.__genitem(this_key)
                
        self.data[this_key][that_key] = value
        
        
    def __getitem__(self, key):
        if not self.is_valid_key(key):
            raise KeyError(key)
        
        if '__' not in key:
            if key not in self.data:
                self.data[key] = self.__genitem(key)
            return self.data[key]
        else:
            this_key, that_key = key.split('__', 1)
            if this_key not in self.data:
                self.data[this_key] = self.__genitem(this_key)
                
            return self.data[this_key][that_key]
    
    
    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        
        item = self
        if '__' in key:
            this_key, that_key = key.split('__', 1)
            del item[this_key][that_key]
            return

        del item.data[key]
    
    
    def __contains__(self, key):
        if '__' not in key:
            return key in self.data
        
        this_key, that_key = key.split('__', 1)
        if this_key not in self.data:
            return False
        
        return that_key in self.data[this_key]
    
    
    def __iter__(self):
        for key in self.data.keys():
            yield key
    
    
    #--- utility methods -------------------------------------------------------
    
    def to_dict(self):
        return self._to_dict()
    
    
    @item_path_decorator
    def _to_dict(self, _item_path=None):
        result = {}
        for key, value in self.data.items():
            if not isinstance(value, ItemBase):
                result[key] = value
            else:
                result[key] = value._to_dict(_item_path=_item_path)
        return result
    
    
    def load_dict(self, data):
        for key, value in data.items():
            if key in self.fields:
                self[key] = value
            elif key in self.relations:
                self[key].load_dict(value)
        
        return self
    
    
    #--- main methods ----------------------------------------------------------
    
    
    def can_create(self, fkeys):
        """ Checks that a new row can be created in database for
        the item.
        
        .. note::
            For relations fields we check that it is in `fkeys`. For normal
            fields we just check that it is present and not `None`.
        
        :param fkeys: A `dict` where keys are relation field names and values
            are ORM models that were got form or created in database.
        :returns: `True` if a corresponding row for the item can be created in
            database, `False` otherwise.
        """
        if self.creators is None:
            return False
        if not self.creators:
            return True
        
        for group in self.creators:
            can_create = True
            for field_name in group:
                if field_name in self.relations:
                    if field_name not in fkeys:
                        can_create = False
                elif field_name not in self.data or \
                        self.data[field_name] is None:
                    can_create = False
                
            if can_create:
                return True
        return False
    
    
    @classmethod
    def is_valid_key(cls, key):
        """ Returns `True` if an instance of this class can have given
        `key` based on configuration.
        
        :param key: Fields name or field names separated by double underscores
            to reference relations.
        """
        cls.complete_setup()
        
        if '__' not in key:
            return key in cls.fields or key in cls.relations
        
        this_key, that_key = key.split('__', 1)
        if this_key not in cls.relations:
            return False
        
        return cls.relations[this_key]['item_cls'].is_valid_key(that_key)
    
    
    @staticmethod
    def _Auto(model_cls, **kwargs):
        """ Creates new item class.
        
        :param model_cls: model for witch new item class is generated.
        :param \*\*kwargs: key-word arguments that will be used as new class
            attributes.
        :returns: Newly created item class.
        """
        kwargs['model_cls'] = model_cls
        item_cls = type('{}Item'.format(model_cls.__name__),
                        (Item,), kwargs)
        return item_cls
        
    
    @classmethod
    def Bulk(cls, *args, **kwargs):
        """ Creates a :py:class:`~.bulk_item.BulkItem` instance for this item
        class.
        
        :param \*args: Positional arguments that are passed to bulk item
            constructor.
        :param \*\*kwargs: Keyword arguments that are passed to bulk item
            constructor.
        :returns: :py:class:`~.bulk_item.BulkItem` instance for this item class.
        """
        return BulkItem(cls, *args, **kwargs)
    
    
    def as_list(self):
        return [self]
    
    
    def is_single_item(self):
        return True
    
    
    def is_bulk_item(self):
        return False
    
    
    @classmethod
    def process_field(cls, key, value):
        """ Converts `value` to the appropriate data type for the given
        `key`.
        
        :param key: Key using which proper value type can be determined.
            This value can contain double underscores to reference relations.
        :returns: Value converted to proper type.
        """
        cls.complete_setup()
        
        if value is None:
            return None
        
        if '__' in key:
            this_key, that_key = key.split('__', 1)
            return cls.relations[this_key]['item_cls'].process_field(
                that_key, value)
        
        conversions = cls.conversions
        column_type = cls.fields[key]
        if column_type is ColumnType.BINARY:
            if not isinstance(value, bytes):
                if isinstance(value, str):
                    value = bytes(value, 'utf-8')
                else:
                    raise ValueError('Cannot convert to bytes: {}'.format(
                        value))
        elif column_type is ColumnType.BOOLEAN:
            if not isinstance(value, bool):
                if value.lower() in conversions['boolean_true_strings']:
                    value = True
                elif value.lower() in conversions['boolean_false_strings']:
                    value = False
                else:
                    raise ValueError('Cannot convert to boolean: {}'.format(
                        value))
        elif column_type.is_str():
            if not isinstance(value, str):
                value = str(value)
        elif column_type.is_num():
            if isinstance(value, str):
                if conversions['decimal_separator'] != '.':
                    value = value.replace('.', '')
                value = value.replace(conversions['decimal_separator'], '.')
                value = _number_regex.sub('', value)
            if column_type is ColumnType.INTEGER:
                if not isinstance(value, int):
                    value = int(value)
            elif column_type is ColumnType.FLOAT:
                if not isinstance(value, float):
                    value = float(value)
        elif column_type is ColumnType.DATE:
            if not isinstance(value, date):
                value = datetime.strptime(value,
                                          conversions['date_format']).date()
        elif column_type is ColumnType.TIME:
            if not isinstance(value, time):
                value = datetime.strptime(value,
                                          conversions['time_format']).time()
        elif column_type is ColumnType.DATETIME:
            if not isinstance(value, datetime):
                value = datetime.strptime(value,
                                          conversions['datetime_format'])
        return value
    
    
    def process(self):
        return self._process()
            
            
    @item_path_decorator
    def _process(self, _item_path=None):
        self.before_process()  # hook
        
        # processing defaults
        for key, value in self.defaults.items():
            if key in self.data:
                continue
            if hasattr(value, '__call__'):
                value = value(self)
            self[key] = value
        
        # processing set fields
        for key, value in self.data.items():
            if not isinstance(value, ItemBase):
                self.data[key] = self.process_field(key, value)
            else:
                value._process(_item_path=_item_path)
        
        # processing nullables
        for key in self.nullables:
            if key in self:
                continue
            if key in self.fields:
                self[key] = None
            elif key in self.relations:
                relation = self.relations[key]
                if relation['relation_type'].is_x_to_many():
                    self[key] = relation['item_cls'].Bulk()
                    self[key]._process(_item_path=_item_path)
                else:
                    self[key] = None
        
        self.after_process()  # hook
        
        
    #--- hooks -----------------------------------------------------------------
    
    def before_process(self):
        """ A hook method that is called before processing fields values. """
        pass
    
    
    def after_process(self):
        """ A hook method that is called immediately after all fields have been
        processed.
        """
        pass
    
    
    def before_model_update(self, model):
        """ A hook method that is called before updating matching model with
        item data.
        
        :param model: Model that was pulled from database or freshly
            created (in case there were no matching models).
        """
        pass
    
    
    def after_model_update(self, model):
        """ A hook method that is called after updating matching ORM model with
        item data.
        
        .. note::
            Changes might not yet be committed to a database at this point.
        
        :param model: Model that was updated.
        """
        pass
    
    