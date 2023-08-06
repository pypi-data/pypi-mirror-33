from .config import Config
import pytest
import tempfile


@pytest.fixture
def filename1():
    file = tempfile.NamedTemporaryFile(delete=False)
    yield file.name
    file.close()


@pytest.fixture
def filename2():
    file = tempfile.NamedTemporaryFile(delete=False)
    yield file.name
    file.close()


def test_read_no_file():
    Config().read('/path/to/non/existing/file')


def test_load_env(monkeypatch):
    monkeypatch.setenv('CONFIG', '---\na: b\nc: d\ne:\n  f:\n    - g')
    c = Config().load_env()
    assert c['a'] == 'b'
    assert c['c'] == 'd'
    assert c['e.f'] == ['g']


def test_read_no_file_fail(filename1, filename2):
    with pytest.raises(FileNotFoundError):
        Config().read('/path/to/non/existing/file', fail=True)


def test_read_single_file(filename1):
    with open(filename1, 'w') as file:
        file.write("""---
deeply:
    nested:
        key: test
""")
    config = Config().read(filename1)
    assert config['deeply.nested.key'] == 'test'
    with pytest.raises(KeyError):
        config['invalid.key']


def test_read_multiple_files(filename1, filename2):
    with open(filename1, 'w') as file:
        file.write("""---
keys:
    key1: 1234
    key2:
        a: 1
""")
    with open(filename2, 'w') as file:
        file.write("""---
keys:
    key1:
        value: 'test'
    key2:
        b: 2
""")

    config = Config().read(filename1).read(filename2)
    assert config['keys.key1'] == {'value': 'test'}
    assert config['keys.key2'] == {'a': 1, 'b': 2}


def test_read_all(filename1, monkeypatch):
    with open(filename1, 'w') as file:
        file.write("""---
keys:
    key4: test4
""")

    monkeypatch.setenv('CONFIG', """---
keys:
    key1: test1
    key2: 2
""")

    config = Config().read_all(filename1)
    assert config._config == {
        'keys': {
            'key1': 'test1',
            'key2': 2,
            'key3': 3,
            'key4': 'test4',
        }
    }


def test_read_all_no_filename_no_env():
    config = Config().read_all()
    assert config._config == {
        'keys': {
            'key2': ['a', 'b'],
            'key3': 3,
        }
    }


def test_str():
    assert repr(Config()) == 'Config[_config={}]'
