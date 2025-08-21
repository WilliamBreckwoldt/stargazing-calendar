import json
import os
import shutil
import importlib
import ipywidgets as widgets
from IPython.display import display
import pytz

import constants as c

importlib.reload(c)


def get_locations():
    """
    Loads location data from a JSON file.

    This function first attempts to load 'my_locations.loc.json' from the 'data'
    folder. If this file doesn't exist, it copies 'default_locations.loc.json'
    to 'my_locations.loc.json' and then loads the new file.

    Returns:
        dict: A dictionary containing the location data.
    """
    # Create the data directory if it doesn't exist.
    if not os.path.exists("data"):
        os.makedirs("data")

    default_locations_path = os.path.join("data", "default_locations.loc.json")
    my_locations_path = os.path.join("data", "my_locations.loc.json")

    try:
        with open(my_locations_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        shutil.copyfile(default_locations_path, my_locations_path)
        with open(my_locations_path, "r") as f:
            return json.load(f)


def save_locations(locations):
    """Helper function to save the locations dictionary to the JSON file."""
    with open(os.path.join("data", "my_locations.loc.json"), "w") as f:
        json.dump(locations, f, indent=2)


def create_location_gui():
    """Creates and displays the ipywidgets GUI for managing locations."""

    locations = get_locations()
    output = widgets.Output()

    # --- ADD LOCATION WIDGETS ---
    add_name = widgets.Text(description="Name:")
    add_region = widgets.Text(description="Region:")
    add_latitude = widgets.FloatText(description="Latitude:", min=-90, max=90)
    add_longitude = widgets.FloatText(description="Longitude:", min=-180, max=180)

    # Prepare and sort timezone options
    timezones = sorted(
        pytz.all_timezones, key=lambda x: not x.startswith(c.DEFAULT_TIMEZONE_REGION)
    )
    add_timezone = widgets.Dropdown(options=timezones, description="Timezone:")
    add_button = widgets.Button(description="Add Location")

    def clear_add_inputs():
        add_name.value = ""
        add_region.value = ""
        add_latitude.value = 0
        add_longitude.value = 0
        add_timezone.value = timezones[0]

    def on_add_button_clicked(b):
        with output:
            output.clear_output()
            name = add_name.value
            if name and name not in locations:
                locations[name] = {
                    "region": add_region.value,
                    "latitude": add_latitude.value,
                    "longitude": add_longitude.value,
                    "timezone": add_timezone.value,
                }
                save_locations(locations)
                edit_name.options = list(locations.keys())
                clear_add_inputs()
                print(f"Added location: {name}")
            elif name in locations:
                print(f"Error: Location '{name}' already exists.")
            else:
                print("Error: Name cannot be empty.")

    add_button.on_click(on_add_button_clicked)
    add_section = widgets.VBox(
        [add_name, add_region, add_latitude, add_longitude, add_timezone, add_button]
    )

    # --- EDIT/REMOVE LOCATION WIDGETS ---
    edit_name = widgets.Dropdown(options=list(locations.keys()), description="Name:")
    edit_region = widgets.Text(description="Region:")
    edit_latitude = widgets.FloatText(description="Latitude:", min=-90, max=90)
    edit_longitude = widgets.FloatText(description="Longitude:", min=-180, max=180)
    edit_timezone = widgets.Dropdown(options=timezones, description="Timezone:")
    edit_save_button = widgets.Button(description="Save Changes")
    edit_delete_button = widgets.Button(description="Delete Location")

    def clear_edit_inputs():
        # Set dropdown to first item if list is not empty, otherwise set to None
        if edit_name.options:
            edit_name.value = edit_name.options[0]
        else:
            edit_name.value = None
        edit_region.value = ""
        edit_latitude.value = 0
        edit_longitude.value = 0
        edit_timezone.value = timezones[0]

    def populate_edit_fields(change):
        # *** THE FIX IS HERE ***
        # Use key access ['new'] which works for both manual calls and observe events.
        location_name = change["new"]
        if location_name:
            location = locations.get(location_name, {})
            edit_region.value = location.get("region", "")
            edit_latitude.value = location.get("latitude", 0)
            edit_longitude.value = location.get("longitude", 0)
            edit_timezone.value = location.get("timezone", timezones[0])
        else:
            # Clear fields if no location is selected
            edit_region.value = ""
            edit_latitude.value = 0
            edit_longitude.value = 0

    edit_name.observe(populate_edit_fields, names="value")

    def on_edit_save_button_clicked(b):
        with output:
            output.clear_output()
            name = edit_name.value
            if name:
                locations[name] = {
                    "region": edit_region.value,
                    "latitude": edit_latitude.value,
                    "longitude": edit_longitude.value,
                    "timezone": edit_timezone.value,
                }
                save_locations(locations)
                print(f"Updated location: {name}")
            else:
                print("Error: No location selected.")

    def on_edit_delete_button_clicked(b):
        with output:
            output.clear_output()
            name = edit_name.value
            if name:
                if name in locations:
                    del locations[name]
                    save_locations(locations)
                    # Update dropdown options and reset its value
                    edit_name.options = list(locations.keys())
                    # The observe function will automatically clear and populate the fields
                    print(f"Deleted location: {name}")
            else:
                print("Error: No location selected.")

    edit_save_button.on_click(on_edit_save_button_clicked)
    edit_delete_button.on_click(on_edit_delete_button_clicked)
    edit_section = widgets.VBox(
        [
            edit_name,
            edit_region,
            edit_latitude,
            edit_longitude,
            edit_timezone,
            widgets.HBox([edit_save_button, edit_delete_button]),
        ]
    )

    # --- TAB WIDGET ---
    tab = widgets.Tab()
    tab.children = [add_section, edit_section]
    tab.set_title(0, "Add Location")
    tab.set_title(1, "Edit/Remove Location")

    # Trigger population of edit fields for the initial value
    if edit_name.value:
        populate_edit_fields({"new": edit_name.value})

    display(tab, output)
