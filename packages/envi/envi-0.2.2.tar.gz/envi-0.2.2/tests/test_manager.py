#!/usr/bin/env python
"""Tests for `envi` package."""
import pytest
from envi.manager import EnviManager, EnviType, EnviNotConfigured, EnviAlreadyConfigured
import json


def test_bridge_str(monkeypatch):
    monkeypatch.setenv('VAR', 'str')

    class EnviBridge(EnviManager):
        VAR = EnviType.string()

    EnviBridge.configure()
    assert EnviBridge().VAR == 'str'
    assert type(EnviBridge().VAR) == str


def test_bridge_int(monkeypatch):
    monkeypatch.setenv('VAR', '123')

    class EnviBridge(EnviManager):
        VAR = EnviType.integer()

    EnviBridge.configure()
    assert EnviBridge().VAR == 123
    assert type(EnviBridge().VAR) == int


def test_bridge_int_error(monkeypatch):
    monkeypatch.setenv('VAR', 'asd')

    class EnviBridge(EnviManager):
        VAR = EnviType.integer()

    with pytest.raises(ValueError) as e:
        EnviBridge.configure()
    assert str(e.value) == "invalid literal for int() with base 10: 'asd'"


def test_bridge_float(monkeypatch):
    monkeypatch.setenv('VAR', '1.1231412')

    class EnviBridge(EnviManager):
        VAR = EnviType.float()

    EnviBridge.configure()
    assert EnviBridge().VAR == 1.1231412
    assert type(EnviBridge().VAR) == float


def test_bridge_float_error(monkeypatch):
    monkeypatch.setenv('VAR', '1.asdad')

    class EnviBridge(EnviManager):
        VAR = EnviType.float()

    with pytest.raises(ValueError) as e:
        EnviBridge.configure()
    assert str(e.value) == "could not convert string to float: '1.asdad'"


def test_bridge_bool(monkeypatch):
    monkeypatch.setenv('VAR', 'True')

    class EnviBridge(EnviManager):
        VAR = EnviType.bool()

    EnviBridge.configure()
    assert EnviBridge().VAR is True
    assert type(EnviBridge().VAR) == bool


def test_bridge_bool_false(monkeypatch):
    monkeypatch.setenv('VAR', 'False')

    class EnviBridge(EnviManager):
        VAR = EnviType.bool()

    EnviBridge.configure()
    assert EnviBridge().VAR is False
    assert type(EnviBridge().VAR) == bool


def test_bridge_bool_anything(monkeypatch):
    monkeypatch.setenv('VAR', 'anything')

    class EnviBridge(EnviManager):
        VAR = EnviType.bool()

    EnviBridge.configure()
    assert EnviBridge().VAR is False
    assert type(EnviBridge().VAR) == bool


def test_bridge_generic(monkeypatch):
    monkeypatch.setenv('VAR', '{"test": "json"}')

    class EnviBridge(EnviManager):
        VAR = EnviType.generic(cast=json.loads)

    EnviBridge.configure()
    assert type(EnviBridge().VAR) == dict
    assert EnviBridge().VAR.get("test") == "json"


def test_bridge_validate_ok(monkeypatch):
    monkeypatch.setenv('VAR', '9')

    def lower_than_10(value):
        if value > 10:
            raise ValueError("Bigger then 10")

    class EnviBridge(EnviManager):
        VAR = EnviType.integer(validate=lower_than_10)

    EnviBridge.configure()
    assert EnviBridge().VAR == 9
    assert type(EnviBridge().VAR) == int


def test_bridge_validate_bad(monkeypatch):
    monkeypatch.setenv('VAR', '12')
    msg = "Bigger then 10"

    def lower_than_10(value):
        if value > 10:
            raise ValueError(msg)

    class EnviBridge(EnviManager):
        VAR = EnviType.integer(validate=lower_than_10)

    with pytest.raises(ValueError) as e:
        EnviBridge.configure()
    assert str(e.value) == msg


def test_bridge_required_ok(monkeypatch):
    monkeypatch.setenv('VAR', 'test')

    class EnviBridge(EnviManager):
        VAR = EnviType.string(required=True)

    EnviBridge.configure()
    assert EnviBridge().VAR == 'test'


def test_bridge_not_required():
    class EnviBridge(EnviManager):
        VAR = EnviType.string(required=False)

    EnviBridge.configure()
    assert EnviBridge().VAR is None


def test_bridge_required_bad():
    class EnviBridge(EnviManager):
        VAR = EnviType.string(required=True)

    with pytest.raises(AttributeError) as e:
        EnviBridge.configure()
    assert str(e.value) == "VAR is required"


def test_bridge_default():
    class EnviBridge(EnviManager):
        VAR = EnviType.string(required=False, default="test")

    EnviBridge.configure()
    assert EnviBridge().VAR == "test"


