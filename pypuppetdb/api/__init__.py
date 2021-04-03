from pypuppetdb.api.pql import PqlAPI
from pypuppetdb.api.query import QueryAPI
from pypuppetdb.api.metrics import MetricsAPI
from pypuppetdb.api.other import CmdAPI, MetaAPI, ServicesAPI


class API(
    QueryAPI,
    MetricsAPI,
    CmdAPI,
    MetaAPI,
    ServicesAPI,
    PqlAPI,
):
    pass
