from pypuppetdb.api.metrics import MetricsAPI
from pypuppetdb.api.other import CmdAPI, MetaAPI, StatusAPI
from pypuppetdb.api.pql import PqlAPI
from pypuppetdb.api.query import QueryAPI


class API(
    QueryAPI,
    MetricsAPI,
    CmdAPI,
    MetaAPI,
    StatusAPI,
    PqlAPI,
):
    pass
