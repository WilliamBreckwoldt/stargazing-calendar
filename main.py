import importlib
import datetime

from astral import LocationInfo

import astronomy
import gui

importlib.reload(astronomy)
importlib.reload(gui)

DEFAULT_TIMESTEP = 3  # minutes


def plot_day(
    location: LocationInfo,
    day: datetime.date,
    timestep_minutes: int = DEFAULT_TIMESTEP,
):

    day_info = astronomy.get_day_info(
        location=location,
        day=day,
        timestep_minutes=timestep_minutes,
    )

    gui.plot_day(day_info)


def get_year_info(
    location: LocationInfo,
    year: int,
    timestep_minutes: int = DEFAULT_TIMESTEP,
):
    start_day = datetime.date(year, 1, 1)
    end_day = datetime.date(year, 12, 31)

    day = start_day - datetime.timedelta(days=1)
    year_info = {}
    while day < end_day:
        day = day + datetime.timedelta(days=1)
        print(day)
        year_info.update(
            {
                day: astronomy.get_day_info(
                    location=location,
                    day=day,
                    timestep_minutes=timestep_minutes,
                )
            }
        )

    return year_info
