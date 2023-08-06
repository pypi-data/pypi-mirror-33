from save_to_db.core.item_cls_manager import item_cls_manager
from unittest import TestCase



class TestBase(TestCase):
    
    item_cls_manager = item_cls_manager
    
    @classmethod
    def setUpClass(cls):
        cls.item_cls_manager.clear()
        super().setUpClass()
    
    
    def setUp(self):
        self.item_cls_manager.autogenerate = False
        self.__item_cls_manager_before = \
            set(self.__class__.item_cls_manager._registry)
        super().setUp()
        
    
    def tearDown(self):
        super().tearDown()
        self.__class__.item_cls_manager._registry = \
            self.__item_cls_manager_before
    
    
    def get_all_models(self, model_cls):
        adapter_settings = self.persister.adapter_settings
        adapter_cls = self.persister.adapter_cls
        return adapter_cls.get_all_models(model_cls,
                                          adapter_settings=adapter_settings)