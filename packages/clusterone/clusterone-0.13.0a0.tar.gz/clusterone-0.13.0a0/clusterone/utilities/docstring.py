def append_to_docstring(text):
    """
    Potentially usefull with Click commands that utilze docstrings as help messages
    """

    def wrapper(function):
        function.__doc__ += text
        return function
    return wrapper
