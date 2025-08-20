import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates


def plot_day(day_info):

    moon_size = 150
    sun_size = 200

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
            facecolor="#DDDDDD",
            alpha=alpha,
        )
        ax.add_patch(rect)

    plt.scatter(
        day_info["plot"]["times"],
        day_info["plot"]["sun"],
        s=sun_size,
        color="#FFDD40",
    )
    plt.scatter(
        day_info["plot"]["times"],
        day_info["plot"]["moon"],
        s=moon_size,
        color="#444444",
    )
    plt.scatter(
        day_info["plot"]["times"],
        day_info["plot"]["moon"],
        s=day_info["plot"]["moon phases"],
        color="#DDDDDD",
    )

    # Add a horizontal line at 0 degrees to represent the horizon
    plt.axhline(0, color="white", linestyle="-", linewidth=1, label="Horizon")
    plt.axhline(-6, color="white", linestyle="--", linewidth=1, label="Civil Dusk")
    plt.axhline(-12, color="white", linestyle="--", linewidth=1, label="Nautical Dusk")
    plt.axhline(
        -18, color="white", linestyle="--", linewidth=1, label="Astronomical Dusk"
    )

    # Formatting the plot
    plt.title(
        f"Sun and Moon Elevation for the night of {day_info["day"].strftime('%Y-%m-%d')} in {day_info["location"].name}"
    )
    plt.xlabel("Time of Day")
    plt.ylabel("Elevation (Degrees)")
    plt.grid(True, linestyle=":")
    plt.legend()

    # Improve x-axis date formatting

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H"))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    # plt.gcf().autofmt_xdate() # Auto-rotates dates for readability

    plt.show()

    return True
