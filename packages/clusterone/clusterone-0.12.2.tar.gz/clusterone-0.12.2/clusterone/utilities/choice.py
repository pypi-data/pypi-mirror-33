import click


def lazify(function):
    """
    A decorator transforming function returning an iterable into generator

    Extremely usefull is the list is constructed based on request
    """

    def generator(*args, **kwargs):
        for item in function(*args, **kwargs):
            yield item

    return generator


def lazy_property(function):
    """
    Convinience wrapper: combines @property and @lazify
    """

    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return property(lazify(wrapper))


class Choice(click.Choice):
    """
    Extends click.Choice so that a generator iterator can be passed
    The generator is evaluated only once and only when needed
    """

    def __init__(self, choices):
        """
        Adds indirection level to hook into values lookup
        The super() is not called deliberately
        """

        self._choices = choices

    @property
    def choices(self):
        # type: () -> [str]
        #TODO: Move this to function signature when dropping Python 2.7 compliance
        """
        Caching generator as a list
        """

        self._choices = list(self._choices)

        return self._choices
