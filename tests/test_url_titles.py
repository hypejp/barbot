"""URLタイトル取得機能の回帰テスト。"""

import ast
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup


SOURCE = Path(__file__).resolve().parents[1] / "barbot.py"


def load_fetch_title():
    """IRC接続を開始せず、fetch_title関数だけを読み込む。"""
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "fetch_title"
    )
    module = ast.Module(body=[function], type_ignores=[])
    namespace = {"requests": requests, "BeautifulSoup": BeautifulSoup}
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return namespace["fetch_title"]


class TestURLTitles(unittest.TestCase):

    def test_wikipedia_user_agent(self):
        response = Mock()
        response.status_code = 200
        response.text = "<html><head><title>Sekisui House - Wikipedia</title></head></html>"
        response.apparent_encoding = "utf-8"

        with patch.object(requests, "get", return_value=response) as get:
            title = load_fetch_title()(
                "https://en.wikipedia.org/wiki/Sekisui_House"
            )

        self.assertEqual(title, "Sekisui House - Wikipedia")
        self.assertIn("User-Agent", get.call_args.kwargs["headers"])

    def test_youtube_oembed(self):
        response = Mock()
        response.json.return_value = {"title": "Example YouTube Video"}

        with patch.object(requests, "get", return_value=response) as get:
            title = load_fetch_title()(
                "https://www.youtube.com/watch?v=example"
            )

        self.assertEqual(title, "Example YouTube Video")
        self.assertEqual(
            get.call_args.args[0],
            "https://www.youtube.com/oembed",
        )


if __name__ == "__main__":
    unittest.main()
