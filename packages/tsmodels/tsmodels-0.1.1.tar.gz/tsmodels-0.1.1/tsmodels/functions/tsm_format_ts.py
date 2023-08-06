
import matplotlib.dates as dates
from datetime import timedelta

def format_ts_ax(ax, start_date, end_date):
    """
    Nicely formats a time series axis.

    Parameters
    ----------
    ax : matplotlib.pyplot.axes
        The axes to format.
    start : datetime
        The start date of the plot.
    end : datetime
        The end date of the plot.
    """
    ax.grid(True)
    length = (end_date - start_date).days
    ext = timedelta(days=2)
    ax.set_xlim(left=start_date-ext, right=end_date+ext)
    if (length < 30):
        ax.xaxis.set_minor_locator(dates.DayLocator())
        ax.xaxis.set_major_locator(dates.DayLocator(interval=5))
    elif (length < 60):
        ax.xaxis.set_minor_locator(dates.WeekdayLocator())
        ax.xaxis.set_major_locator(dates.WeekdayLocator(interval=2))
    elif (length < 100):
        ax.xaxis.set_major_locator(dates.MonthLocator())
    elif (length < 300):
        ax.xaxis.set_minor_locator(dates.MonthLocator())
        ax.xaxis.set_major_locator(dates.MonthLocator(interval=2))
    elif (length < 700):
        ax.xaxis.set_minor_locator(dates.MonthLocator())
        ax.xaxis.set_major_locator(dates.MonthLocator(interval=4))
    else:
        ax.xaxis.set_minor_locator(dates.MonthLocator(interval=6))
        ax.xaxis.set_major_locator(dates.MonthLocator(interval=12))
    # think matplotlib have made mistake below
    # should be which="both" but which="minor"
    # instead works
    ax.xaxis.grid(which="minor")
    ax.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
    ax.get_figure().autofmt_xdate()