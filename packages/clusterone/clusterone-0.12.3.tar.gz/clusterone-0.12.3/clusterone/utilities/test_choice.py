"""
This module is suplementing tests for Choice utility.
Only added functionality is tested because of inheritance.
"""

from .choice import Choice, lazify, lazy_property


def test_generator_evaluation(mocker):
    """
    Sometimes the choice is based on dynamic data that takes a lot of time to aquire, it should be aquired iff necessary.
    """

    long_running_function = mocker.Mock(return_value=['1', '2', '3'])

    def sample_generator():
        for value in long_running_function():
            yield value

    choice = Choice(sample_generator())
    assert not long_running_function.called

    assert choice.choices == ['1','2','3']
    assert long_running_function.called

def test_generator_caching():
    """
    Check if the generator iterator is not exhaused internally but propperly cached.
    """

    def sample_generator():
        for value in ['dummy', 'bunny', 'dummy_bunny']:
            yield value

    choice = Choice(sample_generator())

    # if not cached this would exhaust the iterator
    choice.choices

    assert choice.choices == ['dummy', 'bunny', 'dummy_bunny']


def test_lazify(mocker):

    long_running_function = mocker.Mock(return_value=[1, 2, 3])

    @lazify
    def test_function():
        return long_running_function()

    generator_instance = test_function()
    assert not long_running_function.called

    assert list(generator_instance) == [1, 2, 3]
    assert long_running_function.called


def test_lazy_property():

    RETVAL = [1, 2, 3]

    class Sample():
        @property
        @lazify
        def dummy(self):
            return RETVAL


    class Test():
        @lazy_property
        def dummy(self):
            return RETVAL

    sample, test = Sample(), Test()

    assert list(sample.dummy) == list(test.dummy)
