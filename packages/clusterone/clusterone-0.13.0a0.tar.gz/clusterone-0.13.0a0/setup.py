import re as regexp

from setuptools import setup, find_packages


def get_version():
    """
    Aquires version number from insdie the package without utilising Python import

    When installing clusterone from pypi the clusterone python package does not yet
    exist, causing the imports to fail. Yet, this script has access to sourcefiles
    of the project allowing to extract the __version__ info in another way.

    This was tested on Centos, Fedora, Ubuntu Server 14.04 and Windows
    """
    # type: () -> str
    # TODO: Move this to function signature after removing Python 2.7 compliance

    result = regexp.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format("__version__"), open("clusterone/__init__.py").read())
    return result.group(1)


def main():
    setup(
        name='clusterone',
        version=get_version(),
        py_modules=[
            'clusterone'
        ],
        packages=find_packages(),
        include_package_data=True,
        # The lowest supported Python 3 version is 3.5
        # please update accordingly iff changes
        python_requires=">2.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4",
        install_requires=[
            'click',
            'py',
            'coreapi-cli==1.0.9',
            'gitpython',
            'raven',
            'terminaltables',
            'click_log==0.1.8',
            'virtualenv',
            'six',
            # patches Enum functionality for Python 2.7
            'enum34',
        ],
        extras_require={
            'dev': [
                'pytest',
                'pytest-mock',
            ]
        },
        entry_points='''
            [console_scripts]
            just=clusterone.clusterone_cli:main
        ''',

        author="Clusterone",
        author_email="info@clusterone.com",
        description="Clusterone CLI and Python library.",
        license="MIT",
        keywords="",
        url="https://clusterone.com",
    )


if __name__ == "__main__":
    main()
