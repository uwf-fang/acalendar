import click
import tomli
from datetime import date
from pathlib import Path
from acalendar.calendar import CourseTerm

@click.command()
@click.version_option(package_name='acalendar')
@click.option('--config', '-c', 'conf_file', required=True,
              type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
              help='configuration file for the run')
@click.option('--latex', '-l', 'latex', is_flag=True, default=False, type=bool, help='Output latex snippet')
@click.option('--csv', '-v', 'csv', is_flag=True, default=False, type=bool, help='Output CSV text')
@click.option('--html', '-h', 'html', is_flag=True, default=False, type=bool, help='Output html')
def run(conf_file: Path, latex: bool, csv: bool, html: bool) -> None:
    """
    CLI entrypoint for generating academic calendar outputs.

    Args:
        conf_file (str): Path to configuration TOML file.
        latex (bool): Output LaTeX snippet if True.
        csv (bool): Output CSV text if True.
        html (bool): Output HTML if True.
    """
    if not any((latex, csv, html)):
        raise click.UsageError('Select at least one output format: --csv, --html, or --latex.')
    try:
        with conf_file.open('rb') as stream:
            conf = tomli.load(stream)
        for key in ('first_day', 'last_day'):
            if key not in conf:
                raise ValueError(f'Missing required configuration value: {key}')
        values = {}
        for key in ('first_day', 'last_day', 'module_titles', 'module_events',
                    'spring_break', 'thanksgiving_break'):
            value = conf.get(key, '')
            if key in ('first_day', 'last_day', 'spring_break', 'thanksgiving_break') and isinstance(value, date):
                value = value.isoformat()
            if not isinstance(value, str):
                raise ValueError(f'{key} must be text or a TOML date for date fields')
            values[key] = value.strip()
        cal = CourseTerm(
            start_date=values['first_day'], end_date=values['last_day'],
            module_titles=values['module_titles'], module_events=values['module_events'],
            spring_break=values['spring_break'], thanksgiving_break=values['thanksgiving_break'],
        )
    except (OSError, ValueError) as error:
        raise click.ClickException(str(error)) from error
    if latex:
        print(cal.tex)
    if html:
        print(cal.html)
    if csv:
        print(cal.csv)

if __name__ == "__main__":
    run()
