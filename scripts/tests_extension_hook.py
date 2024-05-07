import ast
import os
import pathlib
import runpy
from collections.abc import Mapping, MutableSequence
from typing import TYPE_CHECKING

from pytest_mypy_plugins import (
    ExtensionHook,
    FollowupFile,
    ItemForHook,
    MypyPluginsScenario,
    OutputMatcher,
    ScenarioHookMaker,
    ScenarioHooks,
    ScenarioHooksRunAndCheckOptions,
)

here = pathlib.Path(__file__).parent


def django_plugin_hook(item: ItemForHook) -> None:
    django_settings_section = (
        "\n[mypy.plugins.django-stubs]\n" "django_settings_module = mysettings"
    )

    if not item.additional_mypy_config:
        item.additional_mypy_config = django_settings_section
    else:
        if "[mypy.plugins.django-stubs]" not in item.additional_mypy_config:
            item.additional_mypy_config += django_settings_section


class Hooks(ScenarioHooks):
    def before_run_and_check_mypy(
        self,
        *,
        scenario: MypyPluginsScenario,
        options: ScenarioHooksRunAndCheckOptions,
        config_file: pathlib.Path,
        expected_output: MutableSequence[OutputMatcher],
        additional_properties: Mapping[str, object],
    ) -> ScenarioHooksRunAndCheckOptions:
        custom_settings = additional_properties.get("custom_settings", None)
        installed_apps = additional_properties.get("installed_apps", None)
        monkeypatch = additional_properties.get("monkeypatch", None)

        current_settings: pathlib.Path = scenario.path_for("mysettings.py")

        if custom_settings is None and installed_apps is None and monkeypatch is None:
            if current_settings.exists():
                return options

        if not current_settings.exists():
            with open(current_settings, "w") as fle:
                fle.write("")

        original_settings_text = current_settings.read_text()

        if monkeypatch is not None:
            monkeypatch_str = "import django_stubs_ext\ndjango_stubs_ext.monkeypatch()\n"
            settings_text = original_settings_text.replace(monkeypatch_str, "")
            if monkeypatch:
                settings_text = monkeypatch_str + settings_text

            with open(current_settings, "w") as fle:
                fle.write(settings_text)

        settings_values = runpy.run_path(str(current_settings))

        if "INSTALLED_APPS" not in settings_values:
            with open(current_settings, "a") as fle:
                fle.write("\nINSTALLED_APPS = None")

        if "SECRET_KEY" not in settings_values:
            with open(current_settings, "a") as fle:
                fle.write('\nSECRET_KEY = "1"')

        settings = ast.parse(current_settings.read_text())

        class Fixer(ast.NodeTransformer):
            def visit_Assign(self, node: ast.Assign) -> ast.Assign:
                match node.targets:
                    case [ast.Name(id="INSTALLED_APPS")]:
                        nonlocal installed_apps
                        if not isinstance(node.value, ast.List):
                            installed_apps = installed_apps or ["myapp", "myapp2"]
                        elif installed_apps is None and isinstance(
                            settings_values["INSTALLED_APPS"], list
                        ):
                            installed_apps = settings_values["INSTALLED_APPS"]

                        if not isinstance(installed_apps, list):
                            installed_apps = []

                        if "django.contrib.contenttypes" not in installed_apps:
                            installed_apps.insert(0, "django.contrib.contenttypes")

                        return ast.Assign(
                            targets=node.targets,
                            value=ast.List(
                                elts=[ast.Constant(value=app) for app in installed_apps]
                            ),
                        )
                    case _:
                        return node

        Fixer().visit(settings)
        with open(current_settings, "w") as fle:
            fle.write(ast.unparse(ast.fix_missing_locations(settings)))
            if isinstance(custom_settings, str):
                fle.write("\n")
                fle.write(custom_settings)

        if current_settings.read_text() != original_settings_text:
            new_settings = current_settings.read_text()
            current_settings.write_text("")
            # Make it recorded that the settings changed
            scenario.handle_followup_file(
                FollowupFile(path=current_settings.name, content=new_settings)
            )

        settings_values = runpy.run_path(str(current_settings))
        installed_apps = settings_values["INSTALLED_APPS"]

        if not isinstance(installed_apps, list):
            installed_apps = []

        if "myapp" in installed_apps:
            for root, _, files in os.walk(here / "myapp"):
                for name in files:
                    location = pathlib.Path(root, name)
                    scenario.handle_followup_file(
                        FollowupFile(
                            path=str(location.relative_to(here)), content=location.read_text()
                        )
                    )
        if "myapp2" in installed_apps:
            for root, _, files in os.walk(here / "myapp2"):
                for name in files:
                    location = pathlib.Path(root, name)
                    scenario.handle_followup_file(
                        FollowupFile(
                            path=str(location.relative_to(here)), content=location.read_text()
                        )
                    )

        return options


if TYPE_CHECKING:
    _eh: ExtensionHook = django_plugin_hook
    _sh: ScenarioHookMaker = Hooks
