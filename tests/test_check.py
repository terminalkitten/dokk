import shutil
from pathlib import Path

import pytest

from dokk.check import Issue, check
from dokk.cli import main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "basic"


def test_example_is_clean(tmp_path: Path) -> None:
    root = tmp_path / "basic"
    shutil.copytree(EXAMPLE, root, ignore=shutil.ignore_patterns("dist", ".dokk"))
    assert [i for i in check(root) if i.level == "error"] == []
    assert not (root / ".dokk" / "build").exists()  # check builds into a temp dir


@pytest.mark.parametrize("site_url", ["https://x.io/", "https://x.io/repo/"])
def test_finds_broken_links_anchors_and_assets(make_site, site_url: str) -> None:
    root = make_site(
        {
            "index.md": "---\ntitle: Home\n---\n## Real\n\n[ok](a.md#real-a) [self](#real)\n",
            "a.md": (
                "---\ntitle: A\n---\n## Real A\n\n"
                "[gone](missing.md) [bad anchor](index.md#nope) [bad self](#nope-here)\n"
                "![img](nope.png) [draft](draft.md)\n"
            ),
            "draft.md": "---\ntitle: D\ndraft: true\n---\n",
            "untitled.md": "No heading here.\n",
        },
        f'title = "T"\nsite_url = "{site_url}"\n',
    )
    base = "/repo" if "repo" in site_url else ""
    assert sorted(map(str, check(root))) == sorted(
        [
            "error: a.md: broken link 'missing.md'",
            "error: a.md: broken link 'nope.png'",
            "error: a.md: broken link 'draft.md'",
            f"error: a.md: missing anchor: {base}/#nope",
            "error: a.md: missing anchor: #nope-here",
            "warning: untitled.md: no title, using 'Untitled'",
        ]
    )


def test_build_errors_become_issues(make_site) -> None:
    root = make_site({"a_b.md": "x", "a-b.md": "y"})
    [issue] = check(root)
    assert issue.level == "error" and "route /a-b/ is produced by both" in issue.message
    assert str(issue).startswith("error: route")


def test_cli_exit_codes(make_site, capsys: pytest.CaptureFixture[str]) -> None:
    root = make_site({"index.md": "# Home\n\n[x](nope.md)\n"})
    assert main(["check", "--root", str(root)]) == 1
    captured = capsys.readouterr()
    assert "error: index.md: broken link 'nope.md'" in captured.err
    assert "1 error(s), 0 warning(s)" in captured.out

    (root / "docs" / "index.md").write_text("# Home\n")
    assert main(["check", "--root", str(root)]) == 0


def test_issue_str() -> None:
    assert str(Issue("warning", "a.md", "m")) == "warning: a.md: m"
