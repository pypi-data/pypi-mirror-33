# Clusterone CLI

![](https://drone.shared.tools.clusterone.com/api/badges/clusterone/cli/status.svg)

## Installation

0. Clone repository

```sh
    git clone git@github.com:clusterone/cli.git
```

If this step does not work for you than please [connect to Github with SSH](https://help.github.com/articles/connecting-to-github-with-ssh/). 

1. Change directory to CLI folder 
```sh
    cd cli
```

2. Create a virtualenv

```sh
   python3 -m venv env 
```

3. Activate the virtualenv
```sh
    . env/bin/activate
```

4. Install project dependencies and dev dependencies

```sh
    pip install -e .[dev]
```

Or for zshell users:

```sh
    echo "pip install -e .[dev]" | bash
```


## Working

0. Run work script, this will:
- activate the virtualenv
- set PYTHONPATH
- alias `just` as the package under dev

```sh
    source workon.sh
```

## Testing

### Units
```sh
    pytest
```

### E2E

```sh
    python -m clusterone.functional_test 
```

Caution: E2Es are to be run from main directory

#### Docker

The images are built and pushed to Quay by the CI automatically, for manual process please do the following:

- Building
```sh
    docker build -t just_end_to_end -f clusterone/functional_test/Dockerfile .
```

Caution: E2Es are to be built from main directory

- Running
```sh
    docker run just_end_to_end
```

##### Running prebuilt version

Please bare in mind that this requires aproperiate Quay credentials

```bash
    docker pull quay.io/tensorport/just_end_to_end:latest
    docker run quay.io/tensorport/just_end_to_end:latest
```

### Mocks

Long mocking literals are stored in `clusterone/mocks`

## Connecting to local main app

```
    just config endpoint http://localhost:8000
```

- Bare in mind this is persistent

## Verbose logging 

```
    export JUST_DEBUG=True
```

- Enable verbose print messages for every request made
- Works for "true" in any case, so "TRUE", "true", "True", "TrUe" are all valid values
- Any other values are considered falsy

## For copywriters 

Be aware that Click framework is sometimes messing the docstring formatting.

### Workflow

- Follow the installation and working instructions 
- Branch from master branch, make sure you're up to date
```bash
    git checkout master
    git pull
    git checkout -b [branchname]
    git push -u origin [branchname]
```
- Do the work
- Create a PR on Github
- Dev team will review, merge and deploy

### Locating the copytext

#### Helptexts

Docstring of `command` function located in  `./clusterone/commands/[command]/[*subcommand]/cmd.py`

Example:
- `./clusterone/commands/get/project/cmd.py`

#### Options helptext

As a `click.option` decorator of `command`. The text is the contents of the `help` kwarg.

#### Most of the error texts

Located in `./clusterone/client_exceptions.py` as a return value of `__str__` method of each exception.

#### Everything else

You'd have to search the codebase and edit matching string literal.

### Caveats

- `just create job` commands family is utilizing common arguments via `base_cmd.py`
- Sometimes the `append_to_docstring` decorator is utilized in order to add to docstring (dynamic data or argument-like mechanisms that lack other way to document them)

## Caution

### Adding new commands

Whenever new command is added please make sure that your it's propperly imported all the way up to `commands` module. We have a test for that, so no worries, just keep that in mind.

Example:
`commands/__init__.py` import `create`, which in it's own `__init__.py` import `project`, which imports `command` from `cmd.py`

### Dependency hell

Clusterone projects depend on `get_data_path()` and `get_logs_path()` from the `clusterone_client` package. We have a test for that, so no worries, just keep that in mind. 

### Passwords in plaintext

ONE. DOES. NOT. SIMPLY. STORE. PASSWORDS. IN. PLAINTEXT. NO. NEVER.

### Global instances

There are global instances used across the CLI of:
- Clusterone client
- Config (persistent between session)
- Session (persistent between invocation)

### Versioning

We follow [semantic versioning](https://semver.org/).
Before new version release please upgrade version number in `clusterone/__init__.py` 

### Files utilized

- `session.json` in `~/.config/clusterone`
- `justrc.json` in `~/.config/clusterone` (or equivalent on platform other than GNU/Linux)

## Linting and style

### EditorConfig

Please make sure that your editor supports editor config.
Visit [EditorConfig webiste](editorconfig.org/) for details.

### Pylint

Please make sure that you have installed `pylint` on your system 

When to run? TBD
Config? TBD

## Additional naming conventions and note about folder structure

Virtualenv for Python 3 shall is to be named `env`  
Virtualenv for Python 2.7 shall it be needed is to be named `env27`

All commands shall have a corresponding `cmd.py` file located in `clusterone/commands/([subcommand]/)*/command/`
If additional code [more than few lines and a just client call] is needed for implementing given functionality than a `helper.py` should be utilised and the client call moved to it

`cmd.py` must  contain `command` function that is a click command   
If `helper.py` exists it must contain `main` function that is to be called by `command` from `cmd.py`

### Example

`just create project [args]` has a `cmd.py` located in `clusterone/commands/create/project/`
Additional code is needed for ensuring that tport git remote is created for a project, therefore `helper.py` exists in the same location

## Deployment

Is performed by the CI, yet - manual trigger is required for the process to start.

### Triggering deployment

0. Please make sure you're at the feature branch from which you'd like to deploy.
1. Increment version in `clusterone/__init__.py` - see [versioning section](#versioning) for details
2. Run `./deployment/tag_version.sh` and verify that the output on the screen matches the desired version
3. Run `./deployment/push_version_tag.sh`

## CI

See `drone.yml`
