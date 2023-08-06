import pytest

import licenraptor
from licenraptor import base
from licenraptor.licenses import MITLicense


KEYS = ('rpm', 'name', 'python', 'url')


class TestRegisterFind(object):
    '''
    Test register() and find()
    '''

    @classmethod
    def teardown_class(cls):
        del licenraptor.core._db['FOO']

    def test_register_no_id(self):
        '''
        Test that License classes cannot be registered without id
        '''
        class FooLicense(base.License):
            pass

        with pytest.raises(AttributeError):
            licenraptor.register(FooLicense)

    def test_register_and_find(self):
        '''
        Test that License classes can be registered with id
        '''
        class FooLicense(base.License):
            id = 'FOO'

        licenraptor.register(FooLicense)
        assert licenraptor.find('FOO') == FooLicense

    def test_nonexisting(self):
        '''
        Test that non-existing license cannot be found
        '''
        with pytest.raises(KeyError):
            licenraptor.find('This is not an existing SPDX identifier')

    @pytest.mark.parametrize('id', ('MIT',))
    def test_exisitng(self, id):
        '''
        Test that an exisitng license can be found
        '''
        assert licenraptor.find(id).id == id


class TestFindByFunction(object):
    '''
    Tests for find_by_function()
    '''

    @pytest.mark.parametrize('multiple', (True, False))
    def test_find_by_true(self, multiple):
        result = licenraptor.find_by_function(lambda x: True, multiple)
        assert result

    def test_find_by_false_multiple(self):
        results = licenraptor.find_by_function(lambda x: False, multiple=True)
        assert results == []

    def test_find_by_false_single(self):
        with pytest.raises(KeyError):
            result = licenraptor.find_by_function(
                lambda x: False, multiple=False)

    def test_find_by_function_is_equal(self):
        result = licenraptor.find_by_function(
            lambda x: x == MITLicense, multiple=False)
        assert result == MITLicense

    @pytest.mark.parametrize(('text', 'res'), (('license', True), ('foobar', False)))
    def test_find_by_function_lower_endswith(self, text, res):
        results = licenraptor.find_by_function(
            lambda x: x.name.lower().endswith(text), multiple=True)
        assert (MITLicense in results) == res


class TestFindByKeyWithoutIndex(object):
    '''
    Tests for find_by_key() when no index has been built
    '''

    @pytest.mark.parametrize('key', KEYS)
    def test_find_by_key_multiple(self, key):
        '''
        Test that it is possible to find the license by various keys
        '''
        value = getattr(MITLicense, key)
        results = licenraptor.find_by_key(key, value)
        assert results == [MITLicense]

    @pytest.mark.parametrize('key', KEYS)
    def test_find_by_key_single(self, key):
        '''
        Test that it is possible to find the license by various keys
        '''
        value = getattr(MITLicense, key)
        result = licenraptor.find_by_key(key, value, multiple=False)
        assert result == MITLicense

    @pytest.mark.parametrize('key', KEYS)
    def test_find_by_key_multiple_wrong(self, key):
        '''
        Test that when finding multiple results, empty list is returned when nothing found
        '''
        value = 'nonexistent value'
        results = licenraptor.find_by_key(key, value)
        assert results == []

    @pytest.mark.parametrize('key', KEYS)
    def test_find_by_key_single_wrong(self, key):
        '''
        Test that when finding single result, KeyError is risen when nothing found
        '''
        value = 'nonexistent value'
        with pytest.raises(KeyError):
            result = licenraptor.find_by_key(key, value, multiple=False)

    def test_bsd_finds_multiple(self):
        '''
        Test that searching for BSD in rpm key return at least two results
        '''
        results = licenraptor.find_by_key('rpm', 'BSD')
        assert len(results) >= 2


class TestFindByKeyWithIndex(TestFindByKeyWithoutIndex):
    '''
    Tests for find_by_key() when the index has been built
    '''

    @classmethod
    def setup_class(cls):
        for key in KEYS:
            licenraptor.build_index(key)

    @classmethod
    def teardown_class(cls):
        for key in KEYS:
            licenraptor.delete_index(key)


class TestIter(object):
    '''
    Tests for the iter() function
    '''

    def test_iter(self):
        for cls in licenraptor.iter():
            pass
