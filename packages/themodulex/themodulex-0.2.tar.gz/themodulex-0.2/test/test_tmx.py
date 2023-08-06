from unittest import TestCase
import themodulex

class TestTMX (TestCase):
	def test_is_str(self):
		s =  str(themodulex)
		self.assertTrue(isinstance(s, str))

