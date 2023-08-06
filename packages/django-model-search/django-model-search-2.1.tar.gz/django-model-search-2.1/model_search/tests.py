
from django.test import TestCase
from django.core.management import call_command


from model_search import normalize_query


class SearchTestCase(TestCase):

    def setUp(self):
        call_command('sync_translation_fields', interactive=False)

    def test_normalize_query_returns_words_list(self):

        query = '  some random  words "with   quotes  " and   spaces'

        result = ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

        self.assertEqual(normalize_query(query), result)
