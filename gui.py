import datetime
import importlib
from functools import partial
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
import ipywidgets as widgets
from astral import LocationInfo
from IPython.display import display

import main
import locations as loc
import images as im
import colors

importlib.reload(main)
importlib.reload(loc)
importlib.reload(im)
importlib.reload(colors)


def plot_day(day_info):

    moon_size = 150
    sun_size = 200

    condition_colors = {
        "day": colors.DAY,
        "civil twilight": colors.CIVIL_TWILIGHT,
        "nautical twilight": colors.NAUTICAL_TWILIGHT,
        "astronomical twilight": colors.ASTRONOMICAL_TWILIGHT,
        "night": colors.NIGHT,
    }

    condition_alpha_multipliers = {
        "moon up": 1.00,
        "moon twilight": 0.50,
        "moon down": 0.00,
    }

    # 4. Plot the results using Matplotlib
    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.set_size_inches(12, 6)
    ax.set_facecolor(colors.NIGHT)
    ax.set_xlim(day_info["start"], day_info["end"])
    ax.set_ylim(-90, 90)

    # Draw patches to represent sun state
    for condition in day_info["conditions"]["sun"]:
        condition_start = condition["start"]
        condition_end = condition["end"]
        rect = patches.Rectangle(
            (condition_start, 0),  # Bottom-left corner
            condition_end - condition_start,  # width
            90,  # height
            facecolor=condition_colors[condition["state"]],
        )
        ax.add_patch(rect)
        if condition["state"] == "night":
            print(
                f"Night from {condition["start"].strftime("%I:%M %p")} to {condition["end"].strftime("%I:%M %p")}"
            )

    # Draw patches to represent moon state
    for condition in day_info["conditions"]["moon"]:
        condition_start = condition["start"]
        condition_end = condition["end"]
        alpha = (
            condition_alpha_multipliers[condition["state"]] * condition["brightness"]
        ) ** 0.5
        rect = patches.Rectangle(
            (condition_start, 0),  # Bottom-left corner
            condition_end - condition_start,  # width
            90,  # height
            facecolor=colors.MOON,
            alpha=alpha,
        )
        ax.add_patch(rect)
        if condition["state"] == "moon down":
            print(
                f"Moon is down from {condition["start"].strftime("%I:%M %p")} to {condition["end"].strftime("%I:%M %p")}"
            )

    plt.scatter(
        day_info["plot"]["times"],
        day_info["plot"]["sun"],
        s=sun_size,
        color=colors.SUN,
    )
    plt.scatter(
        day_info["plot"]["times"],
        day_info["plot"]["moon"],
        s=moon_size,
        color=colors.MOON_DARK,
    )
    plt.scatter(
        day_info["plot"]["times"],
        day_info["plot"]["moon"],
        s=day_info["plot"]["moon phases"],
        color=colors.MOON,
    )

    # Add a horizontal line at 0 degrees to represent the horizon
    plt.axhline(0, color="white", linestyle="-", linewidth=1)
    plt.axhline(-6, color="white", linestyle="--", linewidth=1)
    plt.axhline(-12, color="white", linestyle="--", linewidth=1)
    plt.axhline(-18, color="white", linestyle="--", linewidth=1)

    # Formatting the plot
    plt.title(
        f"Sun and Moon Elevation for the night of {day_info["day"].strftime('%Y-%m-%d')}"
    )
    plt.xlabel("Time of Day")
    plt.ylabel("Elevation (Degrees)")
    plt.grid(True, linestyle=":")

    # Improve x-axis date formatting

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H"))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    # plt.gcf().autofmt_xdate() # Auto-rotates dates for readability

    plt.show()

    return True


