from save_to_db.adapters.utils.adapter_manager import get_adapter_cls

from save_to_db.core.item import Item
from save_to_db.core.exceptions import (MultipleModelsMatch,
                                        MultipleItemsMatch)
from save_to_db.utils.test_base import TestBase



class TestItemPersist(TestBase):
    """ Contains tests for persisting items into database. """
    
    ModelGeneralOne = None
    ModelGeneralTwo = None


    def test_persist_single_item_no_related(self):
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'f_integer'}]
            getters = [{'f_float'}, {'f_string', 'f_text'},
                       {'f_date'}]
        
        # need this for `ItemGeneralOne` (related field)
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
                
        persister = self.persister
        
        # creating first model -------------------------------------------------
        
        # cannot create or get
        item = ItemGeneralOne(f_string='str-one')
        items, model_lists = persister.persist(item)
        self.assertFalse(items)
        self.assertFalse(model_lists)
        
        # can get but not create and not in database
        item['f_text'] = 'text-one'
        items, model_lists = persister.persist(item)
        self.assertFalse(items)
        self.assertFalse(model_lists)
        
        item['f_integer'] = None  # still cannot create
        items, model_lists = persister.persist(item)
        self.assertFalse(items)
        self.assertFalse(model_lists)
        
        # can create
        item['f_integer'] = '100'
        items, model_lists = persister.persist(item)
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items), len(model_lists))
        models = model_lists[0]
        self.assertTrue(len(models), 1)
        self.assertIs(items[0], item)
        
        # checking that model got the same values
        self.assertEqual(models[0].f_string, 'str-one')
        self.assertEqual(models[0].f_text, 'text-one')
        self.assertEqual(models[0].f_integer, 100)
        
        first_model = models[0]
        
        # creating second model ------------------------------------------------
        
        item = ItemGeneralOne(f_integer='200', f_string='str-one')
        items, model_lists = persister.persist(item)
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items), len(model_lists))
        models = model_lists[0]
        self.assertTrue(len(models), 1)
        self.assertIs(items[0], item)
        
        self.assertNotEqual(models[0], first_model)
        self.assertEqual(models[0].f_string, 'str-one')
        self.assertEqual(models[0].f_integer, 200)
        
        # updating first model -------------------------------------------------
        
        # cannot get
        item = ItemGeneralOne(f_date=None)  # `None` value cannot be used
        items, model_lists = persister.persist(item)
        self.assertFalse(items)
        self.assertFalse(model_lists)
        
        # can get
        self.assertIs(first_model.f_boolean, None)  # will be `True` later
        item['f_string'] = 'str-one'
        item['f_text'] = 'text-one'
        item['f_boolean'] = True
        
        items, model_lists = persister.persist(item)
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items), len(model_lists))
        models = model_lists[0]
        self.assertTrue(len(models), 1)
        self.assertIs(items[0], item)
        
        self.assertEqual(models[0], first_model)
        self.assertEqual(models[0].f_integer, 100)
        self.assertEqual(models[0].f_string, 'str-one')
        self.assertEqual(models[0].f_text, 'text-one')
        self.assertIs(models[0].f_boolean, True)

        # return boolean to `None`
        item['f_boolean'] = None
        items, (models,) = persister.persist(item)
        self.assertEqual(models[0], first_model)
        self.assertIs(models[0].f_boolean, None)
        
    
    def test_persist_single_item_with_single_related(self):
        model_one_cls = self.ModelGeneralOne
        model_two_cls = self.ModelGeneralTwo
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'f_integer', 'two_1_1'}]
            getters = [{'f_integer', 'two_1_1'},
                       {'f_float'},
                       {'f_string', 'f_text'},
                       {'f_date'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'f_integer'}]
            getters = [{'f_integer'}]
        
        persister = self.persister
        
        # cannot create any items
        # 'two_1_1' is not present 
        item_one = ItemGeneralOne(f_integer='100')
        items, model_lists = persister.persist(item_one)
        self.assertEqual(len(items), 0)
        self.assertEqual(len(items), len(model_lists))
        
        # 'two_1_1' cannot be created
        item_two = ItemGeneralTwo(f_float='20.20')
        items, model_lists = persister.persist(item_two)
        self.assertEqual(len(items), 0)
        self.assertEqual(len(items), len(model_lists))
        
        item_one['two_1_1'] = item_two
        items, model_lists = persister.persist(item_one)
        self.assertEqual(len(items), 0)
        self.assertEqual(len(items), len(model_lists))
        
        self.assertEqual(len(self.get_all_models(model_one_cls)), 0)
        self.assertEqual(len(self.get_all_models(model_two_cls)), 0)
        
        # 'two_1_1' can be created
        item_two['f_integer'] = '200'
        del item_one['f_integer']  # won't be persisted
        items, model_lists = persister.persist(item_one)
        self.assertEqual(len(items), 0)
        self.assertEqual(len(items), len(model_lists))
        
        self.assertEqual(len(self.get_all_models(model_one_cls)), 0)
        # but `item_two` was persisted
        models_two = self.get_all_models(model_two_cls)
        self.assertEqual(len(models_two), 1)
        self.assertEqual(models_two[0].f_integer, 200)
        self.assertEqual(models_two[0].f_float, 20.2)
        
        # persisting item_one with updating existing model
        self.assertIs(models_two[0].f_boolean, None)
        item_one['f_integer'] = '100'
        item_two['f_boolean'] = True
        
        items, model_lists = persister.persist(item_one)
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items), len(model_lists))
        self.assertEqual(len(model_lists), 1)
        models = model_lists[0]
        self.assertEqual(len(models), 1)
        self.assertIs(items[0], item_one)
        
        self.assertEqual(models[0].f_integer, 100)
        self.assertIsNotNone(models[0].two_1_1)
        self.assertIsNotNone(models[0].two_1_1.f_integer, 200)
        self.assertIsNotNone(models[0].two_1_1.f_float, 20.2)
        self.assertIs(models[0].two_1_1.f_boolean, True)
        
        self.assertEqual(len(self.get_all_models(model_one_cls)), 1)
        self.assertEqual(len(self.get_all_models(model_two_cls)), 1)
        
        # persisting using related item as filter
        item_one = ItemGeneralOne(f_integer='100', two_1_1=item_two)
        item_one['f_boolean'] = False
        items, model_lists = persister.persist(item_one)
        
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items), len(model_lists))
        self.assertEqual(len(model_lists), 1)
        models = model_lists[0]
        self.assertEqual(len(models), 1)
        self.assertIs(items[0], item_one)
        self.assertIs(models[0].f_boolean, False)
        
        self.assertEqual(len(self.get_all_models(model_one_cls)), 1)
        self.assertEqual(len(self.get_all_models(model_two_cls)), 1)
    
    
    def test_persist_bulk_item(self):
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'f_integer'}]
            getters = [{'f_integer'}, {'f_float'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'f_integer'}]
            getters = [{'f_integer'}, {'f_float'}]
        
        adapter_cls = get_adapter_cls(self.ModelGeneralOne)
        persister = self.persister
        
        # generating 10 simple items
        bulk_one = ItemGeneralOne.Bulk()
        for i in range(10):
            bulk_one.gen(id=i, f_integer=i+100, f_float=i+1000)
        
        previous_bulk = bulk_one.bulk[:]
        items, model_lists = persister.persist(bulk_one)
        self.assertEqual(bulk_one.bulk, previous_bulk,
                         'Bulk was not changed after persistence')
        
        self.assertEqual(len(items), 10)
        self.assertEqual(len(items), len(model_lists))
        models = [model_entries[0] for model_entries in model_lists
                  if self.assertEqual(len(model_entries), 1) is None]
        models.sort(key=lambda model: model.id)
        loaded_models = self.get_all_models(self.ModelGeneralOne)
        self.assertEqual(len(models), 10)
        for i, model in enumerate(models):
            self.assertIn(model, loaded_models)
            self.assertEqual(model.id, i)
            self.assertEqual(model.f_integer, i+100)
            self.assertEqual(model.f_float, i+1000)
            self.assertIs(model.f_boolean, None)  # for future tests
        
        # generating 10 items that has previous 5 and new 5 items as relations
        bulk_two = ItemGeneralTwo.Bulk()
        for i in range(10):
            item = bulk_two.gen(id=i, f_integer=i+200, f_float=i+2000)
            if i < 5:
                # last five item ones will have twos with IDs from 0 to 4
                # (all `i` values), item twos from 5 to 9
                item['one_x_x'] = bulk_one.slice(start=5)
                item['one_x_x__f_boolean'] = 'true'
                
                if i == 1:
                    # items are from previously saved bulk
                    # item one at index zero has ID = 0,
                    # item two has ID = 1 (current `i`, current item)
                    item['one_1_1'] = items[0]
                    item['one_1_x'].add(items[0])
            else:
                for j in range(5, 10):
                    # generated items are the same for all iterations,
                    # item twos from 5 to 9 will have item ones with IDs
                    # from 600 to 604, item ones on the other side will have
                    # item twos with IDs from 5 to 9 (all `i` values)
                    item['one_x_x'].gen(id=j+600-5, f_integer=j+200-5,
                                        f_float=j+2000-5)
        
        items, model_lists = persister.persist(bulk_two)
        self.assertEqual(len(items), 10)
        self.assertEqual(len(items), len(model_lists))
        models = [model_entries[0] for model_entries in model_lists
                  if self.assertEqual(len(model_entries), 1) is None]
        
        # checking item twos ---------------------------------------------------
        
        # 5 items were not changed, 5 items were updated, 5 items were created
        all_models = self.get_all_models(self.ModelGeneralOne)
        all_models.sort(key=lambda model: model.id)
        self.assertEqual(len(all_models), 15)
        
        # checking fields (using IDs for relations)
        expected_values = [
            # first 5 items that were not changed
            dict(id=0, f_integer=100, f_float=1000.0, f_boolean=None,
                 two_1_1=1, two_x_1=1),
            dict(id=1, f_integer=101, f_float=1001.0, f_boolean=None),
            dict(id=2, f_integer=102, f_float=1002.0, f_boolean=None),
            dict(id=3, f_integer=103, f_float=1003.0, f_boolean=None),
            dict(id=4, f_integer=104, f_float=1004.0, f_boolean=None),
            # 5 items that were updated
            dict(id=5, f_integer=105, f_float=1005.0, f_boolean=True,
                 two_x_x=[0,1,2,3,4]),
            dict(id=6, f_integer=106, f_float=1006.0, f_boolean=True,
                 two_x_x=[0,1,2,3,4]),
            dict(id=7, f_integer=107, f_float=1007.0, f_boolean=True,
                 two_x_x=[0,1,2,3,4]),
            dict(id=8, f_integer=108, f_float=1008.0, f_boolean=True,
                 two_x_x=[0,1,2,3,4]),
            dict(id=9, f_integer=109, f_float=1009.0, f_boolean=True,
                 two_x_x=[0,1,2,3,4]),
            # 5 items that were created
            dict(id=600, f_integer=200, f_float=2000.0, f_boolean=None,
                 two_x_x=[5,6,7,8,9]),
            dict(id=601, f_integer=201, f_float=2001.0, f_boolean=None,
                 two_x_x=[5,6,7,8,9]),
            dict(id=602, f_integer=202, f_float=2002.0, f_boolean=None,
                 two_x_x=[5,6,7,8,9]),
            dict(id=603, f_integer=203, f_float=2003.0, f_boolean=None,
                 two_x_x=[5,6,7,8,9]),
            dict(id=604, f_integer=204, f_float=2004.0, f_boolean=None,
                 two_x_x=[5,6,7,8,9]),
        ]
        relations = {
            fname: direction
            for fname, _, direction in persister.adapter_cls.iter_relations(
                all_models[0].__class__)
        }
        for i, (expected, model) in enumerate(zip(expected_values, all_models)):
            for key, value in expected.items():
                if key not in relations:
                    model_value = getattr(model, key)
                    err_msg = '{}: {} = {}'.format(i, key, model_value)
                    if key != 'f_boolean':
                        self.assertEqual(model_value, value, err_msg)
                    else:
                        self.assertIs(model_value, value, err_msg)
                else:
                    if relations[key].is_x_to_many():
                        model_value = adapter_cls.get_related_x_to_many(
                            model, key)
                        ids = list(m.id for m in model_value)
                        ids.sort()
                        self.assertEqual(
                            ids, value,
                            '{}: {} = {}'.format(i, key, ids))
                    else:
                        model_value = getattr(model, key)
                        self.assertEqual(
                            model_value.id, value,
                            '{}: {} = {}'.format(i, key, model_value.id))
        
        # checking item ones ---------------------------------------------------
        
        # 10 items were created, other creations or no changes were made
        # (5 items were reused, 5 items were created)
        all_models = self.get_all_models(self.ModelGeneralTwo)
        all_models.sort(key=lambda model: model.id)
        self.assertEqual(len(all_models), 10)
        
        expected_values = [
            dict(id=0, f_integer=200, f_float=2000.0,
                 one_x_x=[5,6,7,8,9]),
            dict(id=1, f_integer=201, f_float=2001.0,
                 one_x_x=[5,6,7,8,9],
                 one_1_1=0, one_1_x=[0]),
            dict(id=2, f_integer=202, f_float=2002.0,
                 one_x_x=[5,6,7,8,9]),
            dict(id=3, f_integer=203, f_float=2003.0,
                 one_x_x=[5,6,7,8,9]),
            dict(id=4, f_integer=204, f_float=2004.0,
                 one_x_x=[5,6,7,8,9]),
            
            dict(id=5, f_integer=205, f_float=2005.0,
                 one_x_x=[600,601,602,603,604]),
            dict(id=6, f_integer=206, f_float=2006.0,
                 one_x_x=[600,601,602,603,604]),
            dict(id=7, f_integer=207, f_float=2007.0,
                 one_x_x=[600,601,602,603,604]),
            dict(id=8, f_integer=208, f_float=2008.0,
                 one_x_x=[600,601,602,603,604]),
            dict(id=9, f_integer=209, f_float=2009.0,
                 one_x_x=[600,601,602,603,604]),
        ]
        relations = {
            fname: direction
            for fname, _, direction in persister.adapter_cls.iter_relations(
                all_models[0].__class__)
        }
        for i, (expected, model) in enumerate(zip(expected_values, all_models)):
            for key, value in expected.items():
                if key not in relations:
                    model_value = getattr(model, key)
                    err_msg = '{}: {} = {}'.format(i, key, model_value)
                    self.assertEqual(model_value, value, err_msg)
                else:
                    if relations[key].is_x_to_many():
                        model_value = adapter_cls.get_related_x_to_many(
                            model, key)
                        ids = list(m.id for m in model_value)
                        ids.sort()
                        self.assertEqual(
                            ids, value,
                            '{}: {} = {}'.format(i, key, ids))
                    else:
                        model_value = getattr(model, key)
                        self.assertEqual(
                            model_value.id, value,
                            '{}: {} = {}'.format(i, key, model_value.id))
                        
    
    def test_persist_single_item_with_bulk_related(self):
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'id'}]
            getters = [{'id'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'id'}]
            getters = [{'id'}]
        
        adapter_cls = get_adapter_cls(self.ModelGeneralOne)
        persister = self.persister
        
        item_one = ItemGeneralOne(id='5', f_float='50.50')
        item_one(two_1_1=ItemGeneralTwo(id='10', f_string='1-to-1'),
                 two_x_1=ItemGeneralTwo(id='20', f_string='X-to-1'))
        bulk = item_one['two_1_x']
        bulk.gen(id='30', f_string='1-to-x first')
        bulk.gen(id='40', f_string='1-to-x second')
        bulk = item_one['two_x_x']
        bulk.gen(id='50', f_string='x-to-x first')
        bulk.gen(id='60', f_string='x-to-x second')
        
        items, model_lists = persister.persist(item_one)
        
        self.assertEqual(len(items), 1)
        self.assertEqual(len(items), len(model_lists))
        models = model_lists[0]
        self.assertEqual(len(models), 1)
        self.assertIs(items[0], item_one)
        
        # checking model data
        model = models[0]
        self.assertEqual(model.id, 5)
        self.assertEqual(model.f_float, 50.5)
        
        self.assertIsNotNone(model.two_1_1)
        self.assertEqual(model.two_1_1.id, 10)
        self.assertEqual(model.two_1_1.f_string, '1-to-1')
        
        two_1_x = list(adapter_cls.get_related_x_to_many(model, 'two_1_x'))
        two_1_x.sort(key=lambda model: model.id)
        self.assertEqual(len(two_1_x), 2)
        self.assertEqual(two_1_x[0].id, 30)
        self.assertEqual(two_1_x[0].f_string, '1-to-x first')
        self.assertEqual(two_1_x[1].id, 40)
        self.assertEqual(two_1_x[1].f_string, '1-to-x second')
        
        two_x_x = list(adapter_cls.get_related_x_to_many(model, 'two_x_x'))
        two_x_x.sort(key=lambda model: model.id)
        self.assertEqual(len(two_x_x), 2)
        self.assertEqual(two_x_x[0].id, 50)
        self.assertEqual(two_x_x[0].f_string, 'x-to-x first')
        self.assertEqual(two_x_x[1].id, 60)
        self.assertEqual(two_x_x[1].f_string, 'x-to-x second')
        
    
    def test_multiple_models_match_exception(self):
        model_one_cls = self.ModelGeneralOne
        model_two_cls = self.ModelGeneralTwo
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'f_integer'}]
            getters = [{'f_integer'}, {'f_float', 'f_text'}]
        
        # need this for `ItemGeneralOne` (related field)
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'f_integer'}]
            getters = [{'f_integer'}, {'f_float', 'one_x_1'}]
        
        persister = self.persister
        
        # with simple fields ---------------------------------------------------
        # creating two items with different integer fields but same other fields
        item = ItemGeneralOne(f_integer='100', f_float='200.200')
        persister.persist(item)
        item = ItemGeneralOne(f_integer='200', f_float='200.200')
        persister.persist(item)
        
        # updating to get 'f_float' and 'f_text' have the same values for
        # different models 
        item = ItemGeneralOne(f_integer='100', f_text='text-1')
        persister.persist(item)
        item = ItemGeneralOne(f_integer='200', f_text='text-1')
        persister.persist(item)
        
        self.assertEqual(len(self.get_all_models(model_one_cls)), 2)
        
        # this must get two models from database
        item = ItemGeneralOne(f_integer='100',
                              f_float='200.200', f_text='text-1')
        with self.assertRaises(MultipleModelsMatch):
            persister.persist(item)
        
        # still 2 models in database
        self.assertEqual(len(self.get_all_models(model_one_cls)), 2)
        
        # using relations ------------------------------------------------------
        item = ItemGeneralTwo(f_integer='100', f_float='200.200')
        persister.persist(item)
        item = ItemGeneralTwo(f_integer='200', f_float='200.200')
        persister.persist(item)
        
        item_one = ItemGeneralOne(f_integer='300')  # new item one
        item = ItemGeneralTwo(f_integer='100', one_x_1=item_one)
        persister.persist(item)
        item = ItemGeneralTwo(f_integer='200', one_x_1=item_one)
        persister.persist(item)
        
        self.assertEqual(len(self.get_all_models(model_one_cls)), 3)
        self.assertEqual(len(self.get_all_models(model_two_cls)), 2)

        # this must get two models from database
        item = ItemGeneralTwo(f_float='200.200', one_x_1=item_one)
        with self.assertRaises(MultipleModelsMatch):
            persister.persist(item)

    
    def test_multiple_items_match_exception(self):
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'f_integer'}]
            getters = [{'f_integer'}, {'f_float'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
        
        persister = self.persister
        persister.persist(ItemGeneralOne(f_integer=10, f_float=1))
        persister.persist(ItemGeneralOne(f_integer=20, f_float=2))
        
        bulk = ItemGeneralOne.Bulk()
        # two items will get the same model
        bulk.gen(f_integer=10, f_string='str-value-one')
        bulk.gen(f_float=1, f_string='str-value-two')
        
        with self.assertRaises(MultipleItemsMatch):
            persister.persist(bulk)
    
    
    def test_replace_x_to_many(self):
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'f_string'}]
            getters = [{'f_string'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'f_string'}]
            getters = [{'f_string'}]
            relations = {
                'one_1_x': {
                    'replace_x_to_many': True,
                }
            }
        
        adapter_cls = get_adapter_cls(self.ModelGeneralOne)
        persister = self.persister
        
        # replace_x_to_many = False
        item_one = ItemGeneralOne(f_string='1')
        item_one['two_1_x'].gen(f_string='1: 2->1')
        item_one['two_1_x'].gen(f_string='2: 2->1')
        persister.persist(item_one)
        item_one = ItemGeneralOne(f_string='1')  # item recreated
        item_one['two_1_x'].gen(f_string='3: 2->1')
        item_one['two_1_x'].gen(f_string='4: 2->1')
        
        _, model_lists = persister.persist(item_one)
        self.assertEqual(len(model_lists), 1)
        models = model_lists[0]
        self.assertEqual(len(models), 1)
        model = models[0]
        two_1_x = list(adapter_cls.get_related_x_to_many(model, 'two_1_x'))
        self.assertEqual(len(two_1_x), 4)
        two_1_x.sort(key=lambda m: m.f_string)
        for i in range(4):
            self.assertEqual(two_1_x[i].f_string, '{}: 2->1'.format(i+1))
        
        # replace_x_to_many = True
        item_two = ItemGeneralTwo(f_string='2')
        item_two['one_1_x'].gen(f_string='1: 1->2')
        item_two['one_1_x'].gen(f_string='2: 1->2')
        persister.persist(item_two)
        item_two = ItemGeneralTwo(f_string='2')  # item recreated
        item_two['one_1_x'].gen(f_string='3: 1->2')
        item_two['one_1_x'].gen(f_string='4: 1->2')
        
        _, model_lists = persister.persist(item_two)
        self.assertEqual(len(model_lists), 1)
        models = model_lists[0]
        self.assertEqual(len(models), 1)
        model = models[0]
        one_1_x = list(adapter_cls.get_related_x_to_many(model, 'one_1_x'))
        self.assertEqual(len(one_1_x), 2)
        
        one_1_x.sort(key=lambda m: m.f_string)
        for i in range(2):
            # `i+3` because first two items replaced
            self.assertEqual(one_1_x[i].f_string, '{}: 1->2'.format(i+3))
    
    
    def test_multiple_model_update(self):
        model_one_cls = self.ModelGeneralOne
        model_two_cls = self.ModelGeneralTwo
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'f_integer'}]
            getters = [{'f_integer'}, {'f_float', 'f_text'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'f_integer'}]
            getters = [{'f_integer'}, {'f_float', 'one_x_1'}]
        
        persister = self.persister
        
        # with simple fields ---------------------------------------------------
        # creating two items with different integer fields but same other fields
        item = ItemGeneralOne(f_integer='100', f_float='200.200',
                              f_boolean=True)
        persister.persist(item)
        item = ItemGeneralOne(f_integer='200', f_float='200.200',
                              f_boolean=False)
        persister.persist(item)
        
        # updating to get 'f_float' and 'f_text' have the same values for
        # different models 
        item = ItemGeneralOne(f_integer='100', f_text='text-1')
        persister.persist(item)
        item = ItemGeneralOne(f_integer='200', f_text='text-1')
        persister.persist(item)
        
        self.assertEqual(len(self.get_all_models(model_one_cls)), 2)
        
        # this must get two models from database
        item = ItemGeneralOne(f_integer='100',
                              f_float='200.200', f_text='text-1')
        item.allow_multi_update= True
        items, model_lists = persister.persist(item)
        
        self.assertEqual(len(items), 1)
        self.assertEqual(len(model_lists), 1)
        self.assertEqual(len(model_lists[0]), 2)
        models = model_lists[0]
        models.sort(key=lambda model: not model.f_boolean)
        
        self.assertIs(models[0].f_boolean, True)
        self.assertEqual(models[0].f_integer, 100)
        self.assertEqual(models[0].f_float, 200.2)
        self.assertEqual(models[0].f_text, 'text-1')
        
        self.assertIs(models[1].f_boolean, False)
        self.assertEqual(models[1].f_integer, 100)
        self.assertEqual(models[1].f_float, 200.2)
        self.assertEqual(models[1].f_text, 'text-1')
        
        # still 2 models in database
        self.assertEqual(len(self.get_all_models(model_one_cls)), 2)
        
        # using relations ------------------------------------------------------
        item = ItemGeneralTwo(f_integer='100', f_float='200.200')
        persister.persist(item)
        item = ItemGeneralTwo(f_integer='200', f_float='200.200')
        persister.persist(item)
        
        item_one = ItemGeneralOne(f_integer='300')  # new item one
        item = ItemGeneralTwo(f_integer='100', one_x_1=item_one)
        persister.persist(item)
        item = ItemGeneralTwo(f_integer='200', one_x_1=item_one)
        persister.persist(item)
        
        self.assertEqual(len(self.get_all_models(model_one_cls)), 3)
        self.assertEqual(len(self.get_all_models(model_two_cls)), 2)

        # this must get two models from database
        item = ItemGeneralTwo(f_float='200.200', one_x_1=item_one)
        item.allow_multi_update = True
        item, model_lists = persister.persist(item)
        
        self.assertEqual(len(items), 1)
        self.assertEqual(len(model_lists), 1)
        self.assertEqual(len(model_lists[0]), 2)
        models = model_lists[0]
        models.sort(key=lambda model: model.f_integer)
        
        self.assertEqual(models[0].f_integer, 100)
        self.assertEqual(models[0].f_float, 200.2)
        
        self.assertEqual(models[1].f_integer, 200)
        self.assertEqual(models[1].f_float, 200.2)
        
        self.assertIs(models[0].one_x_1, models[1].one_x_1)
        self.assertEqual(models[0].one_x_1.f_integer, 300)
    
    
    def test_set_multiple_related(self):
        model_one_cls = self.ModelGeneralOne
        model_two_cls = self.ModelGeneralTwo
        
        class ItemGeneralOne(Item):
            allow_multi_update = True
            model_cls = self.ModelGeneralOne
            creators = [{'f_integer'}]
            getters = [{'f_integer'}, {'f_float', 'f_text'}]
        
        class ItemGeneralTwo(Item):
            allow_multi_update = True
            model_cls = self.ModelGeneralTwo
            creators = [{'f_integer'}]
            getters = [{'f_integer'}, {'f_float', 'one_x_1'}]
        
        persister = self.persister
        
        # creating two items with different integer fields but same other fields
        item = ItemGeneralOne(f_integer='100', f_float='200.200',
                              f_boolean=True)
        persister.persist(item)
        item = ItemGeneralOne(f_integer='200', f_float='200.200',
                              f_boolean=False)
        persister.persist(item)
        
        # updating to get 'f_float' and 'f_text' have the same values for
        # different models 
        item_one = ItemGeneralOne(f_integer='100', f_text='text-1')
        persister.persist(item_one)
        item_one = ItemGeneralOne(f_integer='200', f_text='text-1')
        persister.persist(item_one)
        
        self.assertEqual(len(self.get_all_models(model_one_cls)), 2)
        
        #--- set two models to x-to-many field must work -----------------------
        item_two = ItemGeneralTwo(f_integer='100')
        item_two['one_1_x'].gen(f_float='200.200', f_text='text-1')
        
        items, model_lists = persister.persist(item_two)
        self.assertEqual(len(items), 1)
        self.assertEqual(len(model_lists), 1)
        self.assertEqual(len(model_lists[0]), 1)
        
        # but the model has two related models
        one_1_x = self.get_all_models(model_one_cls)
        self.assertEqual(len(one_1_x), 2)
        
        one_1_x.sort(key=lambda model: model.f_integer)
        self.assertEqual(one_1_x[0].f_integer, 100)
        self.assertEqual(one_1_x[0].f_float, 200.2)
        self.assertEqual(one_1_x[0].f_text, 'text-1')
        self.assertEqual(one_1_x[1].f_integer, 200)
        self.assertEqual(one_1_x[1].f_float, 200.2)
        self.assertEqual(one_1_x[1].f_text, 'text-1')
        
        #--- set two models to x-to-one field must fail ------------------------
        item_two = ItemGeneralTwo(f_integer='200')
        item_two['one_1_1'](f_float='200.200', f_text='text-1')
        
        with self.assertRaises(MultipleModelsMatch):
            persister.persist(item_two)
        

    def test_forward_and_reverse_relations_filters_one(self):
        # referencing parent and two
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'parent_1_1'}, {'parent_x_1'}, {'parent_x_x'},
                        {'two_1_1'}, {'two_1_x'}, {'two_x_1'}, {'two_x_x'},
                        {'f_integer'}]
            getters = [{'parent_1_1'}, {'parent_x_1'}, 
                       {'two_1_1'}, {'two_x_1'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'f_integer'}]
            getters = [{'f_integer'}]
            
        adapter_cls = get_adapter_cls(self.ModelGeneralOne)
        persister = self.persister
        
        # parent_1_1
        item_parent_1_1 = ItemGeneralOne(f_string='parent_1_1',
                                         f_integer='101')
        item_child_1_1 = ItemGeneralOne(f_string='child_1_1',
                                        parent_1_1=item_parent_1_1)
        persister.persist(item_child_1_1)
        models = self.get_all_models(self.ModelGeneralOne)
        model = [m for m in models if m.f_string=='child_1_1'][0]
        self.assertEqual(model.parent_1_1.f_string, 'parent_1_1')
        model = [m for m in models if m.f_string=='parent_1_1'][0]
        self.assertEqual(model.child_1_1.f_string, 'child_1_1')
        
        # parent_x_1
        item_parent_x_1 = ItemGeneralOne(f_string='parent_x_1',
                                         f_integer='901')
        item_child_1_x = ItemGeneralOne(f_string='child_1_x',
                                        parent_x_1=item_parent_x_1)
        persister.persist(item_child_1_x)
        models = self.get_all_models(self.ModelGeneralOne)
        model = [m for m in models if m.f_string=='child_1_x'][0]
        self.assertEqual(model.parent_x_1.f_string, 'parent_x_1')
        model = [m for m in models if m.f_string=='parent_x_1'][0]
        child_1_x = adapter_cls.get_related_x_to_many(model, 'child_1_x')
        self.assertEqual(len(child_1_x), 1)
        self.assertEqual(child_1_x[0].f_string, 'child_1_x')
        
        # two_1_1
        item_two_1_1 = ItemGeneralTwo(f_string='two_1_1',
                                      f_integer='101')
        item_one_1_1 = ItemGeneralOne(f_string='one_1_1',
                                      two_1_1=item_two_1_1)
        persister.persist(item_one_1_1)
        models = self.get_all_models(self.ModelGeneralOne)
        model = [m for m in models if m.f_string=='one_1_1'][0]
        self.assertEqual(model.two_1_1.f_string, 'two_1_1')
        models = self.get_all_models(self.ModelGeneralTwo)
        model = [m for m in models if m.f_string=='two_1_1'][0]
        self.assertEqual(model.one_1_1.f_string, 'one_1_1')
        
        # two_x_1
        item_two_x_1 = ItemGeneralTwo(f_string='two_x_1',
                                      f_integer='901')
        item_one_1_x = ItemGeneralOne(f_string='one_1_x',
                                      two_x_1=item_two_x_1)
        persister.persist(item_one_1_x)
        models = self.get_all_models(self.ModelGeneralOne)
        model = [m for m in models if m.f_string=='one_1_x'][0]
        self.assertEqual(model.two_x_1.f_string, 'two_x_1') 
        models = self.get_all_models(self.ModelGeneralTwo)
        model = [m for m in models if m.f_string=='two_x_1'][0]
        one_1_x = adapter_cls.get_related_x_to_many(model, 'one_1_x')
        self.assertEqual(len(one_1_x), 1)
        self.assertEqual(one_1_x[0].f_string, 'one_1_x')
    
    
    def test_forward_and_reverse_relations_filters_two(self):
        # referencing child and one
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'child_1_1'}, {'child_x_x'},
                        {'f_integer'}]
            getters = [{'child_1_1'},
                       {'two_1_1'}, {'two_x_1'},
                       {'f_string'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            creators = [{'one_1_1'}, {'one_1_x'}, {'one_x_1'}, {'one_x_x'},
                        {'f_integer'}]
            getters = [{'one_1_1'}, {'one_x_1'},
                       {'f_integer'}]
        
        
        adapter_cls = get_adapter_cls(self.ModelGeneralOne)
        persister = self.persister
        
        # child_1_1
        item_child_1_1 = ItemGeneralOne(f_string='child_1_1',
                                        f_integer='101')
        item_parent_1_1 = ItemGeneralOne(f_string='parent_1_1',
                                         child_1_1=item_child_1_1)
        persister.persist(item_parent_1_1)
        models = self.get_all_models(self.ModelGeneralOne)
        model = [m for m in models if m.f_string=='parent_1_1'][0]
        self.assertEqual(model.child_1_1.f_string, 'child_1_1')
        model = [m for m in models if m.f_string=='child_1_1'][0]
        self.assertEqual(model.parent_1_1.f_string, 'parent_1_1')
        
        # one_1_1
        item_one_1_1 = ItemGeneralOne(f_string='one_1_1',
                                      f_integer='1101')
        item_two_1_1 = ItemGeneralTwo(f_string='two_1_1',
                                      one_1_1=item_one_1_1)
        persister.persist(item_two_1_1)
        models = self.get_all_models(self.ModelGeneralTwo)
        model = [m for m in models if m.f_string=='two_1_1'][0]
        self.assertEqual(model.one_1_1.f_string, 'one_1_1')
        models = self.get_all_models(self.ModelGeneralOne)
        model = [m for m in models if m.f_string=='one_1_1'][0]
        self.assertEqual(model.two_1_1.f_string, 'two_1_1')
        
        # one_x_1
        item_one_x_1 = ItemGeneralOne(f_string='one_x_1',
                                      f_integer='1901')
        item_two_1_x = ItemGeneralTwo(f_string='two_1_x',
                                      one_x_1=item_one_x_1)
        persister.persist(item_two_1_x)
        models = self.get_all_models(self.ModelGeneralTwo)
        model = [m for m in models if m.f_string=='two_1_x'][0]
        self.assertEqual(model.one_x_1.f_string, 'one_x_1') 
        models = self.get_all_models(self.ModelGeneralOne)
        model = [m for m in models if m.f_string=='one_x_1'][0]
        two_1_x = adapter_cls.get_related_x_to_many(model, 'two_1_x')
        self.assertEqual(len(two_1_x), 1)
        self.assertEqual(two_1_x[0].f_string, 'two_1_x')
        
        
    def test_forward_and_reverse_relations_persist(self):
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
        
        adapter_cls = get_adapter_cls(self.ModelGeneralOne)
        persister = self.persister
        
        #--- from item_one ---
        item_one = ItemGeneralOne()
        item_one['two_1_1'] = ItemGeneralTwo(f_integer='101')
        item_one['two_x_1'] = ItemGeneralTwo(f_integer='901')
        item_one['two_x_x'].gen(f_integer='909')
        
        persister.persist(item_one)
        models = self.get_all_models(self.ModelGeneralOne)
        
        self.assertEqual(len(models), 1)
        model = models[0]
        self.assertEqual(model.two_1_1.f_integer, 101)
        self.assertEqual(model.two_x_1.f_integer, 901)
        two_x_x = adapter_cls.get_related_x_to_many(model, 'two_x_x')
        self.assertEqual(len(two_x_x), 1)
        self.assertEqual(two_x_x[0].f_integer, 909)
        
        #--- from item two ---
        item_two = ItemGeneralTwo(f_string='second item')
        item_two['one_1_1'] = ItemGeneralOne(f_integer='2101')
        item_two['one_x_1'] = ItemGeneralOne(f_integer='2901')
        item_two['one_x_x'].gen(f_integer='2909')
        
        persister.persist(item_two)
        models = self.get_all_models(self.ModelGeneralTwo)
        
        #self.assertEqual(len(models), 4)  # 3 before and 1 now
        model = [m for m in models if m.f_string=='second item'][0]
        self.assertEqual(model.one_1_1.f_integer, 2101)
        self.assertEqual(model.one_x_1.f_integer, 2901)
        one_x_x = adapter_cls.get_related_x_to_many(model, 'one_x_x')
        self.assertEqual(len(one_x_x), 1)
        self.assertEqual(one_x_x[0].f_integer, 2909)
        
        #--- from self to self ---
        item_one = ItemGeneralOne(f_string='third item')
        # parent
        item_one['parent_1_1'] = ItemGeneralOne(f_integer='3101')
        item_one['parent_x_1'] = ItemGeneralOne(f_integer='3901')
        item_one['parent_x_x'].gen(f_integer='3909')
        # child
        item_one['child_1_1'] = ItemGeneralOne(f_integer='4101')
        item_one['child_1_x'] = ItemGeneralOne(f_integer='4109')
        item_one['child_x_x'].gen(f_integer='4909')
        
        persister.persist(item_one)
        models = self.get_all_models(self.ModelGeneralOne)
        model = [m for m in models if m.f_string=='third item'][0]
        
        # parent
        self.assertEqual(model.parent_1_1.f_integer, 3101)
        self.assertEqual(model.parent_x_1.f_integer, 3901)
        parent_x_x = adapter_cls.get_related_x_to_many(model, 'parent_x_x')
        self.assertEqual(len(parent_x_x), 1)
        self.assertEqual(parent_x_x[0].f_integer, 3909)
        
        # child
        self.assertEqual(model.child_1_1.f_integer, 4101)
        child_1_x = adapter_cls.get_related_x_to_many(model, 'child_1_x')
        self.assertEqual(len(child_1_x), 1)
        self.assertEqual(child_1_x[0].f_integer, 4109)
        child_x_x = adapter_cls.get_related_x_to_many(model, 'child_x_x')
        self.assertEqual(len(child_x_x), 1)
        self.assertEqual(child_x_x[0].f_integer, 4909)
        
