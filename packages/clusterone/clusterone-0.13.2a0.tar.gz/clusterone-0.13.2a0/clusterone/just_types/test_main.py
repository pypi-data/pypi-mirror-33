from click import ParamType
from . import main


def test_subclassing():
    assert issubclass(main.Notebook, ParamType)


def test_notebook_acquisition(mocker):
    main.JustNotebook = mocker.Mock()

    main.Notebook.convert(main.Notebook.__new__(main.Notebook), "elorap", "", "")

    main.JustNotebook.from_clusterone.assert_called_with(mocker.ANY, "elorap")
