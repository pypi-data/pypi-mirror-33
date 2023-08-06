# from typing import Generic, TypeVar, Callable, Tuple, cast, Type, Any, GenericMeta

# from lenses import UnboundLens

# from amino.tc.monad import Monad
# from amino import List, curried, ADT, Either
# from amino.util.string import ToStr

# S = TypeVar('S')
# R = TypeVar('R')
# A = TypeVar('A')
# B = TypeVar('B')
# ST = TypeVar('ST', bound='StateT')


# class SM(Generic[S, A]):
#     pass


# class StateT(Generic[S, A], ADT['StateT[S, A]']):
#     pass


# class StateTPure(Generic[S, A], StateT[S, A]):
#     pass


# class StateTCompute(Generic[S, A], StateT[S, A]):

#     def __init__(self, run_f: SM[S, A]) -> None:
#         self.run_f = run_f

#     @property
#     def cls(self) -> Type[ST]:
#         return cast(Type[ST], type(self))

#     # def run(self, s: S) -> SM[Tuple[S, A]]:
#     #     return self.run_f.flat_map(lambda f: f(s))

#     # def run_s(self, s: S) -> SM[S]:
#     #     return self.run(s).map(lambda a: a[0])

#     # def run_a(self, s: S) -> SM[S]:
#     #     return self.run(s).map(lambda a: a[1])

#     def _arg_desc(self) -> List[str]:
#         return List(str(self.run_f))

#     # def flat_map_f(self, f: Callable[[A], SM[B]]) -> 'StateT[S, B]':
#     #     def h(s: S, a: A) -> SM[Tuple[S, B]]:
#     #         return f(a).map(lambda b: (s, b))
#     #     def g(fsa: SM[Tuple[S, A]]) -> SM[Tuple[S, B]]:
#     #         return fsa.flat_map2(h)
#     #     run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
#     #     return self.cls.apply_f(run_f1)

#     # def transform(self, f: Callable[[Tuple[S, A]], Tuple[S, B]]) -> 'StateT[S, B]':
#     #     def g(fsa: SM[Tuple[S, A]]) -> SM[Tuple[S, B]]:
#     #         return fsa.map2(f)
#     #     run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
#     #     return self.cls.apply_f(run_f1)

#     # def transform_s(self, f: Callable[[R], S], g: Callable[[R, S], R]) -> 'StateT[R, A]':
#     #     def trans(sfsa: S, A, r: R) -> SM[Tuple[R, A]]:
#     #         s = f(r)
#     #         return sfsa(s).map2(lambda s, a: (g(r, s), a))
#     #     return self.cls.apply_f(self.run_f.map(curried(trans)))

#     # def transform_f(self, tpe: Type['StateT[H, S, B]'], f: Callable[[G], H]) -> 'StateT[H, S, B]':
#     #     def trans(s: S) -> H:
#     #         return f(self.run(s))
#     #     return tpe.apply(trans)

#     # def transform_s_lens(self, l: UnboundLens) -> 'StateT[H, R, A]':
#     #     return self.transform_s(l.get(), lambda r, s: l.set(s)(r))

#     # zoom = transform_s_lens

#     # def transform_s_lens_read(self, l: UnboundLens) -> 'StateT[H, R, A]':
#     #     return self.transform_s(l.get(), lambda r, s: r)

#     # read_zoom = transform_s_lens_read

#     # def modify_(self, f: Callable[[S], S]) -> 'StateT[S, A]':
#     #     return self.transform(lambda s, a: (f(s), a))


# class StateMonad(Monad, tpe=StateT):

#     def pure(self, a: A) -> StateT[S, A]:
#         return StateTPure(a)

#     def flat_map(self, fa: StateT[S, A], f: Callable[[A], StateT[S, B]]) -> StateT[S, B]:
#         # def h(s: S, a: A) -> SM[Tuple[S, B]]:
#         #     return f(a).run(s)
#         # def g(fsa: SM[Tuple[S, A]]) -> SM[Tuple[S, B]]:
#         #     return fsa.flat_map2(h)
#         # def i(sfsa: S, A) -> Callable[[S], SM[Tuple[S, B]]]:
#         #     return lambda a: g(sfsa(a))
#         # run_f1 = fa.run_f.map(i)
#         return StateT.apply_f(run_f1)


# class StateMeta(GenericMeta):

#     @property
#     def unit(self) -> StateT[S, None]:
#         return self.pure(None)

# #     def cons(self, run_f: SM[S, A]) -> StateT[S, A]:
# #         return self(run_f)

# #     def apply(self, f: S, A) -> StateT[S, A]:
# #         return self.cons(self.monad.pure(f))

# #     def apply_f(self, run_f: SM[S, A]) -> StateT[S, A]:
# #         return self.cons(run_f)

# #     def inspect(self, f: Callable[[S], A]) -> StateT[S, A]:
# #         def g(s: S) -> SM[Tuple[S, A]]:
# #             return self.monad.pure((s, f(s)))
# #         return self.apply(g)

# #     def inspect_f(self, f: Callable[[S], SM[A]]) -> StateT[S, A]:
# #         def g(s: S) -> SM[Tuple[S, A]]:
# #             return f(s).map(lambda a: (s, a))
# #         return self.apply(g)

#     def pure(self, a: A) -> StateT[S, A]:
#         return StateTPure(a)

# #     def reset(self, s: S, a: A) -> StateT[S, A]:
# #         return self.apply(lambda _: self.monad.pure((s, a)))

# #     def reset_t(self, t: Tuple[S, A]) -> StateT[S, A]:
# #         return self.apply(lambda _: self.monad.pure(t))

# #     def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> StateT[S, A]:
# #         return self.apply(lambda s: self.monad.pure((s, fa(*a, **kw))))

# #     def lift(self, fa: SM[A]) -> StateT[S, A]:
# #         def g(s: S) -> SM[Tuple[S, A]]:
# #             return fa.map(lambda a: (s, a))
# #         return self.apply(g)

# #     def modify(self, f: Callable[[S], S]) -> StateT[S, A]:
# #         return self.apply(lambda s: self.monad.pure((f(s), None)))

# #     def modify_f(self, f: Callable[[S], SM[S]]) -> StateT[S, A]:
# #         return self.apply(lambda s: f(s).map(lambda a: (a, None)))

# #     def set(self, s: S) -> StateT[S, A]:
# #         return self.modify(lambda s0: s)

# #     def get(self) -> StateT[S, A]:
# #         return self.inspect(lambda a: a)


# class State(Generic[S, A], metaclass=StateMeta):
#     pass


# class EitherState(Generic[S, A], State[S, A]):

#     def __init__(self, st: StateT[S, A]) -> None:
#         self.st = st

#     def run(self) -> Either[str, A]:
#         return st.run(Either)


# def bind_either(st: StateT[S, A]) -> EitherState[S, A]:
#     return EitherState(st)


# __all__ = ()