def create_stargazing_gui():
    """
    Creates and displays an ipywidgets GUI for stargazing data with improved layout
    and custom slider readouts.
    """

    # Helper function to format minutes into hours and minutes
    def format_duration(total_minutes):
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        hours = total_minutes // 60
        if hours > 1:
            hr_units = "hrs"
        else:
            hr_units = "hr"
        minutes = total_minutes % 60
        if minutes == 0:
            return f"{hours}{hr_units}"
        return f"{hours}{hr_units}, {minutes}min"

    # Helper function to format the float time range into HH:MM
    def format_time_range(time_range):
        start_float, end_float = time_range

        base_time = datetime.datetime.min
        start_time = base_time + datetime.timedelta(hours=start_float)
        end_time = base_time + datetime.timedelta(hours=end_float)

        return f"{start_time.strftime("%I:%M %p")} - {end_time.strftime("%I:%M %p")}"

    # Section 1: Inputs and "Go" button
    locations = loc.get_locations()
    location_dropdown = widgets.Dropdown(
        options=locations.keys(),
        description="Location:",
        style={"description_width": "initial"},
        layout={"width": "max-content"},  # Adjust width to content
    )

    current_datetime = datetime.datetime.now()
    calendar_year = widgets.BoundedIntText(
        value=current_datetime.year,
        min=2000,
        max=2100,
        step=1,
        description="Year:",
        disabled=False,
    )

    # --- Stargazing Minimum Length Slider with Custom Readout ---
    stargazing_slider = widgets.IntSlider(
        value=60,
        min=15,
        max=360,
        step=15,
        description="Stargazing Minimum Length:",
        readout=False,  # Hide the default float readout
        style={"description_width": "220px"},
        layout={"width": "500px"},
    )
    duration_label = widgets.Label(value=format_duration(stargazing_slider.value))

    def on_duration_change(change):
        duration_label.value = format_duration(change.new)
        update_warning()

    stargazing_slider.observe(on_duration_change, names="value")

    duration_box = widgets.HBox([stargazing_slider, duration_label])

    # --- Stargazing Allowable Times Slider with Custom Readout ---
    stargazing_range_slider = widgets.FloatRangeSlider(
        value=[16, 26],  # 4pm to 2am
        min=12,
        max=36,
        step=0.25,  # 15min step
        description="Stargazing Allowable Times:",
        readout=False,  # Hide the default float readout
        style={"description_width": "220px"},
        layout={"width": "500px"},
    )
    time_range_label = widgets.Label(
        value=format_time_range(stargazing_range_slider.value)
    )

    def on_time_range_change(change):
        time_range_label.value = format_time_range(change.new)
        update_warning()

    stargazing_range_slider.observe(on_time_range_change, names="value")

    time_range_box = widgets.HBox([stargazing_range_slider, time_range_label])

    duration_warning = widgets.Label(
        value="",
        style={"text_color": "red"},
    )

    def update_warning():
        stargazing_duration = stargazing_slider.value
        start_float, end_float = stargazing_range_slider.value
        if (end_float - start_float) < (stargazing_duration / 60):
            duration_warning.value = (
                "WARNING: Given time range is too short for requested duration."
            )
            duration_warning_state = True
        else:
            duration_warning.value = ""
            duration_warning_state = False

        return duration_warning_state

    # --- Go Button ---
    go_button = widgets.Button(description="Go", layout={"width": "100px"})

    # --- Advanced Settings ---
    timestep_slider = widgets.IntSlider(
        value=3,
        min=1,
        max=60,
        step=1,
        description="Timestep (minutes):",
        style={"description_width": "initial"},
    )
    week_start_toggle = widgets.Dropdown(
        options=["Sunday", "Monday"],
        description="Week Starts On:",
        value="Sunday",
        style={"description_width": "initial"},
    )

    advanced_settings_box = widgets.VBox([timestep_slider, week_start_toggle])
    advanced_settings = widgets.Accordion(children=[advanced_settings_box])
    advanced_settings.set_title(0, "Advanced Settings")
    advanced_settings.selected_index = None

    inputs_box = widgets.VBox(
        [
            location_dropdown,
            calendar_year,
            duration_box,
            time_range_box,
            duration_warning,
            advanced_settings,
            go_button,
        ]
    )

    # Section 5: Debugging output
    output_widget = widgets.Output(
        layout={"border": "1px solid black", "margin_top": "10px"}
    )

    # Section 2, 3, 4: Placeholders and save buttons
    section2_results = widgets.Output()
    section3_interactive = widgets.Output()
    save_calendar_button = widgets.Button(
        description="Save Calendar",
        disabled=True,
    )

    save_graphic_button = widgets.Button(
        description="Save Fancy Graphic",
        disabled=True,
    )

    save_buttons_box = widgets.HBox([save_calendar_button, save_graphic_button])

    def save_simple_image(b):
        with output_widget:

            text_info = {
                "year": results["year"],
                "location": results["location"],
                "stargazing times": results["stargazing times"],
                "stargazing duration": results["stargazing duration"],
            }

            im.save_calendar_image(
                calendar_info=results["calendar info"],
                week_starts_on=results["week start"],
                text_info=text_info,
            )

    save_calendar_button.on_click(save_simple_image)

    def save_fancy_image(b):
        with output_widget:
            print("not implemented")

    save_graphic_button.on_click(save_fancy_image)

    results = {}

    # --- Interaction function for the calendar ---
    # This is the function handle that will be passed to the calendar.
    # When a day button is clicked, this function will run.
    def day_interaction_callback(
        day, b
    ):  # The button click passes the button instance `b` as a second arg
        with section3_interactive:
            section3_interactive.clear_output(wait=True)
            plot_day(results["year info"]["days"][day])

    # --- "Go" button callback ---
    def go_button_callback(b):
        save_calendar_button.disabled = True
        save_graphic_button.disabled = True

        section2_results.clear_output(wait=True)
        section3_interactive.clear_output()

        # Gather the inputs to year info
        L = locations[location_dropdown.value]
        location = LocationInfo(
            name=location_dropdown.value,
            region=L["region"],
            timezone=L["timezone"],
            latitude=L["latitude"],
            longitude=L["longitude"],
        )
        year = calendar_year.value
        timestep = timestep_slider.value
        week_start = week_start_toggle.value

        results["year"] = year
        results["timestep"] = timestep
        results["week start"] = week_start
        results["location"] = location

        with section2_results:
            year_info = main.get_year_info(location, year, timestep_minutes=timestep)

        results["year info"] = year_info

        calendar_info = {}
        duration = datetime.timedelta(minutes=stargazing_slider.value)
        times = stargazing_range_slider.value
        results["stargazing times"] = times
        results["stargazing duration"] = duration
        for day, day_info in year_info["days"].items():
            # Check if there's a good stargazing window
            stargazing_window = False
            for condition in day_info["conditions"]["sky"]:
                dark_start = condition["start"]
                dark_end = condition["end"]

                base_date = datetime.datetime.combine(
                    datetime.date.fromisoformat(day),
                    datetime.time(hour=0, minute=0),
                )
                range_start = base_date + datetime.timedelta(minutes=times[0] * 60)
                range_end = base_date + datetime.timedelta(minutes=times[1] * 60)

                true_start = max(dark_start, range_start)
                true_end = min(dark_end, range_end)

                stargazing_window = (true_end - true_start) >= duration

            calendar_info.update({day: stargazing_window})

        results["calendar info"] = calendar_info

        with section2_results:
            print("Creating GUI...")
            calendar_widget = create_calendar_view(
                interaction_function=day_interaction_callback,
                calendar_info=calendar_info,
                location_info=year_info["location"],
                year=year_info["year"],
                week_starts_on=week_start,  # Pass the selected value
            )
            print("Loading GUI...")
            section2_results.clear_output(wait=True)
            display(calendar_widget)

        save_calendar_button.disabled = False
        save_graphic_button.disabled = False

    go_button.on_click(go_button_callback)

    # --- Assemble the GUI ---
    main_gui = widgets.VBox(
        [
            widgets.HTML("<h2>Stargazing Planner</h2>"),
            inputs_box,
            widgets.HTML("<hr><h3>Results</h3>"),
            section2_results,
            widgets.HTML("<h3>Interactive Details</h3>"),
            section3_interactive,
            widgets.HTML("<hr>"),
            save_buttons_box,
            widgets.HTML("<hr>"),
            output_widget,
        ]
    )

    display(main_gui)


