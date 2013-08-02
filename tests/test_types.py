import pytest

from pypuppetdb.utils import json_to_datetime
from pypuppetdb.types import (
    Node, Fact, Resource,
    Report, Event,
    )

pytestmark = pytest.mark.unit


def test_node():
    node = Node('_', 'node1.puppet.board',
                report_timestamp='2013-08-01T09:57:00.000Z',
                catalog_timestamp='2013-08-01T09:57:00.000Z',
                facts_timestamp='2013-08-01T09:57:00.000Z',
                )
    assert node.name == 'node1.puppet.board'
    assert node.deactivated is False
    assert node.report_timestamp is not None
    assert node.facts_timestamp is not None
    assert node.catalog_timestamp is not None


def test_fact():
    fact = Fact('node1.puppet.board', 'osfamily', 'Debian')
    assert fact.node == 'node1.puppet.board'
    assert fact.name == 'osfamily'
    assert fact.value == 'Debian'


def test_resource():
    resource = Resource('node1.puppet.board', '/etc/ssh/sshd_config', 'file',
                        ['class', 'ssh'], False, '/ssh/manifests/init.pp',
                        15, parameters={
                            'ensure': 'present',
                            'owner': 'root',
                            'group': 'root',
                            'mode': '0600',
                            })
    assert resource.node == 'node1.puppet.board'
    assert resource.name == '/etc/ssh/sshd_config'
    assert resource.type_ == 'file'
    assert resource.tags == ['class', 'ssh']
    assert resource.exported is False
    assert resource.sourcefile == '/ssh/manifests/init.pp'
    assert resource.sourceline == 15
    assert resource.parameters['ensure'] == 'present'
    assert resource.parameters['owner'] == 'root'
    assert resource.parameters['group'] == 'root'
    assert resource.parameters['mode'] == '0600'


def test_report():
    report = Report('node1.puppet.board', 'hash#', '2013-08-01T09:57:00.000Z',
                    '2013-08-01T10:57:00.000Z', '2013-08-01T10:58:00.000Z',
                    '1351535883', 3, '3.2.1')
    assert report.node == 'node1.puppet.board'
    assert report.hash_ == 'hash#'
    assert report.start == json_to_datetime('2013-08-01T09:57:00.000Z')
    assert report.end == json_to_datetime('2013-08-01T10:57:00.000Z')
    assert report.received == json_to_datetime('2013-08-01T10:58:00.000Z')
    assert report.version == '1351535883'
    assert report.format_ == 3
    assert report.agent_version == '3.2.1'
    assert report.run_time == report.end - report.start


def test_event():
    event = Event('node1.puppet.board', 'failure', '2013-08-01T10:57:00.000Z',
                  'hash#', '/etc/ssh/sshd_config', 'ensure', 'Nothing to say',
                  'present', 'absent', 'file')

    assert event.node == 'node1.puppet.board'
    assert event.failed is True
    assert event.timestamp == json_to_datetime('2013-08-01T10:57:00.000Z')
    assert event.hash_ == 'hash#'
    assert event.item['title'] == '/etc/ssh/sshd_config'
    assert event.item['type'] == 'file'
    assert event.item['property'] == 'ensure'
    assert event.item['message'] == 'Nothing to say'
    assert event.item['old'] == 'absent'
    assert event.item['new'] == 'present'
