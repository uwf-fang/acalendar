import csv
import io
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner

from acalendar.calendar import CourseTerm, weeks_of_period
from acalendar.cli import run


def test_single_partial_week_stays_within_term():
    assert weeks_of_period(date(2026, 11, 10), date(2026, 11, 12)) == [
        (date(2026, 11, 10), date(2026, 11, 12))
    ]


def test_unnumbered_lines_and_empty_events():
    term = CourseTerm('2026-11-09', '2026-11-20', 'Introduction\n02. Follow-up', '')
    assert term.module_titles == ['Introduction', 'Follow-up']
    assert term.module_events == ['', '']
    assert len(list(csv.reader(io.StringIO(term.csv)))) == 3


def test_output_formats_preserve_plain_text():
    title = 'Discuss "quotes", <tags> & 50% of module_1'
    term = CourseTerm('2026-11-09', '2026-11-13', title, ' \n')
    rows = list(csv.reader(io.StringIO(term.csv)))
    assert rows[1][2] == title
    assert rows[1][3] == ''
    assert '&lt;tags&gt;' in term.html
    assert '&amp;' in term.html
    assert '<tags>' not in term.html
    assert r'\& 50\% of module\_1' in term.tex


def test_two_distinct_breaks_keep_module_alignment():
    term = CourseTerm('2026-11-02', '2026-11-27', 'Start\nEnd', '',
                      spring_break='2026-11-09', thanksgiving_break='2026-11-23')
    assert term.module_titles == ['Start', 'Spring Break', 'End', 'Thanksgiving Break']
    assert len(term.module_events) == len(term.weeks) == 4


def test_overlapping_breaks_are_rejected():
    with pytest.raises(ValueError, match='different weeks'):
        CourseTerm('2026-11-02', '2026-11-27', 'Start\nEnd', '',
                   spring_break='2026-11-09', thanksgiving_break='2026-11-10')


def test_cli_accepts_native_toml_dates(tmp_path):
    config = tmp_path / 'term.toml'
    config.write_text('first_day = 2026-11-09\nlast_day = 2026-11-13\n')
    result = CliRunner().invoke(run, ['--config', str(config), '--csv'])
    assert result.exit_code == 0, result.output
    assert len(list(csv.reader(io.StringIO(result.output)))) == 2


@pytest.mark.parametrize('content, expected', [
    ('module_titles = "Introduction"\n', 'Missing required configuration value: first_day'),
    ('first_day = 123\nlast_day = "2026-11-13"\n', 'first_day must be text'),
    ('first_day = [\n', 'Error:'),
])
def test_invalid_configuration_has_a_readable_error(tmp_path, content, expected):
    config = tmp_path / 'invalid.toml'
    config.write_text(content)
    result = CliRunner().invoke(run, ['--config', str(config), '--csv'])
    assert result.exit_code != 0
    assert expected in result.output
    assert 'Traceback' not in result.output


def test_cli_requires_an_output_format(tmp_path):
    config = tmp_path / 'term.toml'
    config.write_text('first_day = "2026-11-09"\nlast_day = "2026-11-13"\n')
    result = CliRunner().invoke(run, ['--config', str(config)])
    assert result.exit_code != 0
    assert 'Select at least one output format' in result.output


@pytest.mark.parametrize('config', sorted((Path(__file__).parents[1] / 'calendars').glob('*.toml')),
                         ids=lambda path: path.name)
def test_bundled_configurations(config):
    result = CliRunner().invoke(run, ['--config', str(config), '--csv', '--html', '--latex'])
    if config.name == 'cop3014_25s.toml':
        assert result.exit_code != 0
        assert 'Missing required configuration value: first_day' in result.output
    else:
        assert result.exit_code == 0, result.output
        assert '<table' in result.output
        assert r'\toprule' in result.output
        assert '"Week","Dates","Content","Notes"' in result.output
