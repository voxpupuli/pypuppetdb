from pypuppetdb.api.command import CommandAPI
from pypuppetdb.api.metadata import MetadataAPI
from pypuppetdb.api.metrics import MetricsAPI
from pypuppetdb.api.pql import PqlAPI
from pypuppetdb.api.query import QueryAPI
from pypuppetdb.api.status import StatusAPI


class API(
    CommandAPI,
    MetadataAPI,
    MetricsAPI,
    PqlAPI,
    QueryAPI,
    StatusAPI,
):
    pass
