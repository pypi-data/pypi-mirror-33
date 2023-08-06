from django.apps import apps

from django.db import models, transaction
from django.db.models import Q

from django.db.models.fields.related import OneToOneField, OneToOneRel
from django.db.models.fields.related import ManyToManyField, ManyToManyRel
from django.db.models.fields.related import ManyToOneRel
from django.db.models.fields.related import ForeignKey

from django.db.models.fields.related_descriptors import \
    ReverseOneToOneDescriptor, ReverseManyToOneDescriptor

from .utils.adapter_base import AdapterBase
from .utils.column_type import ColumnType
from .utils.relation_type import RelationType



class DjangoAdapter(AdapterBase):
    """ An adapter for working with Django ORM.
    
    The `adapter_settings` is a dictionary with next values:
    
        - *using* is a database name (a key from `DATABASES` dictionary in the
          "settings.py" file of a Django project), if it isn't provided
          "default" database is used.
    
    .. note::
    
        If you are going to use transactions, set `autocommit` for the database
        to `False`:
        
            .. code-block:: Python
        
                from django.db import transaction
                # Next function takes a `using` argument which should be the
                # name of a database. If it isn’t provided, Django uses the
                # "default" database.
                transaction.set_autocommit(False, using='database_name')
    """
    
    COMPOSITE_KEYS_SUPPORTED = False
    
    
    #--- general methods -------------------------------------------------------
    
    @classmethod
    def is_usable(cls, model_cls):
        return issubclass(model_cls, models.Model)
    
    
    @classmethod
    def commit(cls, adapter_settings):
        transaction.commit(using=adapter_settings.get('using', 'default'))


    @classmethod
    def rollback(cls, adapter_settings):
        transaction.rollback(using=adapter_settings.get('using', 'default'))
    
    
    @classmethod
    def iter_fields(cls, model_cls):
        foreign_key_classes = (ForeignKey, ManyToOneRel,
                               OneToOneField, OneToOneRel,
                               ManyToManyField, ManyToManyRel)
        
        type_to_const = (
            (models.BinaryField, ColumnType.BINARY),
            (models.TextField, ColumnType.TEXT),
            (models.CharField, ColumnType.STRING),
            ((models.AutoField, models.IntegerField), ColumnType.INTEGER),
            ((models.BooleanField,
              models.NullBooleanField), ColumnType.BOOLEAN),
            (models.DateTimeField, ColumnType.DATETIME),
            ((models.FloatField,
              models.DecimalField), ColumnType.FLOAT),
            (models.DateField, ColumnType.DATE),
            (models.TimeField, ColumnType.TIME),
            (models.DateTimeField, ColumnType.DATETIME),
        )
        for field in model_cls._meta.get_fields():
            if isinstance(field, foreign_key_classes):
                continue
            
            yield_type = ColumnType.OTHER
            for field_class, column_type in type_to_const:
                if isinstance(field, field_class):
                    yield_type = column_type
                    break
            yield field.name, yield_type
    
    
    @classmethod
    def iter_relations(cls, model_cls):
        foreign_key_classes = (ForeignKey, ManyToOneRel,
                               OneToOneField, OneToOneRel,
                               ManyToManyField, ManyToManyRel)
        
        type_to_const = [
            [(OneToOneField, OneToOneRel), RelationType.ONE_TO_ONE],
            [ForeignKey, RelationType.MANY_TO_ONE],
            [ManyToOneRel, RelationType.ONE_TO_MANY],
            [(ManyToManyField,
              ManyToManyRel), RelationType.MANY_TO_MANY],
        ]
        for field in model_cls._meta.get_fields():
            if not isinstance(field, foreign_key_classes):
                continue
            
            for field_class, column_type in type_to_const:
                if isinstance(field, field_class):
                    yield_type = column_type
                    break
                
            yield field.name, field.related_model, yield_type
    
    
    @classmethod
    def iter_required_fields(cls, model_cls):
        for field in model_cls._meta.get_fields():
            if isinstance(field, (models.AutoField, ManyToManyField)):
                continue
            if not field.null and field.default is models.NOT_PROVIDED:
                yield field.name
    
    
    @classmethod
    def iter_unique_field_combinations(cls, model_cls):
        for unique_constraint_fields in model_cls._meta.unique_together:
            yield unique_constraint_fields
            
        for field in model_cls._meta.get_fields():
            if hasattr(field, 'field'):  # relation
                if isinstance(field, (OneToOneField,
                                      OneToOneRel)):
                    yield (field.name,)  # one-to-one always unique
                    continue
                field = field.field
            if field.unique:
                yield (field.name,)
    
    
    @classmethod
    def get_table_fullname(cls, model_cls):
        return model_cls._meta.db_table
    
    
    @classmethod
    def get_model_cls_by_table_fullname(cls, name, adapter_settings):
        for models in apps.all_models.values():
            for model in models.values():
                if cls.get_table_fullname(model) == name:
                    return model
    
    
    #--- methods for working with items ----------------------------------------
    
    @classmethod
    def persist(cls, item, adapter_settings):
        item.process()
        using = adapter_settings.get('using', 'default')
        
        #--- first getting item models from database ---------------------------
        items_and_fkeys = cls.get_items_and_fkeys(item, adapter_settings)
        if not items_and_fkeys:
            return [], []
        
        all_items_filters = Q()
        getters = items_and_fkeys[0][0].getters
        
        for item, fkeys in items_and_fkeys:
            one_item_filters = Q()
            for group in getters:
                group_filters = Q()
                skip_group_filters = False
                # in case related item was not in database
                for field_name in group:
                    if field_name not in item or \
                            item[field_name] is None:
                        skip_group_filters = True
                        break
                    
                    if field_name in item.fields:
                        field_value = item[field_name]
                        group_filters &= Q(**{field_name: field_value})
                    elif field_name in item.relations:
                        related_models = fkeys.get(field_name)
                        if not related_models:
                            # failed to get or created related model before
                            skip_group_filters = True
                            break
                        
                        relation = item.relations[field_name]
                        if not relation['relation_type'].is_x_to_many():
                            group_filters &= Q(
                                **{field_name: related_models[0]})
                        else:
                            contains_any = Q()
                            for related_model in related_models:
                                contains_any |= Q(**{field_name: related_model})
                            group_filters &= contains_any
                
                if not skip_group_filters:
                    one_item_filters |= group_filters
                
            if one_item_filters.children:
                all_items_filters |= one_item_filters
        
        models = item.model_cls.objects.db_manager(using) \
            .filter(all_items_filters).all()
        
        reverse_classes = ReverseOneToOneDescriptor, ReverseManyToOneDescriptor
        
        #--- matching items to models and updating -----------------------------
        matched_items, matched_models, matched_fkeys = \
            cls.match_items_to_models(items_and_fkeys, models)
        
        other_models_to_save = []
        for item, model_list, fkeys in zip(matched_items, matched_models,
                                           matched_fkeys):
            for model in model_list:
                model._state.db = using
    
                item.before_model_update(model)  # hook
                for field_name in item.data:
                    if field_name in item.fields:
                        setattr(model, field_name, item[field_name])
                
                # because of "ValueError: Unsaved model instance cannot be used
                # in an ORM query" we set x-to-many values last
                
                # x-to-one
                for fkey, fmodels in fkeys.items():
                    relation = item.relations[fkey]
                    if relation['relation_type'].is_x_to_many():
                        continue
                
                    setattr(model, fkey, fmodels[0])
                
                if model.id is None:
                    model.save(using=using)
                    do_save_again = False
                else:
                    do_save_again = True
                
                # x-to-many plus reverse
                for fkey, fmodels in fkeys.items():
                    relation = item.relations[fkey]
                    
                    if not relation['relation_type'].is_x_to_many():
                        field_data = getattr(item.model_cls, fkey)
                        if isinstance(field_data, reverse_classes):
                            other_fkey = field_data.related.remote_field.name
                            setattr(fmodels[0], other_fkey, model)
                            if fmodels[0] not in other_models_to_save:
                                other_models_to_save.append(fmodels[0])
                    else:
                        do_save_again = True
                        related_list = getattr(model, fkey)
                        if relation['replace_x_to_many']:
                            related_list.clear()
                        related_list.add(*fmodels)
                
                if do_save_again:
                    model.save(using=using)
                
                for m in other_models_to_save:
                    m.save(using=using)
                
                item.after_model_update(model)  # hook
            
        return matched_items, matched_models
        
        
    
    #--- helper functions ------------------------------------------------------
    
    @classmethod
    def get_primary_key_names(cls, model_cls):
        # Django cannot handle composite primary keys
        for field in model_cls._meta.get_fields():
            if field.primary_key:
                return (field.name,)
            
    
    @classmethod
    def get_related_x_to_many(cls, model_cls, field_name):
        return list(getattr(model_cls, field_name).all())
    
    
    #--- methods for tests -----------------------------------------------------
    
    @staticmethod
    def get_all_models(model_cls, adapter_settings):
        models = model_cls.objects.db_manager(
            adapter_settings.get('using', 'default')).all()
        return list(models)