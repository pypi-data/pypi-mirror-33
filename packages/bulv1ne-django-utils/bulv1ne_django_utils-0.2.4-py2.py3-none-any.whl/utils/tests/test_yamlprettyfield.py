import yaml

from django import forms
from django.test import TestCase

from ..fields import YAMLPrettyField


class TestForm(forms.Form):
    data_field = YAMLPrettyField(indent=4)


class TestDictForm(forms.Form):
    data_field = YAMLPrettyField(indent=4, dict_only=True)


class TestListForm(forms.Form):
    data_field = YAMLPrettyField(indent=4, list_only=True)


class YAMLPrettyFieldTestCase(TestCase):
    data_dict = 'id: 1\ntest: 2'
    data_list = '- id: 1\n- id: 2'

    def test_indentation(self):
        data = {'id': 1, 'name': {'first': 'Foo', 'last': 'Bar'}}
        form_data = {'data_field': data}
        form = TestForm(initial=form_data)
        self.assertIn(yaml.safe_dump(data, indent=4, default_flow_style=False), form.as_p())

    def test_dict_only_ok(self):
        form_data = {'data_field': self.data_dict}
        form = TestDictForm(form_data)
        self.assertTrue(form.is_valid())

    def test_dict_only_fail(self):
        form_data = {'data_field': self.data_list}
        form = TestDictForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['data_field'], ['Value is not of type dict'])

    def test_list_only_ok(self):
        form_data = {'data_field': self.data_list}
        form = TestListForm(form_data)
        self.assertTrue(form.is_valid())

    def test_list_only_fail(self):
        form_data = {'data_field': self.data_dict}
        form = TestListForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['data_field'], ['Value is not of type list'])

    def test_prepare_value_fail(self):
        form_data = {'data_field': 'a: b, c: d'}
        form = TestForm(form_data)
        self.assertIn('a: b, c: d', form.as_p())
