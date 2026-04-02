import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
from mendeleev import element
import numpy as np

#18 columns and 10 rows instead of  9 to account for the gap
columns = 18
rows = 10
# mapping mendeleev attributes to the common property names
TRENDS = {
    "Electronegativity": "en_pauling",
    "Atomic Mass": "mass",
    "Atomic Radius": "atomic_radius",
    "Ionization Energy": "ionenergies",
    "Melting Point": "melting_point",
    "Boiling Point": "boiling_point"
}
# Define a custom White to Red colorscale
# 0 is the lowest value, 1 is the highest
blue_to_red = [[0, 'rgb(173, 216, 230)'], [1, 'rgb(255, 0, 0)']]

#initialize an 18 by 10 grid
def initialize_grid(initial_value):
    return [[initial_value for _ in range(columns)] for _ in range(rows)]
#this method maps element to coordinates
def get_periodic_table_grid(columns, rows):
    #create empty grid of 18 colums per row
    grid = initialize_grid("")
    hover_text = initialize_grid("") # New hover grid
    #loop through each element int he library and populate the grid
    for i in range(1, 119):
        el = element(i)
        # Create a display string: "1\nH" (Atomic Number on top of Symbol)
        display_label = f"{el.atomic_number}<br><b>{el.symbol}</b>"

        # Create a detailed hover string
        hover_label = (
            f"Atomic Number: {el.atomic_number}<br>"
            f"Element: {el.name}<br>"
            f"Atomic Mass: {round(el.mass, 2)}")
        # 1. Start with "fallback" coordinates to prevent errors
        r, c = 0, 0

        # 2. Only do math if the group exists (Elements 1-56, 72-88, 104-118)
        if el.group is not None:
            r = el.period - 1
            # Use .group_id to get the 1-18 number
            c = el.group_id - 1

        # 3. Use your manual overrides for the "f-block" (Lanthanides/Actinides)
        if 57 <= i <= 71:
            r, c = 7, (i - 57) + 2
        elif 89 <= i <= 103:
            r, c = 8, (i - 89) + 2

        # 4. Place the symbol in the grid
        grid[r][c] = el.symbol
        hover_text[r][c] = hover_label

    return grid, hover_text
#populates the grid for the desired attribute/trend
def get_value_grid(attribute):
    #grid initalized with 0.0
    v_grid = initialize_grid(-1.0)
    #populate grid with actual values for selected attribute
    for i in range(1, 119):
        el = element(i)

        # Pull the specific value (e.g., el.en_pauling)
        val = getattr(el, attribute)
        # Special handling for Ionization Energy (it returns a list, we want the 1st one)
        if attribute == "ionenergies" and val is not None:
            # just want 1st ionization energy, key of 1
            if 1 in val:
                val = val.get(1)

        # Clean up missing data (None) so the map doesn't crash
        if val is None or not isinstance(val, (int, float)):
            if getattr(el, "mass")>0:
                val = 0.0
            else:
                val = -1.0

        # Standard coordinate logic
        r, c = 0, 0
        if el.group_id:
            r, c = el.period - 1, el.group_id - 1
        if 57 <= i <= 71:
            r, c = 7, (i - 57) + 2
        elif 89 <= i <= 103:
            r, c = 8, (i - 89) + 2
        # st.sidebar.info(val)
        v_grid[r][c] = float(val)
    return v_grid
#create the side bar for trend selection
st.sidebar.title("Trend Settings")
selected_trend_label = st.sidebar.selectbox("Select a priodic table trend: ", list(TRENDS.keys()))
selected_attribute = TRENDS[selected_trend_label]
#create the plot
current_values = get_value_grid(selected_attribute)
max_val = np.max(current_values)
symbol_grid, hover_grid = get_periodic_table_grid(columns, rows)
#0 to mark empty grids 1 for element
filled_in_grid = [[1 if cell != "" else 0 for cell in rows] for rows in symbol_grid]

# different color scale for each attribute to reduce confusion
COLOR_MAP = {
    "Electronegativity": "Blues",
    "Atomic Mass": "Greens",
    "Atomic Radius": "Purples",
    "Ionization Energy": "YlOrRd", # Yellow-Orange-Red
    "Melting Point": "Viridis",
    "Boiling Point": "Magma"
}
selected_colorscale = COLOR_MAP.get(selected_trend_label, "Reds") # Default to Reds
#custom scale to differentiate grids where there's no element
custom_scale = [
    [0.0, 'rgb(255, 255, 255)'],      # -1 (Bottom of scale) is White
    [0.1, 'rgb(255, 255, 255)'],      # 0 is still White
    [1.0, 'rgb(255, 0, 0)']           # Max value is Red
]
# Build the plot
fig = ff.create_annotated_heatmap(
    z=current_values[::-1],
    annotation_text=symbol_grid[::-1],
    text=hover_grid[::-1],
    hoverinfo='text',
    colorscale=selected_colorscale,
    zmin=-1,
    zmax=max_val,
    showscale=True
)

# Style the outlines and gaps
# fig.update_traces(xgap=3, ygap=3, marker=dict(line=dict(width=1, color='black')))

fig.update_layout(
    title=f"Periodic Table: {selected_trend_label} Heatmap",
    # light gray bg
    plot_bgcolor='rgb(240, 240, 240)',
    # white bg outside the chart
    paper_bgcolor='rgb(255, 255, 255)', # Example: White
    xaxis=dict(zeroline=False, showgrid=False, side='top'),
    yaxis=dict(zeroline=False, showgrid=False),
    width=1000, height=600
)

st.plotly_chart(fig)