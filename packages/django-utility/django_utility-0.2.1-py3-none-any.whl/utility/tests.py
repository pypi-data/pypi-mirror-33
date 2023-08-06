from django.test import TestCase, TransactionTestCase

class FunctionsTest(TransactionTestCase):
    def test_helper(self):
        self.assertEqual(True, False)