from pathlib import Path

from szymonmiks_deployment.file_collector import WebsiteFileCollector


def test_can_collect_files() -> None:
    # given
    base_dir = Path(__file__).parent
    collector = WebsiteFileCollector(base_dir)
    collector.EXCLUDED = []

    # when
    result = collector.collect()

    # then
    path = Path(__file__).parent / "conftest.py"
    assert path in result


def test_can_collect_files_if_excluded_defined() -> None:
    # given
    base_dir = Path(__file__).parent
    collector = WebsiteFileCollector(base_dir)
    collector.EXCLUDED = ["tests"]

    # when
    result = collector.collect()

    # then
    assert result == []
