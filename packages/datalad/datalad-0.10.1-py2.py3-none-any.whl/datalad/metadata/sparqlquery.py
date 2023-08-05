# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Interface for performing SPARQL queries on meta data
"""

__docformat__ = 'restructuredtext'


from datalad.interface.base import Interface
from datalad.distribution.dataset import datasetmethod
from datalad.distribution.dataset import EnsureDataset
from datalad.metadata import get_metadata
from datalad.metadata.search import get_search_dataset
from datalad.support.param import Parameter
from datalad.support.constraints import EnsureNone


class SPARQLQuery(Interface):
    """SPARQL"""

    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            doc="""specify the dataset to perform the query operation on. If
            no dataset is given, an attempt is made to identify the dataset
            based on the current working directory and/or the `path` given""",
            constraints=EnsureDataset() | EnsureNone()),
        query=Parameter(
            args=('query',),
            doc="""query"""),
    )

    @staticmethod
    @datasetmethod(name='search')
    def __call__(
            query,
            dataset=None):
        ds = get_search_dataset(dataset)
        # obtain meta data from best source
        print('loading from scratch')
        meta = get_metadata(ds, guess_type=False, ignore_subdatasets=False,
                            from_native=False)

        from rdflib import Graph
        from json import dumps
        print('pumping into RDFLib')
        graph = Graph().parse(data=dumps(meta), format='json-ld', publicID='http://db.datalad.org/')
        print('serialize')

        print(graph.serialize(format='turtle'))
        return graph
