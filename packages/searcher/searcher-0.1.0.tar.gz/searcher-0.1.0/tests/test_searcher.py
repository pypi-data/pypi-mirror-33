import pytest
from asynctest import CoroutineMock, patch
from dataclasses import dataclass

from searcher import SolrEngine, converters

URL = "http://localhost:8983/solr/mycore"
DOC_1 = {"title": "One", "body": "1 Body."}
DOC_2 = {"title": "Two", "body": "2 Body."}
RESPONSE = {"response": {"numFound": 2, "docs": [DOC_1, DOC_2]}}
RESPONSE_1 = {"response": {"numFound": 1, "docs": [DOC_1]}}


@dataclass
class Document(object):
    title: str
    body: str


@patch("aiohttp.ClientSession")
def test_solr_url_construction(mock):
    solr = SolrEngine(url=URL, session=mock)
    assert solr.update_url() == f"{URL}/update?commit=false"
    assert solr.update_url(commit=True) == f"{URL}/update?commit=true"
    assert solr.select_url() == f"{URL}/select"


@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
async def test_solr_search(mock):
    mock.get.return_value.__aenter__.return_value.json = CoroutineMock(
        side_effect=[RESPONSE]
    )
    solr = SolrEngine(url=URL, model=Document, session=mock)
    result_set = await solr.search()

    assert result_set.hits == 2
    assert result_set.dicts == RESPONSE["response"]["docs"]
    assert list(result_set) == [Document(**DOC_1), Document(**DOC_2)]


@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
async def test_solr_count(mock):
    mock.get.return_value.__aenter__.return_value.json = CoroutineMock(
        side_effect=[RESPONSE]
    )
    solr = SolrEngine(url=URL, model=Document, session=mock)
    count = await solr.count()
    assert count == 2


@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
async def test_solr_get(mock):
    mock.get.return_value.__aenter__.return_value.json = CoroutineMock(
        side_effect=[RESPONSE_1]
    )
    solr = SolrEngine(url=URL, model=Document, session=mock)
    doc = await solr.get()
    assert doc == Document(**DOC_1)


@pytest.mark.asyncio
@patch("aiohttp.ClientSession")
async def test_solr_add(mock):
    mock.post.return_value.__aenter__.return_value.json = CoroutineMock(
        side_effect=[RESPONSE]
    )

    docs = [Document(**DOC_1), Document(**DOC_2)]

    solr = SolrEngine(url=URL, model=Document, session=mock)
    await solr.add(docs=docs)

    assert mock.method_calls[0][2] == dict(json=[DOC_1, DOC_2])


def test_ensure_list():
    assert converters.ensure_list(None) == []
    assert converters.ensure_list(1) == [1]
    assert converters.ensure_list("abc") == ["abc"]
    assert converters.ensure_list(range(3)) == [0, 1, 2]
    assert converters.ensure_list((0, 1, 2)) == [0, 1, 2]
