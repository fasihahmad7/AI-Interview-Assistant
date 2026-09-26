"""
Unit tests for UIManager text formatting.
Run with: pytest tests/
"""
from src.ui.ui_manager import UIManager


def fmt(text):
    # Skip __init__, which injects CSS through Streamlit
    return UIManager.__new__(UIManager)._format_rich_text(text)


def test_dash_bullets_become_list_items():
    out = fmt("- Measure first\n- Quarantine flaky tests")
    assert out.count("<li>") == 2 and out.startswith("<ul>")


def test_star_and_numbered_bullets_become_list_items():
    out = fmt("* one\n1. two\n2. three")
    assert out.count("<li>") == 3


def test_section_heading_detected():
    out = fmt("Key Strengths:\n- Clear plan")
    assert '<div class="section-heading">Key Strengths:</div>' in out


def test_markdown_bold_converted():
    assert "<b>Page Object Model</b>" in fmt("Use the **Page Object Model** here")


def test_inline_code_converted():
    assert "<code>driver.findElement()</code>" in fmt("Call `driver.findElement()` once")


def test_angle_brackets_are_escaped():
    out = fmt("Return a List<WebElement> from findElements")
    assert "List&lt;WebElement&gt;" in out


def test_blank_lines_add_no_spacing():
    assert "<br>" not in fmt("Technical Assessment:\n\n- Knowledge Depth: 7.5 - ok\n\n")
