# magnet

A library that makes it easy to load YAML config files in a hierarchical
manner. Also loads YAML content from `CONFIG` environment variable.

**Minimal Python version is Python 3.5.**

# Installation

```bash
pip install magnet
```

# Usage

Consider the following yaml file `config/default.yml`:

```yaml
app:
  url: https://www.example.com/app
  certs:
    pem: /path/to/cert.pem
    key: /path/to/cert.key
  clients:
    - a
    - b
```

And the following `config/local.yml` file:

```yaml
app:
  url: https://app.example.com/
```

```python
from magnet import Config

config = Config().read_all()

config['app.url']           # ==> "https://app.example.com"
config['app.certs.pem']     # ==> "/path/to/cert.pem"
config['non.existing.key']  # ==> raises KeyError
```

## Additional options:

```python
from magnet import Config

# Listed below are the default parameters 
config = Config(
    config={
        # set default configuration here
    },
    filenames=(
       'config/default.yml',
       'config/local.yml',
    ),
    env_variable='CONFIG',
    separator='.',
)

config.read_all(
  filename=None,  # string, can be set to load an additional file
)
```

This will load the configuration in the following order:

1. `./config/default.yml` - can be committed to the repository
2. `./config/local.yml` - should not be committed to allow custom config for devs
3. An additional YAML config file (if `filename` argument is defined)
4. YAML contents from the `CONFIG` environment variable (if `env_variable` is defined)

All of these files are optional, but the key lookups will result with
`KeyError` if a key is missing. If `filename` is defined, but the file is not
found, it will raise a `FileNotFoundError`.

# Development

```
make ci            - Run the CI pipeline (deps, lint, test-coverage)
make lint          - Lint all project files
make test          - Run all tests
make test-watch    - Run all tests and re-run on file changes
make test-coverage - Run all tests and calculate test coverage
make deps          - Create a virtual environment and install dependencies
make freeze        - Freeze the requirements
make env           - Create a virtual environment
```
