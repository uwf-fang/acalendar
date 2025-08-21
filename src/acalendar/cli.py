import click
import tomli
from acalendar.calendar import CourseTerm

@click.command()
@click.option('--config', '-c', 'conf_file', required=True, type=str, help='configuration file for the run')
@click.option('--latex', '-l', 'latex', is_flag=True, default=False, type=bool, help='Output latex snippet')
@click.option('--csv', '-v', 'csv', is_flag=True, default=False, type=bool, help='Output CSV text')
@click.option('--html', '-h', 'html', is_flag=True, default=False, type=bool, help='Output html')
def run(conf_file: str, latex: bool, csv: bool, html: bool) -> None:
    """
    CLI entrypoint for generating academic calendar outputs.

    Args:
        conf_file (str): Path to configuration TOML file.
        latex (bool): Output LaTeX snippet if True.
        csv (bool): Output CSV text if True.
        html (bool): Output HTML if True.
    """
    with open(conf_file, 'rb') as f:
        conf = tomli.load(f)
    start_date: str = conf.get('first_day')
    end_date: str = conf.get('last_day')
    module_titles: str = conf.get('module_titles', "")
    module_events: str = conf.get('module_events', "")
    spring_break: str = conf.get('spring_break', "")

    cal: CourseTerm = CourseTerm(
        start_date=start_date,
        end_date=end_date,
        module_titles=module_titles,
        module_events=module_events,
        spring_break=spring_break
    )
    if latex:
        print(cal.tex)
    if html:
        print(cal.html)
    if csv:
        print(cal.csv)

if __name__ == "__main__":
    run()