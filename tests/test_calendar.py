from datetime import date
import pytest
from acalendar.calendar import *


def test_find_weekday_same_week():
    test_cases = {
        (date(2018, 1, 5), MONDAY): date(2018, 1, 1),
        (date(2018, 1, 3), FRIDAY): date(2018, 1, 5),
        (date(2018, 1, 1), WEDNESDAY): date(2018, 1, 3),
        (date(2018, 1, 6), THURSDAY): date(2018, 1, 4),  # From weekend
        (date(2018, 1, 4), MONDAY): date(2018, 1, 1)     # Same week, earlier day
    }
    for param, expected in test_cases.items():
        assert find_weekday_same_week(*param) == expected


def test_find_weekday_next_week():
    test_cases = {
        (date(2018, 1, 5), MONDAY): date(2018, 1, 8),
        (date(2018, 1, 1), MONDAY): date(2018, 1, 8),
        (date(2018, 1, 7), WEDNESDAY): date(2018, 1, 10),
        (date(2018, 1, 6), FRIDAY): date(2018, 1, 12)
    }
    for param, expected in test_cases.items():
        assert find_weekday_next_week(*param) == expected


def test_weeks_of_period():
    test_cases = {
        # Start on Monday and end on Friday
        (date(2018, 1, 8), date(2018, 1, 19)): [
            (date(2018, 1, 8), date(2018, 1, 12)),
            (date(2018, 1, 15), date(2018, 1, 19))
        ],
        # Start on weekend and end on Friday
        (date(2018, 1, 6), date(2018, 1, 19)): [
            (date(2018, 1, 8), date(2018, 1, 12)),
            (date(2018, 1, 15), date(2018, 1, 19))
        ],
        # Start on business day and end on weekend
        (date(2018, 1, 10), date(2018, 1, 21)): [
            (date(2018, 1, 10), date(2018, 1, 12)),
            (date(2018, 1, 15), date(2018, 1, 19))
        ],
        # Start and end on business day
        (date(2018, 1, 10), date(2018, 1, 18)): [
            (date(2018, 1, 10), date(2018, 1, 12)),
            (date(2018, 1, 15), date(2018, 1, 18))
        ],
        # Single week
        (date(2018, 1, 8), date(2018, 1, 12)): [
            (date(2018, 1, 8), date(2018, 1, 12))
        ]
    }
    for param, expected in test_cases.items():
        assert weeks_of_period(*param) == expected


def test_course_term_basics():
    cal = CourseTerm(
        start_date="2024-01-08",
        end_date="2024-01-19",
        module_titles="01. Week 1 Content\n02. Week 2 Content",
        module_events="01. Event for Week 1\n02. Event for Week 2"
    )

    # Test basic properties
    assert len(cal.weeks) == 2
    assert cal.weeks[0] == (date(2024, 1, 8), date(2024, 1, 12))
    assert cal.weeks[1] == (date(2024, 1, 15), date(2024, 1, 19))

    # Test module titles
    assert cal.module_titles[0] == "Week 1 Content"
    assert cal.module_titles[1] == "Week 2 Content"

    # Test module events
    assert cal.module_events[0] == "Event for Week 1"
    assert cal.module_events[1] == "Event for Week 2"


def test_course_term_outputs():
    cal = CourseTerm(
        start_date="2024-01-08",
        end_date="2024-01-19",
        module_titles="01. Week 1 Content\n02. Week 2 Content",
        module_events="01. Event for Week 1\n02. Event for Week 2"
    )

    # Test CSV output
    csv_output = cal.csv
    assert '"Week","Dates","Content","Notes"' in csv_output
    assert '"1","01/08-01/12","Week 1 Content","Event for Week 1"' in csv_output
    assert '"2","01/15-01/19","Week 2 Content","Event for Week 2"' in csv_output

    # Test HTML output
    html_output = cal.html  # Call the method
    assert '<table' in html_output
    assert 'Week 1 Content' in html_output
    assert 'Week 2 Content' in html_output
    assert 'Event for Week 1' in html_output
    assert 'Event for Week 2' in html_output

    # Test LaTeX output
    tex_output = cal.tex  # Call the method
    assert r'\toprule' in tex_output
    assert r'\midrule' in tex_output
    assert 'Week 1 Content' in tex_output
    assert 'Week 2 Content' in tex_output
    assert 'Event for Week 1' in tex_output
    assert 'Event for Week 2' in tex_output


def test_course_term_input_validation():
    # Test invalid date format
    with pytest.raises(ValueError):
        CourseTerm(
            start_date="2024/01/08",  # Wrong format
            end_date="2024-01-19",
            module_titles="01. Week 1 Content\n02. Week 2 Content",
            module_events="01. Event for Week 1\n02. Event for Week 2"
        )

    # Test end date before start date
    with pytest.raises(ValueError):
        CourseTerm(
            start_date="2024-01-19",
            end_date="2024-01-08",  # Before start date
            module_titles="01. Week 1 Content\n02. Week 2 Content",
            module_events="01. Event for Week 1\n02. Event for Week 2"
        )

    # Test mismatched number of titles
    with pytest.raises(ValueError):
        CourseTerm(
            start_date="2024-01-08",
            end_date="2024-01-19",
            module_titles="01. Week 1 Content",
            module_events="01. Event for Week 1\n02. Event for Week 2"
        )

    # Test with mismatched number of events
    with pytest.raises(ValueError):
        CourseTerm(
            start_date="2024-01-08",
            end_date="2024-01-19",
            module_titles="01. Week 1 Content\n02. Week 2 Content",
            module_events="01. Event for Week 1"
        )

    # Test with more events than weeks (raises ValueError)
    with pytest.raises(ValueError):
        CourseTerm(
            start_date="2024-01-08",
            end_date="2024-01-19",
            module_titles="01. Week 1 Content\n02. Week 2 Content",
            module_events="01. Event for Week 1\n02. Event for Week 2\n03. Extra Event"
        )

