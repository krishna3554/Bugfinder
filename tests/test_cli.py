from pathlib import Path

from bugfinder.cli import write_markdown


def test_write_markdown_creates_parent_and_final_newline(tmp_path: Path):
    output = tmp_path / "reports" / "result.md"
    write_markdown(output, "# Result\n")
    assert output.read_text(encoding="utf-8") == "# Result\n"
