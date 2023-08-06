from typing import List, TypeVar, Generic, Type, Dict

R = TypeVar('R')
A = TypeVar('A')
B = TypeVar('B')


class Bound:

    def __init__(self, cls: str) -> None:
        self.cls = cls


class Kind:
    pass


class Nullary(Kind):

    def __init__(self, name: str) -> None:
        self.name = name


class HK(Kind):

    def __init__(self, name: str, params: List[Kind]) -> None:
        self.name = name
        self.params = params


class Par:
    pass


class Mono(Par):

    def __init__(self, tpe: type) -> None:
        self.tpe = tpe


class Poly(Par):

    def __init__(self, kind: Kind, bounds: List[Bound]=[]) -> None:
        self.kind = kind
        self.bounds = bounds


class Signature:

    def __init__(self, input: List[Par], output: Par) -> None:
        self.input = input
        self.output = output


class ClassFunction:
    pass


class ClassFunction1(Generic[R, A], ClassFunction):

    def __init__(self, name: str, signature: Signature, par: Type[A], ret: Type[R]) -> None:
        self.name = name
        self.signature = signature
        self.par = par
        self.ret = ret


class ClassFunction2(Generic[R, A, B], ClassFunction):

    def __init__(self, name: str, signature: Signature, par1: Type[A], par2: Type[B], ret: Type[R]) -> None:
        self.name = name
        self.signature = signature
        self.par1 = par1
        self.par2 = par2
        self.ret = ret


class Class:

    def __init__(self, name: str, functions: List[ClassFunction]) -> None:
        self.name = name
        self.functions = functions


class Instance(Generic[A]):

    def __init__(self, cls: Class, tpe: A, functions: Dict[str, ClassFunction]) -> None:
        self.cls = cls
        self.tpe = tpe
        self.functions = functions


class Instances:

    def __init__(self) -> None:
        self.registry: Dict[str, Instance] = dict()


instances = Instances()


def register(inst: Instance[A]) -> None:
    instances.registry


def instance(cls: Class, tpe: A, **functions: ClassFunction) -> None:
    inst = Instance(cls, tpe, functions)
    register(inst)


class HK1(Generic[A]):
    pass


__all__ = ('Bound', 'Kind', 'Nullary', 'HK', 'Par', 'Mono', 'Poly', 'Signature', 'ClassFunction', 'Class', 'Instance',)
