import types
from typing import Dict

from cytoolz.curried import keyfilter, curry
from dataclasses import asdict, is_dataclass, fields


def to_dict(doc):
    return (
        doc
        if isinstance(doc, dict)
        else asdict(doc)
        if is_dataclass(doc)
        else vars(doc)
    )


@curry
def to_object(dataclass_model, doc: Dict):
    field_names = set(map(lambda x: x.name, fields(dataclass_model)))
    slim = keyfilter(lambda k: k in field_names, doc)
    return dataclass_model(**slim)


def ensure_list(docs):
    if docs is None:
        return []

    elif isinstance(docs, list):
        return docs

    elif isinstance(docs, (tuple, set, range, types.GeneratorType)):
        return list(docs)

    return [docs]
