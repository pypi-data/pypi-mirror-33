import unittest

from sieve.sdk.collections.document import NullableList, Document


class NullableListTests(unittest.TestCase):
    def test_deleting_an_item_makes_the_index_position_value_to_be_None(self):
        list_ = NullableList(('Xablau', 666, 'Xena'))
        del list_[1]
        assert list_ == ['Xablau', None, 'Xena']

    def test_it_deletes_items_by_index_string_representation(self):
        list_ = NullableList(('Xablau', 666, 'Xena'))
        del list_['1']
        assert list_ == ['Xablau', None, 'Xena']

    def test_its_possible_to_access_indexes_by_string_representation(self):
        list_ = NullableList(('Xablau', 666, 'Xena'))

        assert list_[0] == 'Xablau'
        assert list_['0'] == 'Xablau'


class DocumentTests(unittest.TestCase):
    def test_it_creates_elemets_if_path_doesnt_exists(self):
        doc = Document()
        doc['dogs.male'] = 'Xablau'

        assert doc == {'dogs': {'male': 'Xablau'}}

    def test_list_items_are_typecasted_to_NullableList_instances(self):
        doc = Document()
        doc['dogs'] = ['Xablau', 'Xena']

        assert isinstance(doc['dogs'], NullableList)
        assert doc == {'dogs': ['Xablau', 'Xena']}
