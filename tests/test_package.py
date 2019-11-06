from pypuppetdb.package import (__author__, __copyright__, __license__, __title__, __year__)


def test_package():
    assert __title__ == 'pypuppetdb'
    assert __author__ == 'Daniele Sluijters'
    assert __license__ == 'Apache License 2.0'
    assert __year__ == '2013, 2014, 2015, 2016, 2017, 2018, 2019'
    assert __copyright__ == 'Copyright {0} {1}'.format(__year__, __author__)
