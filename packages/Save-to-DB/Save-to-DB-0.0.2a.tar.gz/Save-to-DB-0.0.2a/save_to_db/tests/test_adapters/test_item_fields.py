import datetime

from save_to_db.core.exceptions.item_field import CircularReferenceError
from save_to_db.core.item import Item
from save_to_db.utils.test_base import TestBase



class TestItemFields(TestBase):
    """ Contains tests for setting field values and processing them for both
    normal items and bulk items. This class does not contain tests for
    persisting items to a database.
    """
    
    ModelFieldTypes = None
    ModelGeneralOne = None
    ModelGeneralTwo = None
    
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        class ItemFieldTypes(Item):
            model_cls = cls.ModelFieldTypes
            conversions = {
                'decimal_separator': ',',
            }
        cls.ItemFieldTypes = ItemFieldTypes
        
        class ItemGeneralOne(Item):
            model_cls = cls.ModelGeneralOne
        cls.ItemGeneralOne = ItemGeneralOne
        
        class ItemGeneralTwo(Item):
            model_cls = cls.ModelGeneralTwo
        cls.ItemGeneralTwo = ItemGeneralTwo
        
        
    def test_setting_fields(self):
        #--- setting with correct keys ---
        item = self.ItemGeneralOne()
        item['f_integer'] = '10'
        item['two_1_1__f_string'] = 'one'
        item['two_1_1__one_x_1__f_string'] = 'two'
        item['two_1_1__one_x_x__two_x_1__f_string'] = 'three'
        bulk = item['two_1_1__one_x_x']
        bulk['f_integer'] = '20'
        bulk.gen(f_text='four')
        in_bulk_item = bulk.gen(f_text='five')
        # setting field by calling
        in_bulk_item(f_string='ITEM_CALL') 
        bulk(two_x_1__f_text='BULK_CALL')
        
        expected_value = {
            'f_integer': '10',
            'two_1_1': {
                'f_string': 'one',
                'one_x_1': {
                    'f_string': 'two'
                },
                'one_x_x': {
                    'bulk': [
                        {
                            'f_text': 'four'
                        },
                        {
                            'f_string': 'ITEM_CALL',
                            'f_text': 'five'
                        }
                    ],
                    'defaults': {
                        'f_integer': '20',
                        'two_x_1__f_string': 'three',
                        'two_x_1__f_text': 'BULK_CALL'
                    },
                }
            }
        }
        self.assertEqual(item.to_dict(), expected_value)
        
        #--- setting with incorrect keys ---
        item = self.ItemGeneralOne()
        with self.assertRaises(KeyError):
            item['wrong_key'] = 'value'
        
        bulk = self.ItemGeneralOne.Bulk()
        with self.assertRaises(KeyError):
            bulk['wrong_key'] = 'value'
    
    
    def test_getting_fields(self):
        item = self.ItemGeneralOne()
        related_item = item['two_x_1__one_1_1__two_1_1'](f_integer='20',
                                                         f_string='value')
        self.assertIsInstance(related_item, self.ItemGeneralTwo)
        
        expected_value = {
            'two_x_1': {
                'one_1_1': {
                    'two_1_1': {
                        'f_integer': '20',
                        'f_string': 'value'
                    }
                }
            }
        }
        self.assertEqual(item.to_dict(), expected_value)
        
    
    def test_del_from_item(self):
        item = self.ItemGeneralOne()
        item['f_integer'] = '10'
        item['f_string'] = 'str-10'
        item['two_1_1__f_integer'] = '20'
        item['two_1_1__f_string'] = 'str-20'
        item['two_x_x__one_1_1__f_integer'] = '30'
        item['two_x_x__one_1_1__f_string'] = 'str-30'
        
        expect = {
            'f_integer': '10',
            'f_string': 'str-10',
            'two_1_1': {
                'f_integer': '20',
                'f_string': 'str-20'
            },
            'two_x_x': {
                'bulk': [],
                'defaults': {
                    'one_1_1__f_integer': '30',
                    'one_1_1__f_string': 'str-30'
                },
            }
        }
        self.assertEqual(item.to_dict(), expect)
        
        del expect['f_string']
        del item['f_string']
        self.assertEqual(item.to_dict(), expect)
        
        del expect['two_1_1']['f_string']
        del item['two_1_1__f_string']
        self.assertEqual(item.to_dict(), expect)
        
        del expect['two_x_x']['defaults']['one_1_1__f_string']
        del item['two_x_x__one_1_1__f_string']
        self.assertEqual(item.to_dict(), expect)
    
    
    def test_circular_reference(self):
        # normal reference
        item = self.ItemGeneralOne()
        item['two_x_1__one_1_1'] = item
        with self.assertRaises(CircularReferenceError):
            item.to_dict()
        
        # reference in bulk
        item = self.ItemGeneralOne()
        item['two_x_x'].add(item)
        
        with self.assertRaises(CircularReferenceError):
            item.to_dict()
        
        
    def test_field_convesions(self):
        #--- simple conversion ---
        item = self.ItemFieldTypes(
            binary_1 = 'binary data',
            string_1 = 1000,
            text_1 = 2000,
            integer_1 = '10',
            boolean_1 = 'TRUE',
            float_1 = '1.120,30',  # with comma as decimal separator and a dot
            date_1 = '2000-10-30',
            time_1 = '20:30:40',
            datetime_1 = '2000-10-30 20:30:40')
        
        item.process()
        expected_value = {
            'binary_1': b'binary data',
            'boolean_1': True,
            'date_1': datetime.date(2000, 10, 30),
            'datetime_1': datetime.datetime(2000, 10, 30, 20, 30, 40),
            'float_1': 1120.3,
            'integer_1': 10,
            'string_1': '1000',
            'text_1': '2000',
            'time_1': datetime.time(20, 30, 40)
        }
        self.assertEqual(item.to_dict(), expected_value)
        
        item.process()  # second processing does nothing
        self.assertEqual(item.to_dict(), expected_value)
        
        #--- conversions with relations ---
        item = self.ItemGeneralOne(f_integer='10',
                                   two_x_1__f_integer='20',
                                   two_x_x__f_integer='30')
        item['two_x_x'].gen(f_integer='40')
        item.process()
        
        expected_value = {
            'f_integer': 10,
            'two_x_1': {
                'f_integer': 20
            },
            'two_x_x': {
                'bulk': [
                    {
                        'f_integer': 40
                    }
                ],
                'defaults': {
                    'f_integer': 30
                },
            }
        }
        
        self.assertEqual(item.to_dict(), expected_value)
        
    
    def test_inject_nullables(self):
        self.item_cls_manager.clear()
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            # using normal fields
            nullables = ['f_integer', 'f_string']
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            # using relations
            nullables = ['one_1_1', 'one_x_1', 'one_1_x', 'one_x_x']
        
        # no overwrite for normal fields
        item = ItemGeneralOne(f_integer='10', f_string='20', f_text='30')
        item.process()
        expect = {
            'f_integer': 10,
            'f_string': '20', 
            'f_text': '30',
        }
        self.assertEqual(item.to_dict(), expect)
        
        # normal fields nullables added
        item = ItemGeneralOne()
        item.process()
        expect = {
            'f_integer': None,
            'f_string': None,
        }
        self.assertEqual(item.to_dict(), expect)
        
        # no overwrite for relations
        item = ItemGeneralTwo(one_1_1__f_integer='10',
                              one_1_1__f_string='20',
                              one_x_1__f_integer='10',
                              one_x_1__f_string='20')
        item['one_1_x'].gen(f_integer='10', f_string='20')
        item['one_x_x'].gen(f_integer='10', f_string='20')
        item.process()
        expect = {
            'one_1_1': {
                'f_integer': 10,
                'f_string': '20'
            },
            'one_1_x': {
                'bulk': [
                    {
                        'f_integer': 10,
                        'f_string': '20'
                    }
                ],
                'defaults': {},
            },
            'one_x_1': {
                'f_integer': 10,
                'f_string': '20'
            },
            'one_x_x': {
                'bulk': [
                    {
                        'f_integer': 10,
                        'f_string': '20'
                    }
                ],
                'defaults': {},
            }
        }
        self.assertEqual(item.to_dict(), expect)
        
        # relation fields nullables added
        item = ItemGeneralTwo()
        item.process()
        expect = {
            'one_1_1': None,
            'one_1_x': {
                'bulk': [],
                'defaults': {},
            },
            'one_x_1': None,
            'one_x_x': {
                'bulk': [],
                'defaults': {},
            }
        }
        self.assertEqual(item.to_dict(), expect)
        
    
    def test_inject_bulk_defaults(self):
        self.item_cls_manager.clear()
        
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            # using normal fields
            nullables = ['f_integer', 'f_string']
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
            # using relations
            nullables = ['one_1_1', 'one_1_x']
        
        # default regular fields
        # (first default fields must be injected only then nullables)
        bulk = ItemGeneralOne.Bulk(f_integer='1000', f_text='text-value')
        bulk.gen(f_integer='10', f_float='20.30')
        bulk.gen(f_string='str-value', f_float='20.30')
        bulk.process()
        expect = {
            'bulk': [
                {
                    'f_float': 20.3,  # set value
                    'f_integer': 10,  # nullable, but item has set value
                    'f_string': None,  # nullable, no value was set
                    'f_text': 'text-value'  # default value from bulk
                },
                {
                    'f_float': 20.3,   # set value
                    'f_integer': 1000,  # nullable, overwritten with default
                    'f_string': 'str-value',  # nullable, item has set value
                    'f_text': 'text-value'  # default value from bulk
                }
            ],
            'defaults': {
                'f_integer': 1000,
                'f_text': 'text-value'
            }
        }
        self.assertEqual(bulk.to_dict(), expect)
        
        # default relations
        default_two_1_1 = ItemGeneralTwo(f_integer='10', f_float='20.30')
        default_two_1_x = ItemGeneralTwo.Bulk()
        default_two_1_x.gen(f_integer='20')
        default_two_1_x.gen(f_float='40.50')
        
        bulk = ItemGeneralOne.Bulk(two_1_1=default_two_1_1,
                                   two_1_x=default_two_1_x)
        bulk.gen(two_1_1__f_integer=40)
        bulk.gen(two_1_x__f_text='text-value')
        
        bulk.process()
        expect = {
            'defaults': {
                # `ItemGeneralTwo(f_integer='10', f_float='20.30')` + nullables
                'two_1_1': {
                    'f_float': 20.3,
                    'f_integer': 10,
                    'one_1_1': None,
                    'one_1_x': {
                        'bulk': [],
                        'defaults': {}
                    }
                },
                # `default_two_1_x = ItemGeneralTwo.Bulk()` with two items:
                # `default_two_1_x.gen(f_integer='20')` and
                # `default_two_1_x.gen(f_float='40.50')` + nullables
                'two_1_x': {
                    'bulk': [
                        {
                            'f_integer': 20,
                            'one_1_1': None,
                            'one_1_x': {
                                'bulk': [],
                                'defaults': {}
                            }
                        },
                        {
                            'f_float': 40.5,
                            'one_1_1': None,
                            'one_1_x': {
                                'bulk': [],
                                'defaults': {}
                            }
                        }
                    ],
                    'defaults': {}
                }
            },
            'bulk': [
                # first item: `bulk.gen(two_1_1__f_integer=40)`
                # + nullables + defaults
                {
                    'f_integer': None,
                    'f_string': None,
                    # exited relation
                    'two_1_1': {
                        'f_integer': 40,
                        'one_1_1': None,
                        'one_1_x': {
                            'bulk': [],
                            'defaults': {}
                        }
                    },
                    # added from default
                    'two_1_x': {
                        'bulk': [
                            {
                                'f_integer': 20,
                                'one_1_1': None,
                                'one_1_x': {
                                    'bulk': [],
                                    'defaults': {}
                                }
                            },
                            {
                                'f_float': 40.5,
                                'one_1_1': None,
                                'one_1_x': {
                                    'bulk': [],
                                    'defaults': {}
                                }
                            }
                        ],
                        'defaults': {}
                    }
                },
                # second item: `bulk.gen(two_1_x__f_text='text-value')`
                # + nullables + defaults
                {
                    'f_integer': None,
                    'f_string': None,
                    # added from default
                    'two_1_1': {
                        'f_float': 20.3,
                        'f_integer': 10,
                        'one_1_1': None,
                        'one_1_x': {
                            'bulk': [],
                            'defaults': {}
                        }
                    },
                    # already existed
                    'two_1_x': {
                        'bulk': [],
                        'defaults': {
                            'f_text': 'text-value'
                        }
                    }
                }
            ]
        }
        self.assertTrue(bulk.to_dict(), expect)

    
    def test_can_create(self):
        self.item_cls_manager.clear()
        class ItemGeneralOne(Item):
            model_cls = self.ModelGeneralOne
            creators = [{'two_1_1', 'f_integer', 'f_string'}]
            getters = [{'f_integer', 'f_string'}]
        
        class ItemGeneralTwo(Item):
            model_cls = self.ModelGeneralTwo
        
        # item one
        item_one = ItemGeneralOne(f_integer=10)
        self.assertFalse(item_one.can_create(fkeys={}))
        item_one['f_string'] = 'str-one'
        self.assertFalse(item_one.can_create(fkeys={}))
        
        # relation (using `True` as fake ORM model value)
        self.assertTrue(item_one.can_create(fkeys={'two_1_1': True}))
        
        # item two (empty creators)
        item_two = ItemGeneralTwo()
        # can create with all fields equal to `None`
        self.assertTrue(item_two.can_create(fkeys={}))
        item_two['f_integer'] = '1000'
        self.assertTrue(item_two.can_create(fkeys={}))
        
        # item one no fkey but has field
        item_one = ItemGeneralOne(f_integer=10, f_string='20',
                                  two_1_1=item_two)
        self.assertFalse(item_one.can_create(fkeys={}))


        # `model_cls is None`
        class TestItem(Item):
            pass
        self.assertIsNone(TestItem.model_cls)
        test_item = TestItem()
        self.assertFalse(test_item.can_create(fkeys={}))
        