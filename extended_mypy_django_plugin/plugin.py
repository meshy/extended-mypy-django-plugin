import enum
from typing import Generic

from mypy.nodes import FuncDef
from mypy.plugin import (
    AnalyzeTypeContext,
    AttributeContext,
    ClassDefContext,
    DynamicClassDefContext,
    FunctionContext,
)
from mypy.semanal import SemanticAnalyzer
from mypy.typeanal import TypeAnalyser
from mypy.types import Type as MypyType
from mypy_django_plugin import main
from mypy_django_plugin.transformers.managers import resolve_manager_method
from typing_extensions import assert_never

from . import actions, plugin_hook

MYPY_VERSION_TUPLE: tuple[int, int]


class Hook(
    Generic[plugin_hook.T_Ctx, plugin_hook.T_Ret],
    plugin_hook.Hook["ExtendedMypyStubs", plugin_hook.T_Ctx, plugin_hook.T_Ret],
):
    actions: actions.Actions

    def extra_init(self) -> None:
        self.actions = self.plugin.actions


class ExtendedMypyStubs(main.NewSemanalDjangoPlugin):
    class Annotations(enum.Enum):
        CONCRETE = "extended_mypy_django_plugin.annotations.Concrete"
        CONCRETE_QUERYSET = "extended_mypy_django_plugin.annotations.ConcreteQuerySet"
        DEFAULT_QUERYSET = "extended_mypy_django_plugin.annotations.DefaultQuerySet"

    def __init__(self, options: main.Options) -> None:
        super().__init__(options)
        self.actions = actions.Actions(
            self.lookup_fully_qualified,
            django_context=self.django_context,
            mypy_version=MYPY_VERSION_TUPLE,
        )

    @plugin_hook.hook
    class get_type_analyze_hook(Hook[AnalyzeTypeContext, MypyType]):
        def choose(self) -> bool:
            return any(
                member.value == self.fullname
                for member in ExtendedMypyStubs.Annotations.__members__.values()
            )

        def run(self, ctx: AnalyzeTypeContext) -> MypyType:
            Known = ExtendedMypyStubs.Annotations
            name = Known(self.fullname)

            assert isinstance(ctx.api, TypeAnalyser)
            assert isinstance(ctx.api.api, SemanticAnalyzer)

            if name is Known.CONCRETE:
                method = self.actions.find_concrete_models

            elif name is Known.CONCRETE_QUERYSET:
                method = self.actions.find_concrete_querysets

            elif name is Known.DEFAULT_QUERYSET:
                method = self.actions.find_default_queryset
            else:
                assert_never(name)

            return method(unbound_type=ctx.type, api=ctx.api, sem_api=ctx.api.api)

    @plugin_hook.hook
    class get_function_hook(Hook[FunctionContext, MypyType]):
        def choose(self) -> bool:
            sym = self.plugin.lookup_fully_qualified(self.fullname)
            return bool(
                sym
                and isinstance(sym.node, FuncDef)
                and self.actions.registered_for_function_hook(sym.node)
            )

        def run(self, ctx: FunctionContext) -> MypyType:
            return self.actions.modify_default_queryset_return_type(
                ctx, super_hook=self.super_hook
            )

    @plugin_hook.hook
    class get_customize_class_mro_hook(Hook[ClassDefContext, None]):
        def choose(self) -> bool:
            self.actions.fill_out_concrete_children(self.fullname)
            return False

        def run(self, ctx: ClassDefContext) -> None:
            # Never called
            return None

    @plugin_hook.hook
    class get_dynamic_class_hook(Hook[DynamicClassDefContext, None]):
        def choose(self) -> bool:
            class_name, _, method_name = self.fullname.rpartition(".")
            if method_name == "type_var":
                info = self.plugin._get_typeinfo_or_none(class_name)
                if info and info.has_base(ExtendedMypyStubs.Annotations.CONCRETE.value):
                    return True

            return False

        def run(self, ctx: DynamicClassDefContext) -> None:
            return self.actions.transform_type_var_classmethod(ctx)

    @plugin_hook.hook
    class get_attribute_hook(Hook[AttributeContext, MypyType]):
        def choose(self) -> bool:
            return self.super_hook is resolve_manager_method

        def run(self, ctx: AttributeContext) -> MypyType:
            return self.actions.extended_get_attribute_resolve_manager_method(ctx)


def plugin(version: str) -> type[ExtendedMypyStubs]:
    global MYPY_VERSION_TUPLE
    major, minor, _ = version.split(".", 2)
    MYPY_VERSION_TUPLE = (int(major), int(minor))
    return ExtendedMypyStubs
