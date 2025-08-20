import math

import datetime

import pytz
from astral import LocationInfo, sun, moon


def get_day_info(
    location: LocationInfo,
    day: datetime.date,
    timestep_minutes: int,
):
    """
    Calculates and plots the sun's elevation throughout a given day for a specific location.

    Args:
        location_name: Name of the location.
        region: Region or country.
        tz: Timezone name.
        lat: Latitude.
        lon: Longitude.
        day: The date for which to plot the elevation.
        timestep_minutes: The interval in minutes for the calculation.
    """
    moon_size = 150

    moon_darkness_threshold = -6  # elevation in degrees

    tz = pytz.timezone(location.timezone)

    # 2. Set up the time iteration
    # Start at midnight on the given day in the location's timezone
    start_day = day
    start_time = tz.localize(datetime.datetime.combine(start_day, datetime.time(12, 0)))
    utc_start_time = start_time.astimezone(datetime.timezone.utc)

    # End 24 hours later
    end_day = start_day + datetime.timedelta(days=1)
    end_time = tz.localize(datetime.datetime.combine(end_day, datetime.time(12, 0)))
    utc_end_time = end_time.astimezone(datetime.timezone.utc)

    # end_time = start_time + datetime.timedelta(days=1)
    # Define the interval
    timestep = datetime.timedelta(minutes=timestep_minutes)

    # Lists to store data for plotting
    times = []
    sun_elevations = []
    moon_elevations = []
    moon_phases = []

    current_sun_condition = {
        "state": None,
        "start": None,
        "end": None,
    }
    sun_conditions = []

    current_moon_condition = {
        "state": None,
        "start": None,
        "end": None,
        "brightness": None,
    }
    moon_conditions = []

    current_sky_condition = {
        "state": None,
        "start": None,
        "end": None,
    }
    sky_conditions = []

    # 3. Iterate through the day and calculate elevation
    current_time = utc_start_time
    while current_time <= utc_end_time:

        # Find sun and moon info
        sun_elev = sun.elevation(location.observer, current_time)
        moon_elev = moon.elevation(location.observer, current_time)
        moon_phase = moon.phase(current_time)

        # Find local time
        local_time = current_time.astimezone(pytz.timezone(location.timezone)).replace(
            tzinfo=None
        )

        # Processing of the info we've found
        moon_brightness = (
            -math.cos(moon_phase * math.pi / 14) / 2 + 0.5
        )  # TODO: calculate brightness better

        # Store the results
        times.append(local_time)
        sun_elevations.append(sun_elev)
        moon_elevations.append(moon_elev)
        moon_phases.append(moon_brightness * moon_size)

        # Track conditions to color code the results

        # Track sun state
        sun_state = ""
        if sun_elev >= 0:  # Day
            sun_state = "day"
        elif sun_elev >= -6:  # Civil Twilight
            sun_state = "civil twilight"
        elif sun_elev >= -12:  # Nautical Twilight
            sun_state = "nautical twilight"
        elif sun_elev >= -18:  # Astronomical Twilight
            sun_state = "astronomical twilight"
        else:  # Night
            sun_state = "night"

        if current_sun_condition["state"] is None:  # State not yet assigned
            current_sun_condition["state"] = sun_state
            current_sun_condition["start"] = local_time

        elif (
            current_sun_condition["state"] != sun_state
        ):  # State change since last data point
            # End of old condition
            current_sun_condition["end"] = local_time
            sun_conditions.append(current_sun_condition.copy())
            # Start of new condition
            current_sun_condition["state"] = sun_state
            current_sun_condition["start"] = local_time

        # Track moon state
        moon_state = ""
        if moon_elev >= 0:  # Day
            moon_state = "moon up"
        elif moon_elev >= moon_darkness_threshold:  # Moon Twilight
            moon_state = "moon twilight"
        else:  # Night
            moon_state = "moon down"

        if current_moon_condition["state"] is None:  # State not yet assigned
            current_moon_condition["state"] = moon_state
            current_moon_condition["start"] = local_time

        elif (
            current_moon_condition["state"] != moon_state
        ):  # State change since last data point
            # End of old condition
            current_moon_condition["end"] = local_time
            current_moon_condition["brightness"] = moon_brightness
            moon_conditions.append(current_moon_condition.copy())
            # Start of new condition
            current_moon_condition["state"] = moon_state
            current_moon_condition["start"] = local_time

        sky_state = ""
        if (sun_state == "night") and (moon_state == "moon down"):
            sky_state = "dark"
        else:
            sky_state = "not dark"

        if current_sky_condition["state"] is None:  # State not yet assigned
            current_sky_condition["state"] = sky_state
            current_sky_condition["start"] = local_time

        elif (
            current_sky_condition["state"] != sky_state
        ):  # State change since last data point
            # End of old condition
            current_sky_condition["end"] = local_time
            current_sky_condition["duration"] = (
                current_sky_condition["end"] - current_sky_condition["start"]
            )
            sky_conditions.append(current_sky_condition.copy())
            # Start of new condition
            current_sky_condition["state"] = sky_state
            current_sky_condition["start"] = local_time

        # Move to the next timestep
        current_time += timestep

    # Add final moon and sun conditions
    current_sun_condition["end"] = local_time
    sun_conditions.append(current_sun_condition.copy())
    current_moon_condition["end"] = local_time
    current_moon_condition["brightness"] = moon_brightness
    moon_conditions.append(current_moon_condition.copy())
    current_sky_condition["end"] = local_time
    current_sky_condition["duration"] = (
        current_sky_condition["end"] - current_sky_condition["start"]
    )
    sky_conditions.append(current_sky_condition.copy())
    sky_conditions = [
        condition for condition in sky_conditions if condition["state"] == "dark"
    ]

    day_info = {
        "location": location,
        "day": day,
        "start": start_time.replace(tzinfo=None),
        "end": end_time.replace(tzinfo=None),
        "conditions": {
            "sun": sun_conditions,
            "moon": moon_conditions,
            "sky": sky_conditions,
        },
        "plot": {
            "times": times,
            "sun": sun_elevations,
            "moon": moon_elevations,
            "moon phases": moon_phases,
        },
    }

    return day_info