def test_bridge_custom_is_ok(monkeypatch):
    monkeypatch.setenv('VAR1', 'True')
    monkeypatch.setenv('VAR2', 'true')
    monkeypatch.setenv('VAR3', 'true')
    monkeypatch.setenv('VAR4', 'True')
    monkeypatch.setenv('VAR5', 'False')

    class EnviBridge(EnviManager):
        VAR1 = EnviType.bool(is_ok=["True"])
        VAR2 = EnviType.bool(is_ok=["true"])
        VAR3 = EnviType.bool(is_ok=["True"])
        VAR4 = EnviType.bool(is_ok=["true"])
        VAR5 = EnviType.bool(is_ok=["true", "True"])

    EnviBridge.configure()
    assert EnviBridge().VAR1 is True
    assert EnviBridge().VAR2 is True
    assert EnviBridge().VAR3 is False
    assert EnviBridge().VAR4 is False
    assert EnviBridge().VAR5 is False


def test_bridge_bad_name(monkeypatch):
    monkeypatch.setenv('VAR', 'True')

    class EnviBridge(EnviManager):
        VAR = EnviType.bool()

    EnviBridge.configure()
    with pytest.raises(AttributeError) as e:
        getattr(EnviBridge(), "VAR2")
    assert str(e.value) == "'EnviBridge' object has no attribute 'VAR2'"


def test_bridge_no_conf(monkeypatch):
    monkeypatch.setenv('VAR', 'True')

    class EnviBridge(EnviManager):
        pass

    EnviBridge.configure()
    with pytest.raises(AttributeError) as e:
        getattr(EnviBridge(), "VAR")
    assert str(e.value) == "'EnviBridge' object has no attribute 'VAR'"


def test_bridge_no_envitype_attribute(monkeypatch):
    monkeypatch.setenv('VAR', 'True')

    class EnviBridge(EnviManager):
        VAR = "testing"

    EnviBridge.configure()
    assert EnviBridge().VAR == "testing"


def test_bridge_doesnt_evaluate_callables(monkeypatch):
    monkeypatch.setenv('VAR', 'True')

    class EnviBridge(EnviManager):
        VAR = EnviType.bool()

        def callable(self):
            return "callable"

        @classmethod
        def callable2(cls):
            return "callable2"

    EnviBridge.configure()
    assert EnviBridge().VAR is True
    assert EnviBridge().callable() == "callable"
    assert EnviBridge.callable2() == "callable2"


def test_inheritance(monkeypatch):
    monkeypatch.setenv('VAR1', 'True')
    monkeypatch.setenv('VAR2', 'True')

    class EnviBridge(EnviManager):
        VAR1 = EnviType.string()

    class EnviBridgeInheriting(EnviBridge):
        VAR2 = EnviType.bool()

    EnviBridgeInheriting.configure()
    assert EnviBridgeInheriting().VAR1 == "True"
    assert EnviBridgeInheriting().VAR2 is True
    with pytest.raises(EnviNotConfigured):
        EnviBridge()


def test_override(monkeypatch):
    monkeypatch.setenv('VAR1', 'True')
    monkeypatch.setenv('VAR2', 'True')

    class EnviBridge(EnviManager):
        VAR1 = EnviType.string()

    class EnviBridgeInheriting(EnviBridge):
        VAR1 = EnviType.bool()
        VAR2 = EnviType.bool()

    EnviBridgeInheriting.configure()
    assert EnviBridgeInheriting().VAR1 is True
    assert EnviBridgeInheriting().VAR2 is True
    EnviBridge.configure()
    with pytest.raises(AttributeError) as e:
        getattr(EnviBridge(), 'VAR2')
    assert str(e.value) == "'EnviBridge' object has no attribute 'VAR2'"


def test_two_configure(monkeypatch):
    monkeypatch.setenv('VAR', 'True')

    class EnviBridge(EnviManager):
        VAR = EnviType.bool()

    EnviBridge.configure()
    assert EnviBridge().VAR is True
    with pytest.raises(EnviAlreadyConfigured):
        EnviBridge.configure()


def test_not_configured(monkeypatch):
    monkeypatch.setenv('VAR', 'True')

    class EnviBridge(EnviManager):
        VAR = EnviType.bool()

    with pytest.raises(EnviNotConfigured):
        EnviBridge()


def test_is_singleton(monkeypatch):
    monkeypatch.setenv('VAR', 'True')

    class EnviBridge(EnviManager):
        VAR = EnviType.bool()

    EnviBridge.configure()
    env1 = EnviBridge()
    env2 = EnviBridge()
    assert env1 is env2


def test_no_config_inheritance(monkeypatch):
    monkeypatch.setenv('VAR1', 'True')
    monkeypatch.setenv('VAR2', 'True')

    class EnviBridge(EnviManager):
        VAR1 = EnviType.string()

    EnviBridge.configure()
    assert EnviBridge().VAR1 == "True"

    class EnviBridgeInheriting(EnviBridge):
        VAR1 = EnviType.bool()
        VAR2 = EnviType.bool()

    assert EnviBridgeInheriting.is_configured() is False
    EnviBridgeInheriting.configure()
    assert EnviBridgeInheriting().VAR1 is True
    assert EnviBridgeInheriting().VAR2 is True
    assert EnviBridge().VAR1 == "True"


def test_is_configured(monkeypatch):
    monkeypatch.setenv('VAR1', 'True')

    class EnviBridge(EnviManager):
        VAR1 = EnviType.string()

    assert EnviBridge.is_configured() is False
    EnviBridge.configure()
    assert EnviBridge.is_configured() is True
