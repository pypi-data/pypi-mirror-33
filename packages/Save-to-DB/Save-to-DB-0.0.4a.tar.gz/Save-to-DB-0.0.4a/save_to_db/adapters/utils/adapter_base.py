from itertools import chain
from save_to_db.core.exceptions import (MultipleModelsMatch,
                                        MultipleItemsMatch)


class AdapterBase(object):
    """ Base adapter class for all database adapters.
    Here you can see descriptions of all required methods for DB adapters
    that are going to extend this class.
    """
    
    #: Must be set to `True` if the ORM supports composite primary keys
    COMPOSITE_KEYS_SUPPORTED = True
    
    #--- general methods -------------------------------------------------------
    
    @classmethod
    def is_usable(cls, model_cls):
        """ Returns `True` if this adapter can deal with `model_cls` class.
        Here you must somehow recognize that the model class was created
        using the particular ORM library that this adapter is for.
        
        :param model_cls: ORM model class (of any library).
        :returns: Boolean value indicating whether this adapter can deal with
            the given model class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def commit(cls, adapter_settings):
        """ Commits current transaction to database.
        
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def rollback(cls, adapter_settings):
        """ Rolls back current transaction.
        
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def iter_fields(cls, model_cls):
        """ Returns an iterator of field names and their types. Foreign keys
        and relations must be ignored.
        
        :param model_cls: ORM model class for which column data are going to be
            returned.
        :returns: A generator of tuples of type:
        
                *(field_name, field_type)*
            
            Where:
            
                - *field_name* is a name of an ORM model field.
                - *field_type* must be one of the fields of
                  :py:class:`~.column_type.ColumnType` enumeration class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def iter_relations(cls, model_cls):
        """ Returns an iterator of all fields that used to reference other
        ORM models.
        
        :param model_cls: ORM model class for which relations are going to be
            iterated.
        :returns: A generator of tuples of type:
        
                *(relation_field_name, relation_model_cls, relation_type)*
                
            Where:
            
            - *relation_field_name* is a field of the `model_cls` that
              references another model.
            
            - *relation_model_cls* is an ORM model class being referenced.
              
            - *relation_type* must be one of the fields of
              :py:class:`~.relation_type.RelationType` enumeration class.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def iter_required_fields(cls, model_cls):
        """ Returns an iterator of fields that cannot be null for an ORM model
        class:
        
            - Simple field value cannot be null if the column has a not null
              constraint.
            - Relation field cannot be null if any column used as
              foreign key (can be multiple in case of composite key) is not
              null.
        
        :param model_cls: ORM model class for which relations are going to be
            iterated.
        :returns: A generator of field names.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def iter_unique_field_combinations(cls, model_cls):
        """ Returns an iterator of unique fields.
        
        .. note::
            Relation considered to be unique if the set of columns used as
            foreign keys (can be multiple in case of composite key) has a
            unique constraint.
        
            *Relations can be unique together with other fields.*
        
        :param model_cls: ORM model class for which relations are going to be
            iterated.
        :returns: A generator of field names.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def get_table_fullname(cls, model_cls):
        """ Returns full table name with schema (if applicable) used by an
        ORM model class.
        
        :param model_cls: An ORM model class.
        :returns: Full table name with schema (if applicable). Examples:
        
                - 'public.some_table'
                - 'some_table' (no schema, e.g. SQLite database).
        """
        raise NotImplementedError()
    
    
    @classmethod
    def get_model_cls_by_table_fullname(cls, name, adapter_settings):
        """ Return ORM model class based on full table that that model class
        uses.
        
        :param name: table full name.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :return: ORM model class.
        """
        raise NotImplementedError()
    
    
    #--- methods for working with items ----------------------------------------
    
    @classmethod
    def get_items_and_fkeys(cls, item, adapter_settings):
        """ Returns a list of items and their foreign keys of type:
            
                *[[item, foreign_keys], ...]*
            
            Where:
            
                - `item` is a single item.
                - `foreign_keys` is a dictionary objects where keys are ORM
                  model field names and values are ORM models referenced by
                  those keys. The models are got by persisting related items.
                
        :param item: An instance of
            :py:class:`~save_to_db.core.item_base.ItemBase` class.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :returns: List of items and their foreign keys as ORM models.
        """
        # sorting items by foreign keys
        items_and_related = []
        item_as_list = item.as_list()[:]  # will be popping items from the list
        if not item_as_list:  # empty bulk
            return []
        
        item_relations = item_as_list[0].relations

        while item_as_list:
            items_with_same_related = []
            match_item = item_as_list.pop(0)
            match_related = {}
            for relation_key in match_item.relations:
                if relation_key in match_item:
                    match_related[relation_key] = match_item[relation_key]
            
            items_with_same_related.append(match_item)
            for cur_item in item_as_list[:]:
                cur_related = {}
                for relation_key in cur_item.relations:
                    if relation_key in cur_item:
                        cur_related[relation_key] = cur_item[relation_key]
                
                if cur_related == match_related:
                    item_as_list.remove(cur_item)
                    items_with_same_related.append(cur_item)
                
            items_and_related.append([items_with_same_related, match_related])
        
        # result
        result = []
        for cur_items, cur_related in items_and_related:
            # saving foreign keys
            fkeys = {}
            for relation_key, related_item in cur_related.items():
                _, related_persisted = cls.persist(related_item,
                                                   adapter_settings)
                
                related_persisted_flat = []
                for entries in related_persisted:
                    related_persisted_flat.extend(entries)
                if related_persisted_flat:
                    if len(related_persisted_flat) > 1:
                        relation = item_relations[relation_key]
                        if not relation['relation_type'].is_x_to_many():
                            raise MultipleModelsMatch(
                                cur_items, relation_key, related_persisted_flat)
                    
                    fkeys[relation_key] = related_persisted_flat
                    
            for cur_item in cur_items:
                result.append([cur_item, fkeys])
        
        return result
    
    
    @classmethod
    def match_items_to_models(cls, items_and_fkeys, models):
        """ Matches items to models and returns two lists, one with items and
        another with models. Items in first list match with models from the
        second with the same index in the list.
        
        .. note::
            If model is not in the `models` list but can be created based on
            item data then an empty model will be created for the item.
        
        :param items: List of single items.
        :param models: List of ORM models.
        :returns: Lists of matched items and list of match models for each
            item (a list and a list of lists).
        """
        matched_items = []
        matched_models = []  # list of lists
        matched_fkeys = []
        
        def add_matched(item, model, fkeys):
            if item in matched_items:
                index = matched_items.index(item)
                other_model = matched_models[index]
                if not item.allow_multi_update:
                    raise MultipleModelsMatch(item, model, other_model)
            
            for i, model_list in enumerate(matched_models):
                if model in model_list:
                    other_item = matched_items[i]
                    if item is not other_item:
                        raise MultipleItemsMatch(model, item, other_item)
            
            if item not in matched_items:
                matched_items.append(item)
                matched_models.append([model])
                matched_fkeys.append(fkeys)
            else:
                index = matched_items.index(item)
                matched_models[index].append(model)
        
        for item, fkeys in items_and_fkeys:
            getters = item.getters
            relations = item.relations
            
            item_has_model = False
            for model in models:
                for getter_fields in getters:
                    same = True
                    for field_name in getter_fields:
                        if field_name not in item or item[field_name] is None:
                            same = False
                            break
                        
                        if field_name in item.fields:
                            model_field_value = getattr(model, field_name)
                            if item[field_name] != model_field_value:
                                same = False
                                break
                        elif field_name in relations:
                            if field_name not in fkeys:  # not persisted
                                same = False
                                break
                                
                            relation = relations[field_name]
                            if not relation['relation_type'].is_x_to_many():
                                model_field_value = getattr(model, field_name)
                                if fkeys[field_name][0] != model_field_value:
                                    same = False
                                    break
                            else:
                                model_field_values = cls.get_related_x_to_many(
                                    model, field_name)
                                
                                same = False
                                for fkey_model in fkeys[field_name]:
                                    if fkey_model in model_field_values:
                                        same = True
                                        break
                                    
                                if not same:
                                    break
                    if same:
                        break
                        
                if not same:
                    continue
                
                item_has_model = True
                add_matched(item, model, fkeys)
            
            if not item_has_model and item.can_create(fkeys):
                add_matched(item, item.model_cls(), fkeys)
        
        return matched_items, matched_models, matched_fkeys
    
    
    @classmethod
    def persist(cls, item, adapter_settings, commit=False):
        """ Saves item data into a database by creating or update appropriate
        database records.
        
        :param item: an instance of
            :py:class:`~save_to_db.core.item_base.ItemBase` to persist.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :param commit: If `True` commits changes to database.
        :returns: Item list and corresponding ORM models as a list of lists
            (in case one item updates multiple models).
        """
        raise NotImplementedError()
    
    
    #--- helper functions ------------------------------------------------------
    
    @classmethod
    def get_primary_key_names(cls, model_cls):
        """ Returns tuple of primary key names.
        
        :param model_cls: ORM model class.
        :returns: Tuple of primary key names of `model_cls`.
        """
        raise NotImplementedError()
    
    
    @classmethod
    def get_related_x_to_many(cls, model_cls, field_name):
        """ Returns list of many-to-many related  models.
        
        :param model_cls: ORM model class.
        :param field_name: field name used for reference.
        :returns: List of many-to-many related models.
        """
        return getattr(model_cls, field_name)
    
    
    @classmethod
    def pprint(cls, *models):
        """ Pretty prints `models`.
        
        :param \*models: List of models to print.
        """
        if not models:
            return
        
        def repr_model(model):
            pkeys_names = cls.get_primary_key_names(model.__class__)
            pkeys_values = list(str(getattr(model, pkey))
                                for pkey in pkeys_names)
            return '({},)'.format(','.join(pkeys_values))
            
        
        model_cls = models[0].__class__
        pkeys_names = cls.get_primary_key_names(model_cls)

        field_names = [fname for fname, _, in cls.iter_fields(model_cls)]
        for pk_fname in pkeys_names:
            field_names.remove(pk_fname)
        field_names.sort()
        
        relations = {
            fname: direction
            for fname, _, direction in cls.iter_relations(model_cls)
        }
        relation_names = list(relations.keys())
        relation_names.sort()
        
        padding = len(max(chain(field_names, relation_names), key=len))
        
        for model in models:
            to_print = ['{}:'.format(model_cls.__name__)]
            for fname in chain(pkeys_names, field_names, relation_names):
                if fname in field_names or fname in pkeys_names:
                    value = getattr(model, fname)
                    no_value = value is None
                else:
                    if not relations[fname].is_x_to_many():
                        other_model = None
                        if hasattr(model, fname):
                            other_model = getattr(model, fname)
                            
                        if other_model is None:
                            value = None
                            no_value = True
                        else:
                            value = repr_model(other_model)
                            no_value = False
                    else:
                        other_models = cls.get_related_x_to_many(model,
                                                                    fname)
                        no_value = not other_models
                        value = '[{}]'.format(
                            ','.join([repr_model(m) for m in other_models]))
                    
                to_print.append('    {:<3} {:>{padding}}: {}'.format(
                    'PK' if fname in pkeys_names else
                        '' if no_value else '::',
                    fname if no_value else fname.upper(),
                    value,
                    padding=padding))
            
            print('\n'.join(to_print))
    
    
    #--- methods for tests -----------------------------------------------------
    
    @staticmethod
    def get_all_models(model_cls, adapter_settings):
        """ Returns all models from database `model_cls` class.
        
        :param model_cls: An ORM model class.
        :param adapter_settings: Adapter configuration object. This parameter is
            unique for each adapter class.
        :returns: List of all model instances for `model_cls` class.
        """
        raise NotImplementedError()