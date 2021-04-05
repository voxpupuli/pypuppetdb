from pypuppetdb.api.metrics import MetricsAPI
from pypuppetdb.api.other import CommandAPI, MetadataAPI, StatusAPI
from pypuppetdb.api.pql import PqlAPI
from pypuppetdb.api.query import QueryAPI


class API(
    QueryAPI,
    MetricsAPI,
    CommandAPI,
    MetadataAPI,
    StatusAPI,
    PqlAPI,
):
    pass
