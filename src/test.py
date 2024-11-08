import sys  

import unittest  
from main import EmailAutomationApp  # Adjust based on your actual import path  
from PyQt6.QtWidgets import (
    QApplication, QLineEdit
)

class TestEmailAutomationApp(unittest.TestCase):  
    
    @classmethod  
    def setUpClass(cls):  
        """Setup QApplication before tests."""  
        cls.app = QApplication(sys.argv)  
        cls.window = EmailAutomationApp()  
        cls.window.show()  

    def test_initial_setup(self):  
        """تست راه‌اندازی اولیه اپلیکیشن"""  
        self.assertEqual(self.window.windowTitle(), "Email Automation Tool")  
        self.assertEqual(self.window.geometry().width(), 800)  
        self.assertEqual(self.window.geometry().height(), 600)  
        self.assertEqual(self.window.tabs.count(), 3)  # تعداد تب‌ها  

    def test_link_extractor_tab_setup(self):  
        """تست اجزای تب استخراج لینک"""  
        tab = self.window.tabs.widget(0)  # تب لینک  
        self.assertIsNotNone(tab)  
        self.assertIsNotNone(tab.layout())  

        search_input = tab.findChild(QLineEdit)  
        self.assertIsNotNone(search_input)  
        self.assertEqual(search_input.placeholderText(), "Enter search query...")  
 

    def test_email_extractor_tab_setup(self):  
        """تست اجزای تب استخراج ایمیل"""  
        tab = self.window.tabs.widget(1)  # تب ایمیل  
        self.assertIsNotNone(tab)  
        self.assertIsNotNone(tab.layout())  

        url_input = tab.findChild(QLineEdit)  
        self.assertIsNotNone(url_input)  
        self.assertEqual(url_input.placeholderText(), "Enter filename containing URLs (e.g., urls.txt)")  


    @classmethod  
    def tearDownClass(cls):  
        """بستن اپلیکیشن بعد از تست‌ها"""  
        cls.window.close()  

if __name__ == "__main__":  
    unittest.main()