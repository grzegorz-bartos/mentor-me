import calendar
from datetime import date

from django import template

register = template.Library()


@register.inclusion_tag("calendar_widget.html")
def render_calendar(year=None, month=None, tutor_availabilities=None):
    """
    Generates calendar data for a specific month.

    Returns context with:
    - month_name: "December 2025"
    - weeks: [[day1, day2, ...], [day8, day9, ...]]
    - available_days: set of day_of_week values (0-6) from availabilities
    """
    if not year or not month:
        today = date.today()
        year, month = today.year, today.month

    # Default to 24/7 availability - all days are available
    # (If specific availabilities exist, use those instead)
    if tutor_availabilities and tutor_availabilities.exists():
        available_days = set(tutor_availabilities.values_list("day_of_week", flat=True))
    else:
        # All days are available by default (0-6 = Mon-Sun)
        available_days = {0, 1, 2, 3, 4, 5, 6}

    # Build calendar weeks (Sunday start)
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(year, month)

    return {
        "year": year,
        "month": month,
        "month_name": f"{calendar.month_name[month]} {year}",
        "weeks": month_days,
        "available_days": available_days,
        "today": date.today(),
        "current_month": month,
    }
