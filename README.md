# acalendar

`acalendar` creates academic-term calendars from a TOML configuration file. It
can produce CSV text, a LaTeX table, or an HTML table.

## Features

- Define a term with custom start and end dates.
- Add weekly module titles and events.
- Mark spring and Thanksgiving breaks.
- Generate CSV, LaTeX, and HTML output.

## Installation

The package has not been published to the Python Package Index (PyPI) yet.
PyPI publication is planned and currently pending.

For now, install and run it from a local clone. The project uses Poetry, so
install [Poetry](https://python-poetry.org/docs/) first, then run:

```bash
git clone <repository-url>
cd academic_calendar
poetry install
```

`poetry install` creates or updates the project environment and installs the
runtime dependencies and the `calendar` command.

## How to Run

### 1. View the available options

Run the CLI help command from the repository root:

```bash
poetry run calendar --help
```

The `-c`/`--config` option is required. Select one or more output options:

- `-l`/`--latex`: print a LaTeX table.
- `-v`/`--csv`: print CSV text.
- `-h`/`--html`: print an HTML table.

### 2. Generate an output

The repository includes example configurations in `calendars/`. For example,
to print a calendar as CSV:

```bash
poetry run calendar -c calendars/cop3530_25f.toml -v
```

To generate all three formats at once:

```bash
poetry run calendar \
	--config calendars/cop3530_25f.toml \
	--latex --csv --html
```

The command prints the selected formats to standard output. Redirect the
output to a file when you want to keep it:

```bash
poetry run calendar -c calendars/cop3530_25f.toml --csv > calendar.csv
poetry run calendar -c calendars/cop3530_25f.toml --html > calendar.html
poetry run calendar -c calendars/cop3530_25f.toml --latex > calendar.tex
```

### 3. Create or edit a configuration

A configuration file must include `first_day`, `last_day`, `module_titles`,
and `module_events`. Dates use `YYYY-MM-DD` format. The optional
`spring_break` and `thanksgiving_break` values also use that format; leave them
empty when the term has no such break.

`module_titles` and `module_events` contain one numbered line per instructional
week. The number and period are removed when the calendar is generated:

```toml
first_day = "2025-08-25"
last_day = "2025-09-05"
spring_break = ""
thanksgiving_break = ""

module_titles = """
01. Course introduction
02. Testing and modular design
"""

module_events = """
01. Assignment due
02. No special event
"""
```

The number of title and event lines must match the number of weeks in the
term. A break adds a generated `No classes` week, so the input lists should
contain only instructional weeks.

## Development

Run the test suite with:

```bash
poetry run pytest
```

Contributions are welcome. Please add or update tests for changes and open a
pull request with a clear description.
