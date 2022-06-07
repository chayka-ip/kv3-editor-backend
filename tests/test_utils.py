from unittest import TestCase
from parser_kv3.utils import *


class TestUtils(TestCase):

    def test_get_string_segment_by_characters(self):
        s = '12{345}67'
        result1 = get_max_string_segment_by_characters(s, '{', '}', trim_tips=False)
        result2 = get_max_string_segment_by_characters(s, '{', '}', trim_tips=True)
        self.assertEqual(result1, '{345}')
        self.assertEqual(result2, '345')

        s2 = '12{34567'
        result3 = get_max_string_segment_by_characters(s2, '{', '}', trim_tips=False)
        self.assertEqual(result3, '')

        s3 = '12}34567'
        result4 = get_max_string_segment_by_characters(s3, '{', '}', trim_tips=False)
        self.assertEqual(result4, '')
