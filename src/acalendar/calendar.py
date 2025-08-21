"""
Module of academic calendar related features
"""

import os
from datetime import date, timedelta, datetime

from jinja2 import Environment, FileSystemLoader
from dateutil.rrule import rrule, WEEKLY
from typing import Tuple, List, ClassVar

MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)


def find_weekday_same_week(date_: date, weekday: int) -> date:
    """
    Return the date of the specified weekday in the same week as date_.

    Args:
        date_ (date): Reference date.
        weekday (int): Target weekday (0=Monday, ..., 6=Sunday).

    Returns:
        date: Date of the target weekday in the same week.
    """
    offset: int = weekday - date_.weekday()
    return date_ + timedelta(days=offset)


def find_weekday_next_week(date_: date, weekday: int) -> date:
    """
    Return the date of the specified weekday in the next week after date_.

    Args:
        date_ (date): Reference date.
        weekday (int): Target weekday (0=Monday, ..., 6=Sunday).

    Returns:
        date: Date of the target weekday in the next week.
    """
    days_until_next_week: int = 7 - date_.weekday()
    return date_ + timedelta(days=days_until_next_week + weekday)


def weeks_of_period(start_date: date, end_date: date) -> List[Tuple[date, date]]:
    """
    Generate a list of (week_start, week_end) tuples for each week in the period.

    Args:
        start_date (date): First day of the period.
        end_date (date): Last day of the period.

    Returns:
        List[Tuple[date, date]]: List of tuples (week_start, week_end).
    """
    # Adjust start and end dates to week boundaries
    if start_date.weekday() > FRIDAY:
        start_date = find_weekday_next_week(start_date, MONDAY)
    if end_date.weekday() > FRIDAY:
        end_date = find_weekday_same_week(end_date, FRIDAY)
    week_starts: List[datetime] = list(rrule(WEEKLY, dtstart=find_weekday_same_week(start_date, MONDAY), until=end_date))
    weeks: List[Tuple[date, date]] = [(dt.date(), find_weekday_same_week(dt.date(), FRIDAY)) for dt in week_starts]
    if weeks:
        weeks[0] = (max(start_date, find_weekday_same_week(start_date, MONDAY)),
                    find_weekday_same_week(start_date, FRIDAY))
        weeks[-1] = (find_weekday_same_week(end_date, MONDAY),
                     min(end_date, find_weekday_same_week(end_date, FRIDAY)))
    return weeks


def quoted(text: str) -> str:
    """
    Return the input text wrapped in double quotes.

    Args:
        text (str): Input string.

    Returns:
        str: Quoted string.
    """
    return f'"{text}"'


def parse_lines(content_text: str, num_weeks: int, name: str) -> List[str]:
    """
    Parse a multi-line string into a list of lines, removing leading line numbers.

    Args:
        content_text (str): The multi-line string to parse.
        num_weeks (int): Expected number of lines (weeks).
        name (str): Name of the content type (for error reporting).

    Returns:
        List[str]: List of parsed lines.

    Raises:
        ValueError: If the number of lines does not match num_weeks.
    """
    if not content_text:
        return []
    content_lines: List[str] = [line[3:].strip() for line in content_text.split('\n') if line.strip()]
    if len(content_lines) != num_weeks:
        raise ValueError(f'Number of {name} does not agree with number of weeks')
    return content_lines

