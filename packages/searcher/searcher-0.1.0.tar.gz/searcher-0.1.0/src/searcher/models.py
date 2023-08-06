from typing import List, Dict, TypeVar, Callable

from dataclasses import dataclass

from .converters import to_object

Model = TypeVar("Model")


@dataclass
class ResultSet(object):
    hits: int
    dicts: List[Dict]
    model: Callable[[Dict], Model] = None

    def __iter__(self):
        return iter(self.docs)

    @property
    def docs(self) -> List:
        return self.objects if self.model else self.dicts

    @property
    def objects(self) -> List:
        assert self.model, "Cannot create objects without model."
        return list(map(to_object(self.model), self.dicts))
