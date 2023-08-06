import pytest
from publisher import Publisher


def test_project_must_exists():
    client = Publisher('merlin-qa')

    assert isinstance(client, Publisher)


def test_instance_without_project_must_fail():
    with pytest.raises(Exception):
        Publisher()