class CourseTerm:
    """
    Class that handles the academic calendar of a term (spring, fall, etc.)
    """

    _start_date: date
    _end_date: date
    _weeks: List[Tuple[date, date]]
    _num_weeks: int
    _module_titles: List[str]
    _module_events: List[str]
    _input_date_format: ClassVar[str] = '%Y-%m-%d'
    _spring_break_week: int  # -1 if no spring break

    def __init__(self,
                 start_date: str,
                 end_date: str,
                 module_titles: str,
                 module_events: str,
                 spring_break: str = ''
    ) -> None:
        # Validate and parse start_date
        try:
            self._start_date = datetime.strptime(start_date, self._input_date_format).date()
        except Exception:
            raise ValueError(f"Invalid start date format '{start_date}'. Expected {self._input_date_format}")

        # Validate and parse end_date
        try:
            self._end_date = datetime.strptime(end_date, self._input_date_format).date()
        except Exception:
            raise ValueError(f"Invalid end date format '{end_date}'. Expected {self._input_date_format}")

        if self._end_date <= self._start_date:
            raise ValueError(f"End date ({end_date}) must be after start date ({start_date})")

        self._weeks = weeks_of_period(self._start_date, self._end_date)
        self._num_weeks = len(self._weeks)

        # Validate and parse spring_break
        if spring_break:
            self._num_weeks = self._num_weeks - 1  # exclude spring break week
            try:
                date_of_week = datetime.strptime(spring_break, self._input_date_format).date()
            except Exception:
                raise ValueError(f"Invalid spring break date format '{spring_break}'. Expected {self._input_date_format}")
            if not (self._start_date <= date_of_week <= self._end_date):
                raise ValueError("Spring break must be within the term dates")
            self._spring_break_week = -1
            for i, (week_start, week_end) in enumerate(self.weeks):
                if week_start <= date_of_week <= week_end:
                    self._spring_break_week = i
                    break
            if self._spring_break_week == -1:
                raise ValueError("Spring break date does not match any week in the term")
        else:
            self._spring_break_week = -1

        self._module_titles = parse_lines(module_titles, self._num_weeks, 'titles')
        self._module_events = parse_lines(module_events, self._num_weeks, 'events')

        # insert spring break into titles and events list
        if self._spring_break_week != -1:
            self._module_titles.insert(self._spring_break_week, "Spring Break")
            self._module_events.insert(self._spring_break_week, "No classes")

    @property
    def weeks(self) -> List[Tuple[date, date]]:
        """
        Get the list of week start/end tuples.

        Returns:
            List[Tuple[date, date]]: List of week boundaries.
        """
        return self._weeks

    @property
    def module_titles(self) -> List[str]:
        """
        Get the list of module titles.

        Returns:
            List[str]: Module titles for each week.
        """
        return self._module_titles

    @property
    def module_events(self) -> List[str]:
        """
        Get the list of module events/notes.

        Returns:
            List[str]: Module events for each week.
        """
        return self._module_events

    def week_idx(self, date_: date) -> int:
        """
        Get the week index for a given date.

        Args:
            date_ (date): Date to look up.

        Returns:
            int: Week index.

        Raises:
            ValueError: If date is not within any week.
        """
        for i, (start, end) in enumerate(self.weeks):
            if start <= date_ <= end:
                return i
        raise ValueError(f'Date {date_.strftime("%y/%m/%d")} is not a valid school day!')

    @property
    def csv(self) -> str:
        """
        Get the calendar as a CSV string.

        Returns:
            str: CSV representation of the calendar.
        """
        columns: List[str] = ['Week', 'Dates', 'Content', 'Notes']
        table_header: str = ','.join(map(quoted, columns))
        date_templ: str = '%m/%d'
        contents: List[str] = [table_header]
        for i, (week_start, week_end) in enumerate(self.weeks):
            content: List[str] = [
                f'"{i + 1}"',
                f'"{week_start.strftime(date_templ)}-{week_end.strftime(date_templ)}"',
                f'"{self._module_titles[i]}"',
                f'"{self._module_events[i]}"'
            ]
            contents.append(','.join(content))
        return '\n'.join(contents)

    @property
    def tex(self) -> str:
        """
        Get the calendar as a LaTeX table string.

        Returns:
            str: LaTeX table representation of the calendar.
        """
        header: str = r'Week \# & Week & Content & Due & Events \\'
        template: str = r'{:02d} & {:s}-{:s} & {:s} & & {:s} \\'
        date_templ: str = '%m/%d'
        lines: List[str] = [r'\toprule', header, r'\midrule']
        for i, (week_start, week_end) in enumerate(self.weeks):
            lines.append(
                template.format(
                    i + 1,
                    week_start.strftime(date_templ),
                    week_end.strftime(date_templ),
                    self._module_titles[i],
                    self._module_events[i]
                )
            )
        return '\n'.join(lines)

    @property
    def html(self) -> str:
        """
        Get the calendar as rendered HTML using Jinja2 template.

        Returns:
            str: HTML representation of the calendar.
        """
        # Set up Jinja2 environment
        template_dir: str = os.path.join(os.path.dirname(__file__), 'templates')
        env: Environment = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('calendar.html')

        # Prepare data for the template
        date_templ: str = '%m/%d'
        weeks_data: List[dict] = []
        for i, (week_start, week_end) in enumerate(self.weeks):
            weeks_data.append({
                'number': i + 1,
                'start_date': week_start.strftime(date_templ),
                'end_date': week_end.strftime(date_templ),
                'content': self._module_titles[i],
                'note': self._module_events[i]
            })

        # Render the template with the calendar data
        return template.render(weeks=weeks_data)


# CLI logic has been moved to cli.py for better separation of concerns.
