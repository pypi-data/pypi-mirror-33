from .docstring import append_to_docstring

@append_to_docstring("dummy")
def dummy_function():
    """
    Sample docstring
    """

    pass

def test_docstring_appending(mocker):
    assert dummy_function.__doc__ == "\n    Sample docstring\n    dummy"
