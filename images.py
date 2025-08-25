import os
import textwrap
import datetime
import importlib
from matplotlib import pyplot as plt
from matplotlib import patches
from pathvalidate import sanitize_filename

import colors

importlib.reload(colors)


def save_calendar_image(
    calendar_info,
    text_info,
    week_starts_on,
):
    """
    Generates a visual calendar for a given year and saves it as an image.

    Days are drawn as squares and are color-coded based on the calendar_info dictionary.

    Args:
        calendar_info (dict): A dictionary with date ISO strings ('YYYY-MM-DD')
                              as keys and a boolean value. True highlights the day.
        year (int): The year for which to generate the calendar.
        details_text (str): A paragraph of text to display at the bottom of the calendar.
        filename (str): The name of the image file to save.
        week_starts_on (str): 'Sunday' or 'Monday'. Determines the first day of the week.
    """

    year = text_info["year"]
    duration = timedelta_to_str(text_info["stargazing duration"])
    start_time = hours_to_str(text_info["stargazing times"][0])
    end_time = hours_to_str(text_info["stargazing times"][1])
    location = text_info["location"]
    details_text = f"Highlighted days have {duration} of continuous night sky with no moon between the hours of {start_time} and {end_time}. Location {location.name} is at {location.latitude}, {location.longitude}."
    filename = sanitize_filename(f"{year}_{location.name}_stargazing_calendar.png")

    # --- Directory Setup ---
    if not os.path.exists("images"):
        os.makedirs("images")
        print("Created 'images' directory.")

    # --- Matplotlib Figure Setup ---
    # Standard 8.5x11 figure size
    fig, axes = plt.subplots(4, 3, figsize=(8.5, 11))
    fig.suptitle(f"{location.name} Stargazing Calendar {year}", fontsize=20, y=0.97)

    axes = axes.ravel()

    # --- Day Headers and Offset Logic ---
    if week_starts_on == "Sunday":
        day_headers = ["S", "M", "T", "W", "T", "F", "S"]
        start_day_offset = lambda d: (d.weekday() + 1) % 7
    else:  # Monday start
        day_headers = ["M", "T", "W", "T", "F", "S", "S"]
        start_day_offset = lambda d: d.weekday()

    # --- Iterate Through Each Month to Draw Calendar ---
    for month_num in range(1, 13):
        ax = axes[month_num - 1]
        first_day_of_month = datetime.date(year, month_num, 1)
        month_name = first_day_of_month.strftime("%B")

        # --- Month Formatting ---
        ax.set_title(month_name, fontsize=14, pad=10)

        ax.set_xlim(0, 7)
        ax.set_ylim(0, 7)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal", adjustable="box")
        for spine in ax.spines.values():
            spine.set_visible(False)

        # --- Draw Day of Week Headers ---
        for i, header in enumerate(day_headers):
            ax.text(
                i + 0.5,
                6.5,
                header,
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
            )

        # --- Draw Days ---
        current_day = first_day_of_month
        day_offset = start_day_offset(first_day_of_month)

        while current_day.month == month_num:
            day_col = (current_day.day + day_offset - 1) % 7
            week_row = (current_day.day + day_offset - 1) // 7
            y_base = 5 - week_row

            is_favorable = calendar_info.get(current_day.isoformat(), False)
            face_color = colors.ASTRONOMICAL_TWILIGHT if is_favorable else "#FFFFFF"
            font_color = colors.MOON if is_favorable else "black"
            font_weight = "bold" if is_favorable else "normal"

            rect = patches.Rectangle(
                (day_col, y_base), width=1, height=1, facecolor=face_color
            )
            ax.add_patch(rect)

            ax.text(
                day_col + 0.5,
                y_base + 0.5,
                str(current_day.day),
                ha="center",
                va="center",
                fontsize=8,
                color=font_color,
                fontweight=font_weight,
            )

            current_day += datetime.timedelta(days=1)

    # --- Final Touches and Saving ---
    # Adjust layout to prevent overlap and make space at the bottom
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])

    # Add the details text at the bottom of the figure if it exists
    if details_text:
        # Automatically wrap the text to fit the figure width
        wrapped_text = textwrap.fill(details_text, width=120)
        fig.text(
            0.5,  # Centered horizontally
            0.04,  # Positioned near the bottom of the figure
            wrapped_text,
            ha="center",
            va="top",
            fontsize=6,
            color=colors.MOON_DARK,  # Dark gray for readability
        )

    filepath = os.path.join("images", filename)
    plt.savefig(filepath, dpi=300)  # Increased dpi for better quality
    plt.close(fig)
    print(f"Calendar image saved to '{filepath}'")


def timedelta_to_str(td: datetime.timedelta):
    # Get total seconds
    total_seconds = int(td.total_seconds())

    # Calculate hours and minutes
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60

    # Format the output
    formatted_time = f"{hours}h {minutes}m"

    return formatted_time


def hours_to_str(hrs):
    # Get total seconds
    td = datetime.timedelta(minutes=hrs * 60)

    date = datetime.datetime.min + td

    return date.strftime("%H:%M %p")
