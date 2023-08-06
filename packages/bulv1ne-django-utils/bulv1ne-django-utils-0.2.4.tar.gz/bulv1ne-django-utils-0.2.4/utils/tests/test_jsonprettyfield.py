import json

from django import forms
from django.test import TestCase
from django.utils.html import escape

from ..fields import JSONPrettyField


class TestForm(forms.Form):
    data_field = JSONPrettyField(indent=4)


class TestDictForm(forms.Form):
    data_field = JSONPrettyField(indent=4, dict_only=True)


class TestListForm(forms.Form):
    data_field = JSONPrettyField(indent=4, list_only=True)


class JSONPrettyFieldTestCase(TestCase):
    def test_indentation(self):
        data = [{'id': 1}, {'id': 2}]
        form_data = {'data_field': json.dumps(data)}
        form = TestForm(form_data)
        self.assertIn(escape(json.dumps(data, indent=4)), form.as_p())

    def test_dict_only_ok(self):
        data = {'id': 1}
        form_data = {'data_field': json.dumps(data)}
        form = TestDictForm(form_data)
        self.assertTrue(form.is_valid())

    def test_dict_only_fail(self):
        data = [{'id': 1}, {'id': 2}]
        form_data = {'data_field': json.dumps(data)}
        form = TestDictForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['data_field'], ['Value is not of type dict'])

    def test_list_only_ok(self):
        data = [{'id': 1}, {'id': 2}]
        form_data = {'data_field': json.dumps(data)}
        form = TestListForm(form_data)
        self.assertTrue(form.is_valid())

    def test_list_only_fail(self):
        data = {'id': 1}
        form_data = {'data_field': json.dumps(data)}
        form = TestListForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['data_field'], ['Value is not of type list'])

    def test_dict_and_list(self):
        with self.assertRaises(ValueError):
            JSONPrettyField(dict_only=True, list_only=True)

    def test_prepare_value_fail(self):
        form_data = {'data_field': 'invalid'}
        form = TestForm(form_data)
        self.assertIn('invalid', form.as_p())
