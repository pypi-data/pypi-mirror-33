# magnet

A library that makes it easy to load and layer config files. Name will probably
need to be changed because I'm sure there's a conflict in PyPI.

# Usage

```python
from magnet import Config

config = Config().read_all('path/to/custom/config/file')
# will result in KeyError if value is missing
value = config['key.subkey.subsubkey']
```

By default, this library will load the config files in order:

1. `./config/default.yml` - can be committed to the repository
2. `./config/local.yml` - should not be committed to allow custom config for devs
3. A custom config YAML file
4. YAML from the `CONFIG` environment variable

All of these files are optional, but the key lookups will result with
`KeyError` if a key is missing.

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
