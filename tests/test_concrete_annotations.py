import pytest
from extended_mypy_django_plugin_test_driver import OutputBuilder, Scenario


class TestConcreteAnnotations:
    def test_cast_as_concrete(self, scenario: Scenario) -> None:
        @scenario.run_and_check_mypy_after(installed_apps=["leader", "simple"])
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "main.py",
                """
                from simple.models import Follow1, Follow2
                from leader.models import Leader
                from extended_mypy_django_plugin import Concrete

                model: type[Leader] = Follow1
                # ^ REVEAL ^ type[leader.models.Leader]

                class Thing:
                    def __init__(self, model: type[Leader]) -> None:
                        self.model = model

                found = Concrete.cast_as_concrete(Thing(model=model).model)
                # ^ ERROR(misc) ^ cast_as_concrete can only take variable names. Create a variable with what you're passing in and pass in that variable instead

                thing = Thing(model=model)
                found = Concrete.cast_as_concrete(thing.model)
                # ^ ERROR(misc) ^ cast_as_concrete can only take variable names. Create a variable with what you're passing in and pass in that variable instead

                model = Concrete.cast_as_concrete(model)
                # ^ REVEAL ^ Union[type[simple.models.Follow1], type[simple.models.Follow2]]

                model2: type[Leader] = Follow1
                # ^ REVEAL ^ type[leader.models.Leader]

                model3 = Concrete.cast_as_concrete(model2)
                # ^ REVEAL ^ Union[type[simple.models.Follow1], type[simple.models.Follow2]]

                model2
                # ^ REVEAL ^ type[leader.models.Leader]

                instance: Leader = Follow1.objects.create()
                # ^ REVEAL ^ leader.models.Leader

                instance = Concrete.cast_as_concrete(instance)
                # ^ REVEAL ^ Union[simple.models.Follow1, simple.models.Follow2]

                instance2: Leader = Follow1.objects.create()
                # ^ REVEAL ^ leader.models.Leader

                instance3 = Concrete.cast_as_concrete(instance2)
                # ^ REVEAL ^ Union[simple.models.Follow1, simple.models.Follow2]

                instance2
                # ^ REVEAL ^ leader.models.Leader
                """,
            )

    def test_simple_annotation(self, scenario: Scenario) -> None:
        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "main.py",
                """
                from extended_mypy_django_plugin import Concrete, DefaultQuerySet
                from typing import cast, TypeGuard

                from myapp.models import Parent, Child1, Child2

                def check_cls_with_type_guard(cls: type[Parent]) -> TypeGuard[type[Concrete[Parent]]]:
                    return True

                def check_instance_with_type_guard(cls: Parent) -> TypeGuard[Concrete[Parent]]:
                    return True

                models: Concrete[Parent]
                # ^ REVEAL ^ Union[myapp.models.Child1, myapp.models.Child2, myapp.models.Child3, myapp2.models.ChildOther]

                qs: DefaultQuerySet[Parent]
                # ^ REVEAL ^ Union[django.db.models.query.QuerySet[myapp.models.Child1, myapp.models.Child1], myapp.models.Child2QuerySet, django.db.models.query.QuerySet[myapp.models.Child3, myapp.models.Child3], django.db.models.query.QuerySet[myapp2.models.ChildOther, myapp2.models.ChildOther]]

                cls: type[Parent] = Child1
                assert check_cls_with_type_guard(cls)
                cls
                # ^ REVEAL ^ Union[type[myapp.models.Child1], type[myapp.models.Child2], type[myapp.models.Child3], type[myapp2.models.ChildOther]]

                instance: Parent = cast(Child1, None)
                assert check_instance_with_type_guard(instance)
                instance
                # ^ REVEAL ^ Union[myapp.models.Child1, myapp.models.Child2, myapp.models.Child3, myapp2.models.ChildOther]

                children: Concrete[Parent]
                # ^ REVEAL ^ Union[myapp.models.Child1, myapp.models.Child2, myapp.models.Child3, myapp2.models.ChildOther]

                children_qs: DefaultQuerySet[Parent]
                # ^ REVEAL ^ Union[django.db.models.query.QuerySet[myapp.models.Child1, myapp.models.Child1], myapp.models.Child2QuerySet, django.db.models.query.QuerySet[myapp.models.Child3, myapp.models.Child3], django.db.models.query.QuerySet[myapp2.models.ChildOther, myapp2.models.ChildOther]]

                child: Concrete[Child1]
                # ^ REVEAL ^ myapp.models.Child1

                child1_qs: DefaultQuerySet[Child1]
                # ^ REVEAL ^ django.db.models.query.QuerySet[myapp.models.Child1, myapp.models.Child1]

                child2_qs: DefaultQuerySet[Child2]
                # ^ REVEAL ^ myapp.models.Child2QuerySet

                t1_children: type[Concrete[Parent]]
                # ^ REVEAL ^ Union[type[myapp.models.Child1], type[myapp.models.Child2], type[myapp.models.Child3], type[myapp2.models.ChildOther]]

                t1_children_qs: type[DefaultQuerySet[Parent]]
                # ^ REVEAL ^ Union[type[django.db.models.query.QuerySet[myapp.models.Child1, myapp.models.Child1]], type[myapp.models.Child2QuerySet], type[django.db.models.query.QuerySet[myapp.models.Child3, myapp.models.Child3]], type[django.db.models.query.QuerySet[myapp2.models.ChildOther, myapp2.models.ChildOther]]]

                t1_child: type[Concrete[Child1]]
                # ^ REVEAL ^ type[myapp.models.Child1]

                t1_child1_qs: type[DefaultQuerySet[Child1]]
                # ^ REVEAL ^ type[django.db.models.query.QuerySet[myapp.models.Child1, myapp.models.Child1]]

                t1_child2_qs: type[DefaultQuerySet[Child2]]
                # ^ REVEAL ^ type[myapp.models.Child2QuerySet]

                t2_children: Concrete[type[Parent]]
                # ^ REVEAL ^ Union[type[myapp.models.Child1], type[myapp.models.Child2], type[myapp.models.Child3], type[myapp2.models.ChildOther]]

                t2_children_qs: DefaultQuerySet[type[Parent]]
                # ^ REVEAL ^ Union[type[django.db.models.query.QuerySet[myapp.models.Child1, myapp.models.Child1]], type[myapp.models.Child2QuerySet], type[django.db.models.query.QuerySet[myapp.models.Child3, myapp.models.Child3]], type[django.db.models.query.QuerySet[myapp2.models.ChildOther, myapp2.models.ChildOther]]]

                t2_child: Concrete[type[Child1]]
                # ^ REVEAL ^ type[myapp.models.Child1]

                t2_child1_qs: DefaultQuerySet[type[Child1]]
                # ^ REVEAL ^ type[django.db.models.query.QuerySet[myapp.models.Child1, myapp.models.Child1]]

                t2_child2_qs: DefaultQuerySet[type[Child2]]
                # ^ REVEAL ^ type[myapp.models.Child2QuerySet]
                """,
            )

    def test_can_use_type_var_before_class_is_defined(self, scenario: Scenario) -> None:
        @scenario.run_and_check_mypy_after(installed_apps=["example"])
        def _(expected: OutputBuilder) -> None:
            scenario.file(expected, "example/__init__.py", "")

            scenario.file(
                expected,
                "example/apps.py",
                """
                from django.apps import AppConfig

                class Config(AppConfig):
                    name = "example"
                """,
            )

            scenario.file(
                expected,
                "example/models.py",
                """
                from __future__ import annotations

                from django.db import models
                from typing import Any
                from typing_extensions import Self
                from extended_mypy_django_plugin import Concrete

                T_Leader = Concrete.type_var("T_Leader", "Leader")

                class Leader(models.Model):
                    @classmethod
                    def new(cls) -> Concrete[Self]:
                        cls = Concrete.cast_as_concrete(cls)
                        # ^ REVEAL ^ Union[type[example.models.Follower1], type[example.models.Follower2]]
                        return cls.objects.create()

                    @classmethod
                    def new_with_kwargs(cls, **kwargs: Any) -> Concrete[Self]:
                        cls = Concrete.cast_as_concrete(cls)
                        # ^ REVEAL ^ Union[type[example.models.Follower1], type[example.models.Follower2]]
                        return cls.objects.create(**kwargs)

                    class Meta:
                        abstract = True


                class Follower1(Leader):
                    ...

                class Follower2(Leader):
                    ...

                def make_instance(cls: type[T_Leader]) -> T_Leader:
                    cls
                    # ^ REVEAL ^ type[example.models.Follower1]
                    # ^ REVEAL ^ type[example.models.Follower2]
                    return cls.new()
                """,
            )

            scenario.file(
                expected,
                "main.py",
                """
                from example.models import Leader, Follower1, Follower2, make_instance
                from extended_mypy_django_plugin import Concrete

                instance1 = make_instance(Follower1)
                # ^ REVEAL ^ example.models.Follower1

                instance2 = make_instance(Follower2)
                # ^ REVEAL ^ example.models.Follower2

                from_new_with_kwargs = Follower1.new_with_kwargs()
                # ^ REVEAL ^ example.models.Follower1

                model: type[Concrete[Leader]] = Follower1
                # ^ REVEAL ^ Union[type[example.models.Follower1], type[example.models.Follower2]]
                """,
                # TODO: Make this possible
                # would require generating overload variants on make_instance
                # instance3 = make_instance(model)
                # # ^ REVEAL ^ Union[example.models.Follower1, example.models.Follower2]
                # """,
            )

    def test_using_concrete_annotation_on_class_used_in_annotation(
        self, scenario: Scenario
    ) -> None:
        @scenario.run_and_check_mypy_after(installed_apps=["example"])
        def _(expected: OutputBuilder) -> None:
            scenario.file(expected, "example/__init__.py", "")

            scenario.file(
                expected,
                "example/apps.py",
                """
                from django.apps import AppConfig

                class Config(AppConfig):
                    name = "example"
                """,
            )

            scenario.file(
                expected,
                "example/models.py",
                """
                from __future__ import annotations

                from django.db import models
                from collections.abc import Callable
                from typing_extensions import Self
                from typing import Protocol
                from extended_mypy_django_plugin import Concrete, DefaultQuerySet

                class Leader(models.Model):
                    @classmethod
                    def new(cls) -> Concrete[Self]:
                        cls = Concrete.cast_as_concrete(cls)
                        # ^ REVEAL ^ Union[type[example.models.Follower1], type[example.models.Follower2]]
                        return cls.objects.create()

                    def qs(self) -> DefaultQuerySet[Self]:
                        self = Concrete.cast_as_concrete(self)
                        # ^ REVEAL ^ Union[example.models.Follower1, example.models.Follower2]
                        return self.__class__.objects.filter(pk=self.pk)

                    class Meta:
                        abstract = True

                class Follower1QuerySet(models.QuerySet["Follower1"]):
                    ...

                Follower1Manager = models.Manager.from_queryset(Follower1QuerySet)

                class Follower1(Leader):
                    objects = Follower1Manager()

                class Follower2(Leader):
                    ...
                """,
            )

            scenario.file(
                expected,
                "main.py",
                """
                from example.models import Leader, Follower1, Follower2
                from extended_mypy_django_plugin import Concrete

                model: type[Leader] = Follower1
                # ^ REVEAL ^ type[example.models.Leader]

                leader = model.new()
                # ^ REVEAL ^ Union[example.models.Follower1, example.models.Follower2]

                qs = leader.qs()
                # ^ REVEAL ^ Union[example.models.Follower1QuerySet, django.db.models.query.QuerySet[example.models.Follower2, example.models.Follower2]]

                follower1 = Follower1.new()
                # ^ REVEAL ^ example.models.Follower1

                qs3 = Follower2.new().qs()
                # ^ REVEAL ^ django.db.models.query.QuerySet[example.models.Follower2, example.models.Follower2]

                other: Leader = Follower1.new()
                # ^ REVEAL ^ example.models.Leader

                narrowed = Concrete.cast_as_concrete(other)
                # ^ REVEAL ^ Union[example.models.Follower1, example.models.Follower2]
                other
                # ^ REVEAL ^ example.models.Leader
                """,
            )

    def test_resolving_concrete_type_vars(self, scenario: Scenario) -> None:
        @scenario.run_and_check_mypy_after(installed_apps=["example"])
        def _(expected: OutputBuilder) -> None:
            scenario.file(expected, "example/__init__.py", "")

            scenario.file(
                expected,
                "example/apps.py",
                """
                from django.apps import AppConfig

                class Config(AppConfig):
                    name = "example"
                """,
            )

            scenario.file(
                expected,
                "example/models.py",
                """
                from __future__ import annotations

                from django.db import models
                from collections.abc import Callable
                from typing_extensions import Self
                from typing import Protocol
                from extended_mypy_django_plugin import Concrete, DefaultQuerySet

                class Leader(models.Model):
                    class Meta:
                        abstract = True

                def thing() -> None:
                    all_concrete: Concrete[Leader]
                    # ^ REVEAL[leader-concrete-where-leader-defined] ^ Union[example.models.Follower1, example.models.Follower2]

                T_Leader = Concrete.type_var("T_Leader", Leader)

                class Follower1QuerySet(models.QuerySet["Follower1"]):
                    ...

                Follower1Manager = models.Manager.from_queryset(Follower1QuerySet)

                class Follower1(Leader):
                    objects = Follower1Manager()

                class Follower2(Leader):
                    ...

                def make_queryset(instance: T_Leader, /) -> DefaultQuerySet[T_Leader]:
                    return instance.__class__.objects.filter(pk=instance.pk)

                class MakeQueryset(Protocol):
                    def __call__(self, instance: T_Leader, /) -> DefaultQuerySet[T_Leader]:
                        ...

                functions: list[MakeQueryset] = [make_queryset]

                functions2: list[Callable[[T_Leader], DefaultQuerySet[T_Leader]]] = [make_queryset] # type: ignore[list-item]
                """,
            )

            scenario.file(
                expected,
                "main.py",
                """
                from example.models import Leader, Follower1, Follower2, functions, functions2, make_queryset
                from extended_mypy_django_plugin import Concrete
                from example import models

                # Test Concrete.type_var can be made with "models.Leader" (as in with a MemberExpr)
                T_Leader = Concrete.type_var("T_Leader", models.Leader)

                def get_leader(cls: type[T_Leader]) -> T_Leader:
                    return cls.objects.create()

                made = get_leader(Follower1)
                # ^ REVEAL ^ example.models.Follower1

                all_concrete: Concrete[Leader]
                # ^ REVEAL[all-concrete] ^ Union[example.models.Follower1, example.models.Follower2]

                follower1 = Follower1.objects.create()
                # ^ REVEAL ^ example.models.Follower1

                func = functions[0]
                # ^ REVEAL ^ example.models.MakeQueryset

                func2 = functions2[0]
                
                qs1 = func(follower1)
                # ^ REVEAL ^ example.models.Follower1QuerySet

                qs2 = func2(follower1)
                # ^ REVEAL ^ example.models.Follower1QuerySet

                qs5 = make_queryset(follower1)
                # ^ REVEAL ^ example.models.Follower1QuerySet
                """,
            )

        @scenario.run_and_check_mypy_after(installed_apps=["example", "example2"])
        def _(expected: OutputBuilder) -> None:
            scenario.file(expected, "example2/__init__.py", "")

            scenario.file(
                expected,
                "example2/apps.py",
                """
                from django.apps import AppConfig

                class Config(AppConfig):
                    name = "example2"
                """,
            )

            scenario.file(
                expected,
                "example2/models.py",
                """
                from __future__ import annotations

                from example.models import Leader

                from django.db import models

                class Follower3QuerySet(models.QuerySet["Follower3"]):
                    ...

                Follower3Manager = models.Manager.from_queryset(Follower3QuerySet)

                class Follower3(Leader):
                    objects = Follower3Manager()
                """,
            )

            expected.daemon_should_restart()
            expected.on("example/models.py").add_revealed_type(
                "leader-concrete-where-leader-defined",
                "Union[example.models.Follower1, example.models.Follower2, example2.models.Follower3]",
            )
            expected.on("main.py").add_revealed_type(
                "all-concrete",
                "Union[example.models.Follower1, example.models.Follower2, example2.models.Follower3]",
            )

    def test_restarts_dmypy_if_names_of_known_settings_change(self, scenario: Scenario) -> None:
        if not scenario.for_daemon:
            pytest.skip("Test only relevant for the daemon")

        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            pass

        # New names should restart
        custom_settings = """
        ONE: int = 1
        TWO: str = "2"
        """

        @scenario.run_and_check_mypy_after(
            additional_properties={"custom_settings": custom_settings}
        )
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_restart()

        @scenario.run_and_check_mypy_after(
            additional_properties={"custom_settings": custom_settings}
        )
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_not_restart()

        # Same names, different types should  restart
        custom_settings = """
        ONE: str = "1"
        TWO: str = "2"
        """

        @scenario.run_and_check_mypy_after(
            additional_properties={"custom_settings": custom_settings}
        )
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_restart()

        @scenario.run_and_check_mypy_after(
            additional_properties={"custom_settings": custom_settings}
        )
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_not_restart()

        # Same names, same types, different values should not restart
        custom_settings = """
        ONE: str = "3"
        TWO: str = "4"
        """

        @scenario.run_and_check_mypy_after(
            additional_properties={"custom_settings": custom_settings}
        )
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_not_restart()

        @scenario.run_and_check_mypy_after(
            additional_properties={"custom_settings": custom_settings}
        )
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_not_restart()

        # removed names, same types, different values should not restart
        custom_settings = """
        TWO: str = "4"
        """

        @scenario.run_and_check_mypy_after(
            additional_properties={"custom_settings": custom_settings}
        )
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_restart()

        @scenario.run_and_check_mypy_after(
            additional_properties={"custom_settings": custom_settings}
        )
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_not_restart()

    def test_sees_apps_removed_when_they_still_exist_but_no_longer_installed(
        self, scenario: Scenario
    ) -> None:
        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "main.py",
                """
                from extended_mypy_django_plugin import Concrete, DefaultQuerySet

                from myapp.models import Parent

                models: Concrete[Parent]
                # ^ REVEAL[concrete-parent] ^ Union[myapp.models.Child1, myapp.models.Child2, myapp.models.Child3, myapp2.models.ChildOther]

                qs: DefaultQuerySet[Parent]
                # ^ REVEAL[qs-parent] ^ Union[django.db.models.query.QuerySet[myapp.models.Child1, myapp.models.Child1], myapp.models.Child2QuerySet, django.db.models.query.QuerySet[myapp.models.Child3, myapp.models.Child3], django.db.models.query.QuerySet[myapp2.models.ChildOther, myapp2.models.ChildOther]]
                """,
            )

        # Now let's remove myapp2 from the installed_apps and see that the daemon restarts and myapp2 is removed from the revealed types

        @scenario.run_and_check_mypy_after(installed_apps=["myapp"])
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_restart()

            (
                expected.on("main.py")
                .remove_from_revealed_type(
                    "concrete-parent",
                    ", myapp2.models.ChildOther",
                )
                .remove_from_revealed_type(
                    "qs-parent",
                    ", django.db.models.query.QuerySet[myapp2.models.ChildOther, myapp2.models.ChildOther]",
                )
            )

    def test_does_not_see_apps_that_exist_but_are_not_installed(self, scenario: Scenario) -> None:
        @scenario.run_and_check_mypy_after(
            installed_apps=["myapp"], copied_apps=["myapp", "myapp2"]
        )
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "main.py",
                """
                from extended_mypy_django_plugin import Concrete, DefaultQuerySet

                from myapp.models import Parent

                model: Concrete[Parent]
                model.concrete_from_myapp

                qs: DefaultQuerySet[Parent]
                qs.values("concrete_from_myapp")
                """,
            )

        # And after installing the app means the types expand

        @scenario.run_and_check_mypy_after(installed_apps=["myapp", "myapp2"])
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_restart()

            (
                expected.on("main.py")
                .add_error(
                    6,
                    "union-attr",
                    'Item "ChildOther" of "Child1 | Child2 | Child3 | ChildOther" has no attribute "concrete_from_myapp"',
                )
                .add_error(
                    9,
                    "misc",
                    "Cannot resolve keyword 'concrete_from_myapp' into field. Choices are: concrete_from_myapp2, id, one, two",
                )
            )

    def test_sees_models_when_they_are_added_and_installed(self, scenario: Scenario) -> None:
        @scenario.run_and_check_mypy_after(installed_apps=["myapp"])
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "main.py",
                """
                from extended_mypy_django_plugin import Concrete, DefaultQuerySet

                from myapp.models import Parent

                models: Concrete[Parent]
                # ^ REVEAL[concrete-parent] ^ Union[myapp.models.Child1, myapp.models.Child2, myapp.models.Child3]

                qs: DefaultQuerySet[Parent]
                qs.values("concrete_from_myapp")
                # ^ TAG[concrete-qs] ^
                """,
            )

        # and the models become available after being installed

        @scenario.run_and_check_mypy_after(installed_apps=["myapp", "myapp2"])
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_restart()

            (
                expected.on("main.py")
                .add_revealed_type(
                    "concrete-parent",
                    "Union[myapp.models.Child1, myapp.models.Child2, myapp.models.Child3, myapp2.models.ChildOther]",
                )
                .add_error(
                    "concrete-qs",
                    "misc",
                    "Cannot resolve keyword 'concrete_from_myapp' into field. Choices are: concrete_from_myapp2, id, one, two",
                )
            )

        # And same output if nothing changes

        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_not_restart()

    def test_sees_new_models(self, scenario: Scenario) -> None:
        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "main.py",
                """
                from extended_mypy_django_plugin import Concrete, DefaultQuerySet

                from myapp.models import Parent

                models: Concrete[Parent]
                models.two

                qs: DefaultQuerySet[Parent]
                qs.values("two")
                """,
            )

        # And if we add some more models

        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            scenario.append_to_file(
                expected,
                "myapp2/models.py",
                """
                class Another(Parent):
                    pass
                """,
            )

            expected.daemon_should_restart()

            (
                expected.on("main.py")
                .add_error(
                    6,
                    "union-attr",
                    'Item "Another" of "Child1 | Child2 | Child3 | ChildOther | Another" has no attribute "two"',
                )
                .add_error(
                    9, "misc", "Cannot resolve keyword 'two' into field. Choices are: id, one"
                )
            )

        # And the new model remains after a rerun

        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_not_restart()

    def test_sees_changes_in_custom_querysets_within_app(self, scenario: Scenario) -> None:
        @scenario.run_and_check_mypy_after(installed_apps=["leader", "follower1"])
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "main.py",
                """
                from extended_mypy_django_plugin import Concrete, DefaultQuerySet

                from leader.models import Leader

                models: Concrete[Leader]
                # ^ REVEAL[concrete-leader] ^ follower1.models.follower1.Follower1

                qs: DefaultQuerySet[Leader]
                # ^ REVEAL[qs-leader] ^ follower1.models.follower1.Follower1QuerySet

                qs.good_ones().values("nup")
                # ^ ERROR(misc)[error1] ^ Cannot resolve keyword 'nup' into field. Choices are: from_follower1, good, id
                """,
            )

        # And then add another model

        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "follower1/models/__init__.py",
                """
                from .follower1 import Follower1
                from .follower2 import Follower2

                __all__ = ["Follower1", "Follower2"]
                """,
            )

            scenario.file(
                expected,
                "follower1/models/follower2.py",
                """
                from django.db import models
                from leader.models import Leader

                class Follower2QuerySet(models.QuerySet["Follower2"]):
                    def good_ones(self) -> "Follower2QuerySet":
                        return self.filter(good=True)

                Follower2Manager = models.Manager.from_queryset(Follower2QuerySet)

                class Follower2(Leader):
                    good = models.BooleanField()

                    objects = Follower2Manager()
                """,
            )

            expected.daemon_should_restart()

            (
                expected.on("main.py")
                .add_revealed_type(
                    "concrete-leader",
                    "Union[follower1.models.follower1.Follower1, follower1.models.follower2.Follower2]",
                )
                .add_revealed_type(
                    "qs-leader",
                    "Union[follower1.models.follower1.Follower1QuerySet, follower1.models.follower2.Follower2QuerySet]",
                )
                .replace_errors(
                    "error1",
                    (
                        "misc",
                        "Cannot resolve keyword 'nup' into field. Choices are: from_follower1, good, id",
                    ),
                    (
                        "misc",
                        "Cannot resolve keyword 'nup' into field. Choices are: good, id",
                    ),
                )
            )

        # And same output, no daemon restart on no change

        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_not_restart()

        # And removing the method from the queryset

        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "follower1/models/follower2.py",
                """
                from django.db import models
                from leader.models import Leader

                class Follower2QuerySet(models.QuerySet["Follower2"]):
                    pass

                Follower2Manager = models.Manager.from_queryset(Follower2QuerySet)

                class Follower2(Leader):
                    good = models.BooleanField()

                    objects = Follower2Manager()
                """,
            )

            (
                expected.on("main.py").replace_errors(
                    "error1",
                    (
                        "union-attr",
                        'Item "Follower2QuerySet" of "Follower1QuerySet | Follower2QuerySet" has no attribute "good_ones"',
                    ),
                    (
                        "misc",
                        "Cannot resolve keyword 'nup' into field. Choices are: from_follower1, good, id",
                    ),
                )
            )

    def test_sees_changes_in_custom_querysets_in_new_apps(self, scenario: Scenario) -> None:
        @scenario.run_and_check_mypy_after(installed_apps=["leader", "follower1"])
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "main.py",
                """
                from extended_mypy_django_plugin import Concrete, DefaultQuerySet

                from leader.models import Leader

                models: Concrete[Leader]
                # ^ REVEAL[concrete-leader] ^ follower1.models.follower1.Follower1

                qs: DefaultQuerySet[Leader]
                # ^ REVEAL[qs-leader] ^ follower1.models.follower1.Follower1QuerySet

                qs.good_ones().values("nup")
                # ^ ERROR(misc)[error1] ^ Cannot resolve keyword 'nup' into field. Choices are: from_follower1, good, id
                """,
            )

        # Let's then add a new app with new models

        @scenario.run_and_check_mypy_after(installed_apps=["leader", "follower1", "follower2"])
        def _(expected: OutputBuilder) -> None:
            scenario.file(expected, "follower2/__init__.py", "")

            scenario.file(
                expected,
                "follower2/apps.py",
                """
                from django.apps import AppConfig
                class Config(AppConfig):
                    name = "follower2"
                """,
            )

            scenario.file(
                expected,
                "follower2/models.py",
                """
                from django.db import models
                from leader.models import Leader

                class Follower2QuerySet(models.QuerySet["Follower2"]):
                    def good_ones(self) -> "Follower2QuerySet":
                        return self.filter(good=True)

                Follower2Manager = models.Manager.from_queryset(Follower2QuerySet)

                class Follower2(Leader):
                    good = models.BooleanField()

                    objects = Follower2Manager()
                """,
            )

            expected.daemon_should_restart()

            (
                expected.on("main.py")
                .add_revealed_type(
                    "concrete-leader",
                    "Union[follower1.models.follower1.Follower1, follower2.models.Follower2]",
                )
                .add_revealed_type(
                    "qs-leader",
                    "Union[follower1.models.follower1.Follower1QuerySet, follower2.models.Follower2QuerySet]",
                )
                .replace_errors(
                    "error1",
                    (
                        "misc",
                        "Cannot resolve keyword 'nup' into field. Choices are: from_follower1, good, id",
                    ),
                    (
                        "misc",
                        "Cannot resolve keyword 'nup' into field. Choices are: good, id",
                    ),
                )
            )

        # And everything stays the same on rerun

        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            expected.daemon_should_not_restart()

        # And it sees where custom queryset gets queryset manager removed

        @scenario.run_and_check_mypy_after
        def _(expected: OutputBuilder) -> None:
            scenario.file(
                expected,
                "follower2/models.py",
                """
                from django.db import models
                from leader.models import Leader

                class Follower2QuerySet(models.QuerySet["Follower2"]):
                    pass

                Follower2Manager = models.Manager.from_queryset(Follower2QuerySet)

                class Follower2(Leader):
                    good = models.BooleanField()

                    objects = Follower2Manager()
                """,
            )

            (
                expected.on("main.py").replace_errors(
                    "error1",
                    (
                        "union-attr",
                        'Item "Follower2QuerySet" of "Follower1QuerySet | Follower2QuerySet" has no attribute "good_ones"',
                    ),
                    (
                        "misc",
                        "Cannot resolve keyword 'nup' into field. Choices are: from_follower1, good, id",
                    ),
                )
            )
