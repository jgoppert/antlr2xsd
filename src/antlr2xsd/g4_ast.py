from typing import List, Dict, Union
import json


class Node:

    def __str__(self):
        d = self.__to_dict(self)
        return json.dumps(d, indent=2, sort_keys=True)

    __repr__ = __str__

    def to_dict(self):
        return self.__to_dict(self)

    @classmethod
    def __to_dict(cls, var):
        if isinstance(var, list):
            res = [cls.__to_dict(item) for item in var]
        elif isinstance(var, dict):
            res = {key: cls.__to_dict(var[key]) for key in var.keys()}
        elif isinstance(var, Node):
            res = {key: cls.__to_dict(var.__dict__[key]) for key in var.__dict__.keys()}
            res['_type'] = var.__class__.__name__
        else:
            res = var
        return res


class Root(Node):

    def __init__(self):
        self.rules = []  # type: List[Rule]


class RuleRef(Node):

    def __init__(self, min_occurs:int=1, max_occurs:int=1):
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs


class Rule(Node):

    def __init__(self, name: str, refs:  Dict[str, RuleRef]=None):
        self.name = name
        if refs is None:
            refs = {}
        self.refs = refs


class Choice(Node):

    def __init__(self, choices: List[RuleRef]=None):
        if choices is None:
            choices = []
        self.choices = choices

