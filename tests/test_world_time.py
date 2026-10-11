"""Tests for the !wt country-name detection."""

import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "barbot.py"
tree = ast.parse(SOURCE.read_text(encoding="utf-8"))

function = next(
    node for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name == "world_time_country"
)

module = ast.Module(body=[function], type_ignores=[])

namespace = {
    "pytz": SimpleNamespace(
        country_names={
            "JP": "Japan",
            "US": "United States",
            "DE": "Germany",
            "GB": "Britain (UK)",
            "ES": "Spain",
            "IS": "Iceland",
        }
    )
}

exec(compile(module, str(SOURCE), "exec"), namespace)
world_time_country = namespace["world_time_country"]


class TestWorldTimeCountry(unittest.TestCase):

    def test_country_names(self):
        for name, code in [
            ("Japan", "JP"),
            ("USA", "US"),
            ("Germany", "DE"),
            ("United States", "US"),
            ("UK", "GB"),
            ("Spain", "ES"),
        ]:
            with self.subTest(name=name):
                self.assertEqual(world_time_country(name), code)

    def test_country_codes(self):
        self.assertEqual(world_time_country("JP"), "JP")
        self.assertEqual(world_time_country("US"), "US")

    def test_case_insensitive(self):
        self.assertEqual(world_time_country("jApAn"), "JP")
        self.assertEqual(world_time_country(" usa "), "US")

    def test_cities_are_not_countries(self):
        for city in ["Tokyo", "Barcelona", "New York", "Berlin"]:
            with self.subTest(city=city):
                self.assertIsNone(world_time_country(city))

    def test_city_country_is_not_country_only(self):
        self.assertIsNone(world_time_country("Tokyo, Japan"))
        self.assertIsNone(world_time_country("Barcelona, Spain"))