def create_calendar_view(
    interaction_function,
    calendar_info,
    location_info,
    year,
    week_starts_on="Sunday",
):
    """
    Creates a full year calendar view with interactive day buttons and cosmetic tweaks.

    Args:
        interaction_function (function): The callback function to call when a day is clicked.
        location_info (dict): A dictionary containing location information.
        year (int): The year for which to generate the calendar.
        week_starts_on (str): 'Sunday' or 'Monday', determines the first day of the week.

    Returns:
        ipywidgets.VBox: The top-level widget containing the calendar.
    """
    day_size = 24
    day_gap = 2
    main_container = widgets.VBox()
    year_label = widgets.Label(
        value=f"Calendar for {year}",
        style={"font_size": "20px", "font_weight": "bold"},
    )

    w = 7 * day_size + 8 * day_gap
    months_grid = widgets.GridBox(
        children=[],
        layout=widgets.Layout(
            grid_template_columns=f"{w}px {w}px {w}px",
            grid_template_rows="auto auto auto auto",
            grid_gap="10px 10px",  # Add a bit more vertical gap
        ),
    )

    month_widgets = []

    # Determine day headers and offset logic based on the start of the week
    if week_starts_on == "Sunday":
        day_headers = ["S", "M", "T", "W", "T", "F", "S"]
        # weekday() is 0=Mon, 6=Sun. For a Sunday start, a date on Sunday (6) needs 0 offset.
        start_day_offset = lambda d: (d.weekday() + 1) % 7
    else:  # Monday start
        day_headers = ["M", "T", "W", "T", "F", "S", "S"]
        start_day_offset = lambda d: d.weekday()

    s = day_size
    day_button_layout = widgets.Layout(
        width=f"{s}px",
        height=f"{s}px",
        padding="0px",
    )

    for month_num in range(1, 13):
        first_day_of_month = datetime.date(year, month_num, 1)
        month_name = first_day_of_month.strftime("%B")

        # Use HTML for better centering control
        month_label = widgets.HTML(
            value=f"<div style='text-align: center; font-weight: bold;'>{month_name}</div>"
        )

        s = day_size
        g = day_gap
        w = 7 * day_size + 8 * day_gap
        h = w
        days_grid = widgets.GridBox(
            children=[],
            layout=widgets.Layout(
                # Define fixed column widths and a small gap to reduce horizontal space
                grid_template_columns=f"{s}px {s}px {s}px {s}px {s}px {s}px {s}px",
                grid_template_rows=f"{s}px {s}px {s}px {s}px {s}px {s}px {s}px",
                grid_gap=f"{g}px",
                width=f"{w}px",
                height=f"{h}px",
            ),
        )

        day_items = []
        for header in day_headers:
            day_items.append(
                widgets.HTML(
                    value=f"<div style='text-align: center'>{header}</div>",
                    layout=widgets.Layout(
                        width=f"{s}px",
                        height=f"{s}px",
                        padding="0px",
                    ),
                )
            )

        # Add blank placeholders for days before the 1st of the month
        for _ in range(start_day_offset(first_day_of_month)):
            day_items.append(widgets.Label(value=""))

        # Generate buttons for each day
        current_day = first_day_of_month
        while current_day.month == month_num:
            day_button = widgets.Button(
                description=str(current_day.day),
                # style={"font_size":"12px"},
                layout=day_button_layout,
            )
            day_callback = partial(interaction_function, current_day.isoformat())
            day_button.on_click(day_callback)

            if calendar_info[current_day.isoformat()]:
                day_button.style.button_color = colors.ASTRONOMICAL_TWILIGHT
                day_button.style.text_color = colors.MOON
            else:
                day_button.style.button_color = "white"

            day_items.append(day_button)
            current_day += datetime.timedelta(days=1)

        days_grid.children = day_items

        # Center the compact grid of days within the month's VBox
        centering_box = widgets.HBox(
            [days_grid],
            layout=widgets.Layout(justify_content="center"),
        )
        month_box = widgets.VBox([month_label, centering_box])
        month_widgets.append(month_box)

    months_grid.children = month_widgets
    main_container.children = [year_label, months_grid]

    return main_container
