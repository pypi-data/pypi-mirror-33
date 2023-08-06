#!/usr/bin/env python
"""Tests for `envi` package."""
import pytest

from envi import get, get_str, get_bool, get_float, get_int


def test_smoke(monkeypatch):
    monkeypatch.setenv('VAR', 'str')
    assert get('VAR', str) == 'str'


def test_not_valid_cast(monkeypatch):
    monkeypatch.setenv('VAR', 'str')
    with pytest.raises(ValueError) as e:
        get('VAR', None)
    assert str(e.value) == 'cast: NoneType is not a callable'


def test_fail_validation(invalid, monkeypatch):
    monkeypatch.setenv('VAR', 'noempty')
    with pytest.raises(AssertionError) as e:
        get('VAR', str, validate=invalid)
    assert str(e.value) == "assert 'noempty' == False"


@pytest.mark.parametrize('test,cast,output', [
    ('False', bool, True),
    ('True', lambda x: x == 'True', True),
    ('False', str, 'False'),
    ('1', int, 1),
    ('3.14', float, 3.14)
])
def test_cast(test, output, cast, argtest, monkeypatch):
    monkeypatch.setenv('VAR', test)
    argtest.casted(cast)
    assert get('VAR', argtest) == output
    assert argtest.arg == test


def test_required():
    with pytest.raises(AttributeError) as e:
        get('VAR', str)
    assert str(e.value) == 'VAR is required'


def test_not_required():
    assert get('STR', str, required=False) is None


def test_required_and_default():
    with pytest.raises(AttributeError) as e:
        get('VAR', str, default=True)
    assert str(e.value) == 'VAR is required'


def test_not_required_and_default():
    assert get('VAR', bool, required=False, default=True) is True


def test_default_ignore_cast():
    assert get('VAR', str, required=False, default=True) is True


def test_fail_invalid_default(invalid):
    with pytest.raises(AssertionError) as e:
        get('VAR', str, required=False, default='noempty', validate=invalid)
    assert str(e.value) == "assert 'noempty' == False"


def test_get_str(monkeypatch):
    monkeypatch.setenv('STR', 'str')
    assert get_str('STR') == 'str'


def test_get_int(monkeypatch):
    monkeypatch.setenv('INT', '1')
    assert get_int('INT') == 1


def test_get_float(monkeypatch):
    monkeypatch.setenv('FLOAT', '1.0')
    assert get_float('FLOAT') == 1.0


@pytest.mark.parametrize('test,output', [
    ('True', True),
    ('False', False),
    ('yes', False),
])
def test_get_bool(test, output, monkeypatch):
    monkeypatch.setenv('TRUE', test)
    assert get_bool('TRUE') is output


@pytest.mark.parametrize('case', ['yes', 'True'])
def test_get_bool_is_ok(case, monkeypatch):
    monkeypatch.setenv('TRUE', case)
    assert get_bool('TRUE', is_ok=['True', 'yes']) is True


def test_missing_different_from_empty(monkeypatch):
    monkeypatch.setenv('VAR', '')

    assert get('VAR', str) == ''
    with pytest.raises(AttributeError) as e:
        get('VAR2', str)
    assert str(e.value) == 'VAR2 is required'
