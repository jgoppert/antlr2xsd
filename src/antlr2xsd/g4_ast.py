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
        self.rules = []  # type: List[Type]


class TypeRef(Node):

    def __init__(self, name, min_occurs:int=1, max_occurs:int=1):
        self.name = name
        self.min_occurs = min_occurs
        self.max_occurs = max_occurs


class Type(Node):

    def __init__(self, name: str, refs:  Dict[str, TypeRef]=None):
        self.name = name
        if refs is None:
            refs = {}
        self.refs = refs


class Choice(Node):

    def __init__(self, choices: List[TypeRef]=None):
        if choices is None:
            choices = []
        self.choices = choices


class TreeListener:
    """
    Defines interface for tree listeners.
    """

    def __init__(self):
        self.context = {}

    def enterEvery(self, tree: Node) -> None:
        self.context[type(tree).__name__] = tree

    def exitEvery(self, tree: Node):
        self.context[type(tree).__name__] = None

    def enterType(self, tree: Type) -> None: pass

    def exitType(self, tree: Type) -> None: pass

    def enterTypeRef(self, tree: TypeRef) -> None: pass

    def exitTypeRef(self, tree: TypeRef) -> None: pass

    def enterChoice(self, tree: Choice) -> None: pass

    def exitChoice(self, tree: Choice) -> None: pass


class TreeWalker:
    """
    Defines methods for tree walker. Inherit from this to make your own.
    """

    def walk(self, listener: TreeListener, tree: Node) -> None:
        """
        Walks an AST tree recursively
        :param listener:
        :param tree:
        :return: None
        """
        name = tree.__class__.__name__
        if hasattr(listener, 'enterEvery'):
            getattr(listener, 'enterEvery')(tree)
        if hasattr(listener, 'enter' + name):
            getattr(listener, 'enter' + name)(tree)
        for child_name in tree.__dict__.keys():
            self.handle_walk(listener, tree.__dict__[child_name])
        if hasattr(listener, 'exitEvery'):
            getattr(listener, 'exitEvery')(tree)
        if hasattr(listener, 'exit' + name):
            getattr(listener, 'exit' + name)(tree)

    def handle_walk(self, listener: TreeListener, tree: Union[Node, dict, list]) -> None:
        """
        Handles tree walking, has to account for dictionaries and lists
        :param listener: listener that reacts to walked events
        :param tree: the tree to walk
        :return: None
        """
        if isinstance(tree, Node):
            self.walk(listener, tree)
        elif isinstance(tree, dict):
            for k in tree.keys():
                self.handle_walk(listener, tree[k])
        elif isinstance(tree, list):
            for i in range(len(tree)):
                self.handle_walk(listener, tree[i])
        else:
            pass