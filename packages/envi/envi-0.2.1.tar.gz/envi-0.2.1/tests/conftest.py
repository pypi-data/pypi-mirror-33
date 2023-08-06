import pytest


@pytest.fixture
def argtest():
    class TestArgsClass(object):

        cast = str

        def __call__(self, arg):
            self.arg = arg
            return self.cast(arg)

        def casted(self, cast):
            self.cast = cast

    return TestArgsClass()


@pytest.fixture
def invalid():
    def func(case):
        assert case == False

    return func
