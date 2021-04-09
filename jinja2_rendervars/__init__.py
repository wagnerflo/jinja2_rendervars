from contextlib import contextmanager
from contextvars import ContextVar,copy_context
from functools import partial
from jinja2.ext import Extension
from jinja2.nodes import CallBlock,Const
from ._contextvars import enter_context,exit_context

_MISSING = object()
_REGISTRY = {}
_POLICY_RESTRICT = "rendervars.restrict"

class RenderVars:
    def __init__(self, env, ctx=None):
        self._env = env
        self._ctx = ctx

    def __getattr__(self, name):
        if name not in _REGISTRY:
            raise AttributeError(f"rendervar '{name}' unknown")
        if self._ctx is None:
            if (restrict := self._env.policies.get(_POLICY_RESTRICT)) is not None:
                if name not in restrict:
                    raise AttributeError(
                        f"access to rendervar '{name}' is restricted"
                    )
            return _REGISTRY[name].__get__()
        return _REGISTRY[name]._from_ctx(self._ctx)

    def __repr__(self):
        content = ", ".join(
            f"{n}={repr(getattr(self, n))}"
            for n in (
                _REGISTRY.keys() if self._ctx is not None else
                self._env.policies.get(_POLICY_RESTRICT, _REGISTRY.keys())
            )
        )
        return f"{self.__class__.__name__}({content})"

class RenderVarsExtension(Extension):
    tags = frozenset(["rendervar"])

    def __init__(self, env):
        super().__init__(env)
        env.rendervars = self.context
        env.globals["rendervars"] = RenderVars(env)

    @contextmanager
    def context(self):
        ctx = copy_context()
        enter_context(ctx)
        try:
            yield RenderVars(self.environment, ctx)
        finally:
            exit_context(ctx)

    def parse(self, parser):
        next(parser.stream)
        name = parser.stream.expect("name")
        parser.stream.expect("assign")
        return CallBlock(
            self.call_method(
                "_set", [
                    Const(name.value, lineno=name.lineno),
                    parser.parse_expression()
                ],
                lineno=name.lineno
            ),
            [], [], [],
            lineno=name.lineno
        )

    def _set(self, name, value, caller):
        if name not in _REGISTRY:
            raise AttributeError(f"rendervar '{name}' unknown")
        if (restrict := self.environment.policies.get(_POLICY_RESTRICT)) is not None:
            if name not in restrict:
                raise AttributeError(
                    f"access to rendervar '{name}' is restricted"
                )
        _REGISTRY[name].__set__(None, value)
        return ""

class RenderVar:
    def __new__(cls, name, *args, **kwds):
        if not args:
            return lambda factory: cls(name, factory, **kwds)
        return super().__new__(cls)

    def __init__(self, name, factory, **kwds):
        if callable(factory):
            self._factory = partial(factory, **kwds)
        else:
            self._factory = lambda: factory
        self._var = ContextVar(name, default=_MISSING)
        _REGISTRY[name] = self

    def __get__(self, instance=None, owner=None):
        if (res := self._var.get()) is _MISSING:
            res = self._factory()
            self._var.set(res)
        return res

    def __set__(self, instance, value):
        self._var.set(value)

    def __repr__(self):
        return repr(self.__get__())

    def _from_ctx(self, ctx):
        try:
            return ctx[self._var]
        except KeyError:
            try:
                return ctx.run(self.__get__)
            except RuntimeError:
                return self.__get__()
