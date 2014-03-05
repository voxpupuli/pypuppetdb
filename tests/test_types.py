import sys

from pypuppetdb.utils import json_to_datetime
from pypuppetdb.types import (
    Node, Fact, Resource,
    Report, Event, Catalog, Edge
    )

if sys.version_info >= (3, 0):
    unicode = str


class TestNode(object):
    """Test the Node object."""
    def test_without_status(self):
        node = Node('_', 'node',
                    report_timestamp='2013-08-01T09:57:00.000Z',
                    catalog_timestamp='2013-08-01T09:57:00.000Z',
                    facts_timestamp='2013-08-01T09:57:00.000Z',)

        assert node.name == 'node'
        assert node.deactivated is False
        assert node.report_timestamp is not None
        assert node.facts_timestamp is not None
        assert node.catalog_timestamp is not None
        assert str(node) == str('node')
        assert unicode(node) == unicode('node')
        assert repr(node) == str('<Node: node>')

    def test_with_status_unreported(self):
        node = Node('_', 'node',
                    report_timestamp='2013-08-01T09:57:00.000Z',
                    catalog_timestamp='2013-08-01T09:57:00.000Z',
                    facts_timestamp='2013-08-01T09:57:00.000Z',
                    status='unreported',
                    unreported_time='0d 5h 20m',)

        assert node.name == 'node'
        assert node.deactivated is False
        assert node.report_timestamp is not None
        assert node.facts_timestamp is not None
        assert node.catalog_timestamp is not None
        assert node.status is 'unreported'
        assert node.unreported_time is '0d 5h 20m'
        assert str(node) == str('node')
        assert unicode(node) == unicode('node')
        assert repr(node) == str('<Node: node>')


class TestFact(object):
    """Test the Fact object."""
    def test_fact(self):
        fact = Fact('node', 'osfamily', 'Debian')

        assert fact.node == 'node'
        assert fact.name == 'osfamily'
        assert fact.value == 'Debian'
        assert str(fact) == str('osfamily/node')
        assert unicode(fact) == unicode('osfamily/node')
        assert repr(fact) == str('Fact: osfamily/node')


class TestResource(object):
    "Test the Resource object."""

    def test_resource(self):
        resource = Resource('node', '/etc/ssh/sshd_config', 'file',
                            ['class', 'ssh'], False, '/ssh/manifests/init.pp',
                            15, parameters={
                                'ensure': 'present',
                                'owner': 'root',
                                'group': 'root',
                                'mode': '0600',
                                })

        assert resource.node == 'node'
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
        assert str(resource) == str('file[/etc/ssh/sshd_config]')
        assert unicode(resource) == unicode('file[/etc/ssh/sshd_config]')
        assert repr(resource) == str(
            '<Resource: file[/etc/ssh/sshd_config]>')


class TestReport(object):
    """Test the Report object."""
    def test_report(self):
        report = Report('_', 'node1.puppet.board', 'hash#',
                        '2013-08-01T09:57:00.000Z',
                        '2013-08-01T10:57:00.000Z',
                        '2013-08-01T10:58:00.000Z',
                        '1351535883', 3, '3.2.1',
                        'af9f16e3-75f6-4f90-acc6-f83d6524a6f3')

        assert report.node == 'node1.puppet.board'
        assert report.hash_ == 'hash#'
        assert report.start == json_to_datetime('2013-08-01T09:57:00.000Z')
        assert report.end == json_to_datetime('2013-08-01T10:57:00.000Z')
        assert report.received == json_to_datetime('2013-08-01T10:58:00.000Z')
        assert report.version == '1351535883'
        assert report.format_ == 3
        assert report.agent_version == '3.2.1'
        assert report.run_time == report.end - report.start
        assert report.transaction == 'af9f16e3-75f6-4f90-acc6-f83d6524a6f3'
        assert str(report) == str('hash#')
        assert unicode(report) == unicode('hash#')
        assert repr(report) == str('Report: hash#')
        assert report._Report__query_scope == '["=", "report", "hash#"]'


class TestEvent(object):
    """Test the Event object."""
    def test_event(self):
        event = Event('node', 'failure', '2013-08-01T10:57:00.000Z',
                      'hash#', '/etc/ssh/sshd_config', 'ensure',
                      'Nothing to say', 'present', 'absent', 'file')

        assert event.node == 'node'
        assert event.status == 'failure'
        assert event.failed is True
        assert event.timestamp == json_to_datetime('2013-08-01T10:57:00.000Z')
        assert event.hash_ == 'hash#'
        assert event.item['title'] == '/etc/ssh/sshd_config'
        assert event.item['type'] == 'file'
        assert event.item['property'] == 'ensure'
        assert event.item['message'] == 'Nothing to say'
        assert event.item['old'] == 'absent'
        assert event.item['new'] == 'present'
        assert str(event) == str('file[/etc/ssh/sshd_config]/hash#')
        assert unicode(event) == unicode('file[/etc/ssh/sshd_config]/hash#')
        assert repr(event) == str('Event: file[/etc/ssh/sshd_config]/hash#')

    def test_event_failed(self):
        event = Event('node', 'success', '2013-08-01T10:57:00.000Z',
                      'hash#', '/etc/ssh/sshd_config', 'ensure',
                      'Nothing to say', 'present', 'absent', 'file')

        assert event.status == 'success'
        assert event.failed is False


class TestCatalog(object):
    """Test the Catalog object."""
    def test_catalog(self):
        catalog = Catalog('node', [], [], 'unique', None)
        assert catalog.node == 'node'
        assert catalog.version == 'unique'
        assert catalog.transaction_uuid is None
        assert catalog.resources == {}
        assert catalog.edges == []
        assert str(catalog) == str('node/None')
        assert unicode(catalog) == unicode('node/None')
        assert repr(catalog) == str(
            '<Catalog: node/None>')


class TestEdge(object):
    """Test the Edge object."""
    def test_edge(self):
        resource_a = Resource('node', '/etc/ssh/sshd_config', 'file',
                              ['class', 'ssh'], False,
                              '/ssh/manifests/init.pp', 15, parameters={})

        resource_b = Resource('node', 'sshd', 'service',
                              ['class', 'ssh'], False,
                              '/ssh/manifests/init.pp', 30, parameters={})

        edge = Edge(resource_a, resource_b, 'notify')

        assert edge.source == resource_a
        assert edge.target == resource_b
        assert edge.relationship == 'notify'
        assert str(edge) == str(
            'file[/etc/ssh/sshd_config] - notify - service[sshd]')
        assert unicode(edge) == unicode(
            'file[/etc/ssh/sshd_config] - notify - service[sshd]')
        assert repr(edge) == str(
            '<Edge: file[/etc/ssh/sshd_config] - notify - service[sshd]>')
