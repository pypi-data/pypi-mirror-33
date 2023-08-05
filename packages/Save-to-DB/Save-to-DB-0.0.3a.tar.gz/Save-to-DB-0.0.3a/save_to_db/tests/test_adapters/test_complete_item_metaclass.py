from save_to_db.adapters.utils.adapter_manager import get_adapter_cls
from save_to_db.adapters.utils.column_type import ColumnType
from save_to_db.adapters.utils.relation_type import RelationType
from save_to_db.core.exceptions.item_config import (InvalidFieldName,
                                                    DefaultRelationDefined,
                                                    RelatedItemNotFound,
                                                    MultipleRelatedItemsFound,
                                                    NonExistentRelationDefined,
                                                    NonExistentFieldUsed,
                                                    XToManyGetterUsed)
from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase



class TestCompleteItemMetaclass(TestBase):
    """ Contains tests for an item metaclass that require `model_cls` attribute
    to be a proper model class.
    """
    
    # models that are needed for tests to run
    ModelFieldTypes = None
    ModelGeneralOne = None
    ModelGeneralTwo = None
    ModelInvalidFieldNames = None
    
    
    def setup_models(self, one=True, two=True, one_conf=None, two_conf=None,
                     clear_registry=False):
        if clear_registry:
            self.item_cls_manager.clear()
        
        if one:
            dct = {'model_cls': self.ModelGeneralOne, }
            if one_conf:
                dct.update(one_conf)
            self.ItemGeneralOne = type('ItemGeneralOne', (Item,), dct)
        if two:
            dct = {'model_cls': self.ModelGeneralTwo, }
            if two_conf:
                dct.update(two_conf)
            self.ItemGeneralTwo = type('ItemGeneralTwo', (Item,), dct)
        
        if one and two:
            self.ItemGeneralOne.complete_setup()
            self.ItemGeneralTwo.complete_setup()


    def test_nullables_getters_creators_x_to_many(self):
        for key in ('creators', 'getters', 'nullables'):
            if key == 'getters':  # exception must be raised
                with self.assertRaises(XToManyGetterUsed):
                    self.setup_models(two_conf={key: ['parent_x_x']},
                                      clear_registry=True)
            else:  # no exception
                self.setup_models(one_conf={key: ['parent_x_x']},
                                  clear_registry=True)
        
    
    def test_defaults_nullables_getters_creators_nonexistent_field(self):
        # proper configuration (no nonexistent fields)
        self.setup_models(
            one_conf={
                'creators': ['f_text', 'child_1_1'],  # field and relation
                'getters': ['f_float', 'parent_1_1'],
                'nullables': ['f_date', 'child_1_x'],
                'defaults': {'f_integer': None}
            },
            clear_registry=True)
        item_one_cls = self.ItemGeneralOne
        self.assertEqual(item_one_cls.creators, [{'f_text'}, {'child_1_1'}])
        self.assertEqual(item_one_cls.getters, [{'f_float'}, {'parent_1_1'}])
        self.assertEqual(item_one_cls.nullables, {'child_1_x', 'f_date'})
        
        # nonexistent field
        for key in ('creators', 'getters', 'nullables'):
            with self.assertRaises(NonExistentFieldUsed):
                self.setup_models(two_conf={key: ['nonexistent']},
                                  clear_registry=True)
        
        with self.assertRaises(NonExistentFieldUsed):
            self.setup_models(two_conf={'defaults': {'nonexistent': None}},
                              clear_registry=True)

    
    def test_relations_config_excpetions(self):
        # NonExistentRelationDefined
        class WithNonExistantRelation(Item):
            model_cls = self.ModelFieldTypes
            relations = {
                'non_existant': self.ModelGeneralOne,
            }

        with self.assertRaises(NonExistentRelationDefined):
            WithNonExistantRelation.complete_setup()
        
        # RelatedItemNotFound
        self.setup_models(one=True, two=False)
        with self.assertRaises(RelatedItemNotFound):
            self.ItemGeneralOne.complete_setup()
        
        # MultipleRelatedItemsFound
        self.setup_models(one=False, two=True)
        self.setup_models(one=False, two=True)  # second model
        
        with self.assertRaises(MultipleRelatedItemsFound):
            self.ItemGeneralOne.complete_setup()
        
    
    def test_fields_autoconfig(self):
        self.setup_models()
        
        extected_fields = {
            'id': ColumnType.INTEGER,
            'f_binary': ColumnType.BINARY,
            'f_boolean': ColumnType.BOOLEAN,
            'f_text': ColumnType.TEXT,
            'f_string': ColumnType.STRING,
            'f_integer': ColumnType.INTEGER,
            'f_float': ColumnType.FLOAT,
            'f_date': ColumnType.DATE,
            'f_time': ColumnType.TIME,
            'f_datetime': ColumnType.DATETIME,
        }
        self.assertEqual(self.ItemGeneralOne.fields, extected_fields)
        
    
    def test_relations_autoconfig(self):
        self.setup_models(two_conf={
            'relations': {
                    'parent_x_x': {
                        'replace_x_to_many': True,
                    },
                },
            })
        
        #--- one ---
        expected_relations = {
            'parent_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
            'child_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
            'parent_x_1': {
                'relation_type': RelationType.MANY_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
            'child_1_x': {
                'relation_type': RelationType.ONE_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
            'parent_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
            'child_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
            'two_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
            },
            'two_1_x': {
                'relation_type': RelationType.ONE_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
            },
            'two_x_1': {
                'relation_type': RelationType.MANY_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
            },
            'two_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
            },
        }
        self.assertEqual(self.ItemGeneralOne.relations, expected_relations)
        
        #--- two ---
        expected_relations = {
            'parent_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
            },
            'child_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
            },
            'parent_x_1': {
                'relation_type': RelationType.MANY_TO_ONE,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
            },
            'child_1_x': {
                'relation_type': RelationType.ONE_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
            },
            'parent_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': True,  # default overwritten
            },
            'child_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralTwo,
                'replace_x_to_many': False,
            },
            'one_1_1': {
                'relation_type': RelationType.ONE_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
            'one_1_x': {
                'relation_type': RelationType.ONE_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
            'one_x_1': {
                'relation_type': RelationType.MANY_TO_ONE,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
            'one_x_x': {
                'relation_type': RelationType.MANY_TO_MANY,
                'item_cls': self.ItemGeneralOne,
                'replace_x_to_many': False,
            },
        }
        self.assertEqual(self.ItemGeneralTwo.relations, expected_relations)
    
    
    def __to_sorted_lists(self, iterable_of_iterables):
        result = []
        for iterable in iterable_of_iterables:
            element = list(iterable)
            element.sort()
            result.append(element)
        result.sort()
        return result
    
    
    def test_creators_getter_autoconfig(self):
        # generating items for models
        models_for_items = (
            self.ModelConstraintsOne,
            self.ModelConstraintsTwo,
            self.ModelConstraintsThree,
            self.ModelConstraintsFour,
            self.ModelConstraintsFive,
            self.ModelConstraintsSix,
            self.ModelConstraintsSelf,
        )
        item_classes = []
        for model_cls in models_for_items:
            item_classes.append(type(
                model_cls.__name__.replace('Model', 'Item'), (Item,), {
                    'model_cls': model_cls
                }
            ))
            
        for item_cls in item_classes:
            item_cls.complete_setup()
        (ItemConstraintsOne, ItemConstraintsTwo, ItemConstraintsThree,
         ItemConstraintsFour, ItemConstraintsFive, ItemConstraintsSix,
         ItemConstraintsSelf) = item_classes
        
        # checking configuration
        adapter_cls = get_adapter_cls(ItemConstraintsOne.model_cls)
        composites = adapter_cls.COMPOSITE_KEYS_SUPPORTED
        
        expected = {
            ItemConstraintsOne: {
                'creators': [{'f_text', 'f_string'}],
                'getters': [{'id'}, {'f_integer'}, {'f_string'}, {'five_1_1'}],
            },
            ItemConstraintsTwo: {
                'creators': [{'four_x_1'}],
                'getters': [{'id'}],
            },
            ItemConstraintsThree: {
                'creators': [{'one_x_1'}],
                'getters': [{'id'}],
            },
            ItemConstraintsFour: {
                'creators':
                    [{'primary_two', 'primary_one'}]
                        if composites else [],
                'getters':
                    [{'primary_two', 'primary_one'} if composites else {'id'},
                     {'five_1_1'}, {'f_integer', 'f_string'}],
            },
            ItemConstraintsFive: {
                'creators': [],
                'getters': [{'id'}, {'one_1_1'}, {'four_1_1'}, {'six_1_1'}],
            },
            ItemConstraintsSix: {
                'creators': [{'five_1_1'}],
                'getters': [{'id'}, {'f_integer', 'five_1_1'}, {'five_1_1'}],
            },
            ItemConstraintsSelf: {
                'creators': [{'code', 'second_parent_1_1', 'parent_x_1'}],
                'getters': [{'code'},
                            {'first_parent_1_1'}, {'first_child_1_1'},
                            {'second_parent_1_1'}, {'second_child_1_1'},],
            },
        }
        
        for item_cls in item_classes:
            #--- getters ---
            item_getters = self.__to_sorted_lists(
                item_cls.getters)
            expected_getters = self.__to_sorted_lists(
                expected[item_cls]['getters'])
            self.assertEqual(item_getters, expected_getters, item_cls)
            
            #--- creators ---
            item_creators = self.__to_sorted_lists(
                item_cls.creators)
            expected_creators = self.__to_sorted_lists(
                expected[item_cls]['creators'])
            
            self.assertEqual(item_creators, expected_creators, item_cls)
    
    
    def test_creators_getter_autoconfig_no_overwrite(self):
        class ItemConstraintsSelf(Item):
            model_cls = self.ModelConstraintsSelf
            creators = [{'parent_x_1'}]
            getters = [{'first_parent_1_1'}]
        ItemConstraintsSelf.complete_setup()
        
        self.assertEqual(ItemConstraintsSelf.creators,
                         [{'parent_x_1'}])
        self.assertEqual(ItemConstraintsSelf.getters,
                         [{'first_parent_1_1'}])
    
    
    def test_default_relation_exception(self):
        with self.assertRaises(DefaultRelationDefined):
            self.setup_models(self, one_conf={
                    'defaults': {'two_1_1': None}
                })
    
    
    def test_defaults_injection(self):
        self.setup_models(self, one_conf={
                'defaults': {'f_integer': '100', 'f_boolean': 'true',
                             'f_string': lambda item: 'INT: {}'.format(
                                 item['f_integer'])}
            })
        
        item = self.ItemGeneralOne(f_integer='400')
        item.process()
        self.assertEqual(item['f_integer'], 400)
        self.assertIs(item['f_boolean'], True)
        self.assertEqual(item['f_string'], 'INT: 400')
        
        item = self.ItemGeneralOne(f_boolean='false')
        item.process()
        self.assertEqual(item['f_integer'], 100)
        self.assertIs(item['f_boolean'], False)
        self.assertEqual(item['f_string'], 'INT: 100')
    
    
    def test_invalid_field_name(self):
        class InvalidItem(Item):
            model_cls = self.ModelInvalidFieldNames

        with self.assertRaises(InvalidFieldName):
            InvalidItem()
