import json

import pytest
import requests

from ocdsextensionregistry import Extension, ExtensionVersion


def test_init():
    args = arguments()
    obj = ExtensionVersion(args)

    assert obj.id == args['Id']
    assert obj.date == args['Date']
    assert obj.version == args['Version']
    assert obj.base_url == args['Base URL']
    assert obj.download_url == args['Download URL']


def test_update():
    obj = ExtensionVersion(arguments())
    obj.update(Extension({'Id': 'location', 'Category': 'item', 'Core': 'true'}))

    assert obj.id == 'location'
    assert obj.category == 'item'
    assert obj.core is True


def test_update_ignore_private_properties():
    obj = ExtensionVersion(arguments())
    other = ExtensionVersion(arguments())
    other._file_cache['key'] = 'value'
    obj.update(other)

    assert obj._file_cache == {}


def test_as_dict():
    args = arguments()
    obj = ExtensionVersion(args)

    assert obj.as_dict() == {
        'id': args['Id'],
        'date': args['Date'],
        'version': args['Version'],
        'base_url': args['Base URL'],
        'download_url': args['Download URL'],
    }


def test_remote():
    obj = ExtensionVersion(arguments(**{'Download URL': None}))
    data = obj.remote('extension.json')
    # Repeat requests should return the same result.
    data = obj.remote('extension.json')

    assert json.loads(data)


def test_remote_download_url():
    obj = ExtensionVersion(arguments())
    data = obj.remote('extension.json')
    # Repeat requests should return the same result.
    data = obj.remote('extension.json')

    assert json.loads(data)


def test_remote_nonexistent():
    obj = ExtensionVersion(arguments(**{'Download URL': None}))
    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        obj.remote('nonexistent')

    assert str(excinfo.value) == "404 Client Error: Not Found for url: https://raw.githubusercontent.com/open-contracting/ocds_location_extension/v1.1.3/nonexistent"  # noqa


def test_remote_download_url_nonexistent():
    obj = ExtensionVersion(arguments())
    with pytest.raises(KeyError) as excinfo:
        obj.remote('nonexistent')

    assert str(excinfo.value) == "'nonexistent'"


def test_metadata():
    obj = ExtensionVersion(arguments())
    result = obj.metadata

    assert 'name' in result
    assert 'description' in result


def test_repository_full_name():
    obj = ExtensionVersion(arguments())
    result = obj.repository_full_name

    assert result == 'open-contracting/ocds_location_extension'


def test_repository_name():
    obj = ExtensionVersion(arguments())
    result = obj.repository_name

    assert result == 'ocds_location_extension'


def test_repository_html_page():
    obj = ExtensionVersion(arguments())
    result = obj.repository_html_page

    assert result == 'https://github.com/open-contracting/ocds_location_extension'


def test_repository_url():
    obj = ExtensionVersion(arguments())
    result = obj.repository_url

    assert result == 'git@github.com:open-contracting/ocds_location_extension.git'


def arguments(**kwargs):
    data = {
        'Id': 'location',
        'Date': '2018-02-01',
        'Version': 'v1.1.3',
        'Base URL': 'https://raw.githubusercontent.com/open-contracting/ocds_location_extension/v1.1.3/',
        'Download URL': 'https://api.github.com/repos/open-contracting/ocds_location_extension/zipball/v1.1.3',
    }

    data.update(kwargs)
    return data
