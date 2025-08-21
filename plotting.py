import datetime

# import importlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates

# from IPython.display import display

# import main
# import locations as loc
# import images as im

# importlib.reload(main)
# importlib.reload(loc)
# importlib.reload(im)


def plot_month(year_info, month_num):

    # Get month info from year
    year = year_info["year"]
    first_day_of_month = datetime.date(year, month_num, 1)
    month_name = first_day_of_month.strftime("%B")

    month_info = {
        "month name": month_name,
        "month num": month_num,
        "conditions": {
            "sun": [],
            "moon": [],
            "sky": [],
        },
        "plot": {
            "times": [],
            "sun": [],
            "moon": [],
            "moon phases": [],
        },
    }

    num_days = 0
    current_day = first_day_of_month
    day_info = year_info["days"][current_day.isoformat()]
    month_info["start"] = day_info["start"]
    while current_day.month == month_num:
        day_info = year_info["days"][current_day.isoformat()]

        print(day_info["day"])

        for key in ["sun", "moon", "sky"]:
            month_info["conditions"][key].extend(day_info["conditions"][key])

        for key in ["times", "sun", "moon", "moon phases"]:
            month_info["plot"][key].extend(day_info["plot"][key])

        num_days += 1
        current_day += datetime.timedelta(days=1)
    month_info["end"] = day_info["end"]

    moon_size = 150
    sun_size = 200

    # Desired pixel dimensions
    print(num_days)
    width_px = 120 * num_days
    height_px = 120

    # Choose a DPI. A common value is 100 or 72, but you can choose any suitable value.
    # The higher the DPI, the smaller the physical size (in inches) for the same pixel dimensions.
    dpi_val = 300

    # Calculate figsize in inches
    figsize_width_in = width_px / dpi_val
    figsize_height_in = height_px / dpi_val

    condition_colors = {
        "day": "#9085C0",
        "civil twilight": "#656F89",
        "nautical twilight": "#363655",
        "astronomical twilight": "#181B35",
        "night": "#070614",
    }

    condition_alpha_multipliers = {
        "moon up": 1.00,
        "moon twilight": 0.50,
        "moon down": 0.00,
    }

    # 4. Plot the results using Matplotlib
    fig, ax = plt.subplots(nrows=1, ncols=1)
    # fig.set_facecolor("grey")
    fig.set_size_inches(12, 6)
    ax.set_facecolor("#0D1C2E")
    ax.set_xlim(month_info["start"], month_info["end"])
    ax.set_ylim(-90, 90)
    ax.set_axis_off()

    # Draw patches to represent sun state
    for condition in month_info["conditions"]["sun"]:
        condition_start = condition["start"]
        condition_end = condition["end"]
        rect = patches.Rectangle(
            (condition_start, 0),  # Bottom-left corner
            condition_end - condition_start,  # width
            90,  # height
            facecolor=condition_colors[condition["state"]],
        )
        ax.add_patch(rect)

    # Draw patches to represent moon state
    for condition in month_info["conditions"]["moon"]:
        condition_start = condition["start"]
        condition_end = condition["end"]
        alpha = (
            condition_alpha_multipliers[condition["state"]] * condition["brightness"]
        ) ** 0.5
        rect = patches.Rectangle(
            (condition_start, 0),  # Bottom-left corner
            condition_end - condition_start,  # width
            90,  # height
            facecolor="#DDDDDD",
            alpha=alpha,
        )
        ax.add_patch(rect)

    plt.scatter(
        month_info["plot"]["times"],
        month_info["plot"]["sun"],
        s=sun_size,
        color="#FFDD40",
    )
    plt.scatter(
        month_info["plot"]["times"],
        month_info["plot"]["moon"],
        s=moon_size,
        color="#444444",
    )
    plt.scatter(
        month_info["plot"]["times"],
        month_info["plot"]["moon"],
        s=month_info["plot"]["moon phases"],
        color="#DDDDDD",
    )

    # Add a horizontal line at 0 degrees to represent the horizon
    plt.axhline(0, color="white", linestyle="-", linewidth=1)
    # plt.axhline(-6, color="white", linestyle="--", linewidth=1)
    # plt.axhline(-12, color="white", linestyle="--", linewidth=1)
    # plt.axhline(-18, color="white", linestyle="--", linewidth=1)

    # Formatting the plot
    plt.title(f"Sun and Moon Elevation for {month_name} {year}")
    # plt.xlabel("Time of Day")
    # plt.ylabel("Elevation (Degrees)")
    # plt.grid(True, linestyle=":")

    # Improve x-axis date formatting

    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H"))
    # plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    # plt.gcf().autofmt_xdate() # Auto-rotates dates for readability

    plt.show()

    return True
