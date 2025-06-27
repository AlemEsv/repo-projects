import json
import pytest
import os

# Get the directory where this test file is located
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(TEST_DIR, 'network_config.json')

@ pytest.fixture(scope="module")
def conf():
    return json.load(open(CONFIG_FILE))

def test_schema_keys(conf):
    assert isinstance(conf, dict)
    assert 'resources' in conf
    for res in conf['resources']:
        assert 'type' in res and 'name' in res
