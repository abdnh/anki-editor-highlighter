from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class Term:
    text: str
    classes: str
    is_regex: bool
    flags: str


TermsDict = Dict[str, List[Union[str, dict]]]


def terms_dict_to_list(terms_dict: TermsDict) -> list[Term]:
    """Collect terms from the config's `terms` dict into a list"""
    terms: list[Term] = []
    for classes, term_list in terms_dict.items():
        for term_obj in term_list:
            if isinstance(term_obj, str):
                terms.append(Term(term_obj, classes, False, ""))
            else:
                terms.append(
                    Term(
                        term_obj["pattern"],
                        classes,
                        True,
                        term_obj.get("flags", ""),
                    )
                )
    return terms


def normalize_classes(classes: str) -> str:
    return " ".join(sorted(klass.lower() for klass in classes.split()))


def terms_list_to_dict(terms: list[Term]) -> TermsDict:
    terms_dict: TermsDict = {}
    for term in terms:
        classes = normalize_classes(term.classes)
        terms_dict.setdefault(classes, [])
        if term.is_regex:
            terms_dict[classes].append({"pattern": term.text, "flags": term.flags})
        else:
            terms_dict[classes].append(term.text)
    return terms_dict
