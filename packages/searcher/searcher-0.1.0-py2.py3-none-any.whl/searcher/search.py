from aiohttp import ClientSession
from cytoolz.curried import assoc
from dataclasses import dataclass

from .converters import to_dict, ensure_list
from .models import ResultSet, Model


class BaseSearchEngine(object):
    async def add(self, docs, commit=False):
        raise NotImplementedError

    async def search(self, q="*:*", **params):
        raise NotImplementedError


class SearchException(Exception):
    pass


@dataclass()
class SolrEngine(BaseSearchEngine):
    url: str
    model: Model = None
    session: ClientSession = ClientSession()
    update_handler: str = "update"
    select_handler: str = "select"

    async def search(self, q="*:*", **kwargs):
        url = self.select_url()
        params = assoc(kwargs, "q", q)

        async with self.session.get(url, params=params) as context:
            json = await context.json()
            return self.json_response_to_result_set(json)

    async def count(self, q="*:*", **kwargs):
        result_set = await self.search(q=q, rows=0, **kwargs)
        return result_set.hits

    async def get(self, q="*:*", **kwargs):
        result_set = await self.search(q=q, rows=1, **kwargs)
        return result_set.docs[0] if result_set.hits == 1 else None

    async def add(self, docs, commit=False):
        url = self.update_url(commit=commit)
        docs = list(map(to_dict, ensure_list(docs)))
        async with self.session.post(url, json=docs) as context:
            json = await context.json()
            raise_on_error("add", json)
            return json

    def select_url(self):
        return f"{self.url}/{self.select_handler}"

    def update_url(self, commit=False):
        commit = "true" if commit else "false"
        return f"{self.url}/{self.update_handler}?commit={commit}"

    def json_response_to_result_set(self, json: dict) -> ResultSet:
        response = json.get("response")

        return ResultSet(
            hits=response.get("numFound"),
            dicts=response.get("docs"),
            model=self.model,
        )


def raise_on_error(func: str, json: dict):
    status = json.get("responseHeader", {}).get("status")
    if status:  # pragma: no cover
        raise SearchException(f"'{func}' Error [{status}]")
