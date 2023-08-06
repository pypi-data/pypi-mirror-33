from .search import SolrEngine
from .models import ResultSet
from .converters import to_object, to_dict

__all__ = ("SolrEngine", "ResultSet", "to_object", "to_dict")


__author__ = """AwesomeToolbox.com"""
__email__ = "info@awesometoolbox.com"
__version__ = "0.1"

__uri__ = "http://www.github.com/awesometoolbox/searcher"
__copyright__ = "Copyright (c) 2018 awesometoolbox.com"
__description__ = "searcher: Solr Search Client"
__doc__ = __description__ + " <" + __uri__ + ">"
__license__ = "MIT"
__title__ = "searcher"