class TestWorldTimeHandler(unittest.TestCase):

    def test_country_prompt(self):
        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        bot_class = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "BarBot"
        )
        handler = next(
            node for node in bot_class.body
            if isinstance(node, ast.FunctionDef) and node.name == "on_pubmsg"
        )

        wt_branch = next(
            node for node in ast.walk(handler)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.BoolOp)
            and any(
                isinstance(value, ast.Compare)
                and isinstance(value.left, ast.Name)
                and value.left.id == "lowered"
                and any(
                    isinstance(comp, ast.Constant) and comp.value == "!wt"
                    for comp in value.comparators
                )
                for value in node.test.values
            )
        )

        branch_function = ast.FunctionDef(
            name="run_wt",
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="msg"),
                    ast.arg(arg="nick"),
                    ast.arg(arg="c"),
                    ast.arg(arg="locations"),
                ],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[
                ast.Assign(
                    targets=[ast.Name(id="lowered", ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="msg", ctx=ast.Load()),
                            attr="lower",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    ),
                ),
                *wt_branch.body,
            ],
            decorator_list=[],
        )

        module = ast.fix_missing_locations(
            ast.Module(body=[branch_function], type_ignores=[])
        )

        from unittest.mock import Mock
        from datetime import datetime
        from zoneinfo import ZoneInfo

        env = {
            "world_time_country": world_time_country,
            "CHANNEL": "##bar-jp",
            "pytz": SimpleNamespace(
                country_timezones={
                    "US": ["America/New_York", "America/Los_Angeles"],
                    "DE": ["Europe/Berlin", "Europe/Busingen"],
                    "JP": ["Asia/Tokyo"],
                    "IS": ["Atlantic/Reykjavik"],
                },
                country_names={"JP": "Japan", "IS": "Iceland"},
                timezone=ZoneInfo,
            ),
            "datetime": datetime,
            "geocode_location": Mock(
                side_effect=AssertionError("Geocoding must not be called")
            ),
        }

        exec(compile(module, str(SOURCE), "exec"), env)

        for location, example in [
            ("USA", "New York, USA"),
            ("Germany", "Berlin, Germany"),
        ]:
            with self.subTest(location=location):
                connection = Mock()
                env["run_wt"](
                    f"!wt {location}",
                    "hype",
                    connection,
                    {},
                )
                connection.privmsg.assert_called_once_with(
                    "##bar-jp",
                    f"hype: Please specify a city (e.g. {example}).",
                )


        for country in ("Japan", "Iceland"):
            with self.subTest(country=country):
                connection = Mock()
                env["run_wt"](f"!wt {country}", "hype", connection, {})
                connection.privmsg.assert_called_once()
                channel, reply = connection.privmsg.call_args.args
                self.assertEqual(channel, "##bar-jp")
                self.assertRegex(
                    reply,
                    rf"^{country}: [0-9]{{2}}:[0-9]{{2}} .+ \([A-Za-z]{{3}}\)$",
                )


    def test_city_and_registered_location(self):
        from unittest.mock import Mock
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from types import SimpleNamespace

        source = SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)

        bot_class = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "BarBot"
        )
        handler = next(
            node for node in bot_class.body
            if isinstance(node, ast.FunctionDef) and node.name == "on_pubmsg"
        )
        wt_branch = next(
            node for node in ast.walk(handler)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.BoolOp)
            and any(
                isinstance(value, ast.Compare)
                and isinstance(value.left, ast.Name)
                and value.left.id == "lowered"
                and any(
                    isinstance(comp, ast.Constant) and comp.value == "!wt"
                    for comp in value.comparators
                )
                for value in node.test.values
            )
        )

        runner = ast.FunctionDef(
            name="run_wt",
            args=ast.arguments(
                posonlyargs=[],
                args=[
                    ast.arg(arg="msg"),
                    ast.arg(arg="nick"),
                    ast.arg(arg="c"),
                    ast.arg(arg="locations"),
                ],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[
                ast.Assign(
                    targets=[ast.Name(id="lowered", ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="msg", ctx=ast.Load()),
                            attr="lower",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[],
                    ),
                ),
                *wt_branch.body,
            ],
            decorator_list=[],
        )

        module = ast.fix_missing_locations(
            ast.Module(body=[runner], type_ignores=[])
        )

        places = {
            "Tokyo": {
                "name": "Tokyo",
                "country": "Japan",
                "timezone": "Asia/Tokyo",
            },
            "Barcelona": {
                "name": "Barcelona",
                "country": "Spain",
                "timezone": "Europe/Madrid",
            },
            "Japan, Japan": {
                "name": "Japan",
                "country": "Japan",
                "timezone": "Asia/Tokyo",
            },
        }

        geocode = Mock(side_effect=lambda location: places.get(location))
        env = {
            "world_time_country": world_time_country,
            "geocode_location": geocode,
            "CHANNEL": "##bar-jp",
            "pytz": SimpleNamespace(timezone=ZoneInfo),
            "datetime": datetime,
        }

        exec(compile(module, str(SOURCE), "exec"), env)

        cases = [
            ("!wt Tokyo", {}, "Tokyo, Japan:"),
            ("!wt Barcelona", {}, "Barcelona, Spain:"),
            ("!wt", {"hype": "Tokyo"}, "Tokyo, Japan:"),
            ("!wt Japan, Japan", {}, "Japan:"),
        ]

        for command, locations, expected_prefix in cases:
            with self.subTest(command=command):
                connection = Mock()
                env["run_wt"](command, "hype", connection, locations)
                connection.privmsg.assert_called_once()
                channel, reply = connection.privmsg.call_args.args
                self.assertEqual(channel, "##bar-jp")
                self.assertTrue(
                    reply.startswith(expected_prefix),
                    f"Unexpected reply: {reply}",
                )
                self.assertNotIn("Japan, Japan:", reply)

        connection = Mock()
        env["run_wt"]("!wt", "hype", connection, {})
        connection.privmsg.assert_called_once_with(
            "##bar-jp",
            "hype: no location registered. Use !loc City, Country",
        )


if __name__ == "__main__":
    unittest.main()
