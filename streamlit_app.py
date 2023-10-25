"""
streamlit_app.py
----
Temporary streamlit dashboard for litterati project
See readme for details. 

"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import textwrap
import os

# 1. Setup

# data import
points_data_file = 'data/points_with_covariates_20231003.csv'
points_df = pd.read_csv(points_data_file)

comb_data_file = 'data/kbt_comb_weights_volumes_20230803.csv'
comb_map = pd.read_csv(
        comb_data_file, 
        usecols= ['object', 'material', 'volume', 'weight']
        )

full_df = points_df.merge(
        comb_map[['object', 'material', 'weight', 'volume']], 
        on=['object', 'material'], 
        how='left')

segments_df = pd.read_csv("data/segments_counts_oct18_2023_v2.csv")
segment_cols = {
    'segment_id': 'segment_id',
    'all_count': 'litter_count',
    'non_srl_count': 'count_nosrl',
    'food_count': 'count_food',
    'drink_count': 'count_drink',
    'wrapper_count': 'count_wrapper',
    'bottle_count': 'count_bottle',
    'can_count': 'count_can',
    'segment_distance': 'segment_length',
    'land_use': 'land_use',
    'Region': 'region',
    'imd_score': 'imd_score',
    #'imd_decile': 'imd_decile',
    'imd_quintile': 'imd_quintile',
    'urban_rural': 'urban_rural_desc',
}
segments_df = segments_df[segment_cols.keys()].rename(
        columns=segment_cols, errors='ignore')

# add a new count combining bottles and cans
segments_df['count_bottles_and_cans'] = (segments_df['count_bottle'] + 
                                         segments_df['count_can'])

## style prep
litterati_color = '#0179ff'

litterati_colors = [
    "#0179ff",   # Base Color (Blue)
    "#33a1ff",   # Lighter and More Saturated Shade (Light Blue)
    "#3394ff",   # Lighter Shade (Light Blue)
    "#0066ff",   # Slightly Saturated Shade (Medium Blue)
    "#1f8eff",   # Slightly Lighter Shade (Medium Blue)
    "#0060cc",   # Slightly Darker Shade (Medium Blue)
    "#0052b3",   # Darker Shade (Dark Blue)
    "#004699",   # Even Darker Shade (Dark Blue)
    "#0040cc",   # Even Darker and Slightly Saturated Shade (Dark Blue)
    "#0040a3",   # Even Darker and Less Saturated Shade (Dark Blue)
    "#b3e0ff",   # Very Light Shade (Very Light Blue)
    "#8ab3cc",   # Light Shade with Reduced Saturation (Light Grayish Blue)
    "#ffcc00",   # Yellow Shade
    "#cc7a00",   # Dark Yellow Shade
    "#a31700",   # Reddish Shade
    "#e64d00",   # Orange Shade
    "#ff99cc"    # Light Pink Shade
]

display_map = {
 'segment_id': 'Segment ID',
 'litter_count': 'Total Litter',
 'count_nosrl': 'Non Smoking Related Litter',
 'count_food': 'Food Litter',
 'count_drink': 'Drink Litter',
 'count_wrapper': 'Wrappers',
 'count_bottle': 'Bottles',
 'count_bottles_and_cans': 'Bottles and Cans',
 'count_can': 'Cans',
 'segment_length': 'Segment Length',
 'land_use': 'Land Use Type',
 'region': 'Region of England',
 'imd_score': 'IMD Score',
 'imd_decile': 'IMD Decile',
 'imd_quintile': 'IMD Quintile (int)',
 'imd_quintile_cat': 'IMD Quintile',
 'urban_rural': 'Urban vs Rural',
 'urban_rural_desc': 'Urban vs Rural description',
 'urban_rural_class': 'Urban vs Rural class',
}

## 2. App layout

st.title('KBT: Interactive Visualizations')
st.markdown('Draft. **Last updated: 2023 October 4**')
st.markdown('*Data and results are under review and subject to change*')
st.divider()

## 3. Visualization 

# select which dataframe to use
df = full_df

## 3.1 Donut Chart

st.header('Donut Chart')

def plot_donut_chart(selected_column, threshold):
    # Group the data by the selected column and calculate the counts
    column_counts = df[selected_column].value_counts()

    # Set a threshold (percentage of total)
    threshold_percentage = threshold

    # Calculate the total count of categories
    total_count = column_counts.sum()

    # Calculate the threshold count based on the percentage
    threshold_count = total_count * threshold_percentage / 100

    # Combine tiny categories into 'Other'
    other_categories = column_counts[column_counts < threshold_count].index
    other_count = column_counts[column_counts < threshold_count].sum()
    column_counts = column_counts[column_counts >= threshold_count]
    column_counts['other'] = column_counts.get('other', 0) + other_count 

    # Create a donut chart using Plotly
    fig = px.pie(column_counts, 
                 values=column_counts.values, 
                 names=column_counts.index,
                 hole=0.4,  
                 title=f'Breakdown of {selected_column.capitalize()}',
                 )

    # Update layout for better aesthetics and larger size
    fig.update_traces(
            # values to display
            textinfo='percent+label', 
            hovertemplate='<b>%{label}</b><br>Count: %{value}',

            # fonts
            insidetextfont=dict(size=18),
            outsidetextfont=dict(size=18),
            hoverlabel=dict(font=dict(size=18)),

            # other
            showlegend=False
            )
    fig.update_layout(width=800, height=800)

    # Show the plot
    # fig.show()
    st.plotly_chart(fig)

    # Display the categories included in "Other"
    #wrapped_text = textwrap.fill(', '.join(other_categories), width=60)
    #st.write(f"Threshold: {threshold_percentage}%")
    #st.write("Categories captured in 'Other'")
    #st.write(wrapped_text)

# Create a dropdown widget to select the column to plot
column_options = ['object', 'material', 'brand', 'object_category']
selected_column = st.selectbox('Select Column:', column_options)

# set the width of the selectbox
# st.markdown('<style>div[role="listbox"] .Select-arrow {display: none;}</style>', unsafe_allow_html=True)
# selected_column = st.selectbox('Select Column:', column_options, key='selectbox', format_func=lambda x: x)

# treshold and slider values for each column
slider_configurations = {
    'object': {'min_value': 0.0, 'max_value': 5.0, 'step': 0.2, 'value': 2.0},
    'material': {'min_value': 0.0, 'max_value': 3.0, 'step': 0.1, 'value': 0.0},
    'brand': {'min_value': 0.0, 'max_value': 3.0, 'step': 0.1, 'value': 1.2},
    'parent_company': {'min_value': 0.0, 'max_value': 3.0, 'step': 0.1, 'value': 1.2},
}

# Get the selected column configuration or use a default configuration
def get_slider_config(selected_column):
    return slider_configurations.get(
            selected_column, 
            # default values here:  
            {'min_value': 0.0, 'max_value': 3.0, 'step': 0.1, 'value': 0.0},
            )

slider_config = get_slider_config(selected_column)

# Create a slider widget for the threshold
threshold = st.slider('Threshold:', **slider_config)

plot_donut_chart(selected_column, threshold)

## 3.2 Sunburst Chart 1

# insert divider
st.divider()
st.header('Sunburst Chart')

def create_sunburst_plot(group1, group1_threshold, group2, group2_threshold):

    # Group the data by 'parent_company' and 'material' and calculate the counts
    sunburst_counts = df.groupby([group1, group2]).size().reset_index(name='count')

    # Calculate the threshold count for group1 and group2
    total_count = sunburst_counts['count'].sum()
    group1_threshold_count = total_count * (group1_threshold / 100)
    group2_threshold_count = total_count * (group2_threshold / 100)

    # Group into "Other" category if they occupy less than the threshold for group1 and group2
    sunburst_counts[group1] = np.where(
        sunburst_counts.groupby(group1)['count'].transform('sum') < group1_threshold_count,
        'other',
        sunburst_counts[group1]
    )

    sunburst_counts[group2] = np.where(
        sunburst_counts.groupby(group2)['count'].transform('sum') < group2_threshold_count,
        'other',
        sunburst_counts[group2]
    )

    # Create a sunburst plot using Plotly
    fig = px.sunburst(sunburst_counts,
                      path=[group1, group2],
                      values='count',
                      title=f'Sunburst of {group1.capitalize()} > {group2.capitalize()}',
                     )

    # Setting font size (optional)
    fig.update_layout(uniformtext=dict(
        minsize=18,   # set the font size 
        mode='hide'))   # if mode is 'hide', text will be hidden when the wedge is too small
    
    # Customize hover text and textinfo
    fig.update_traces(
            # values to display
            textinfo='label+percent entry',
            # texttemplate='%{label}<br>%{percent entry:,.0f}',
            hovertemplate='<b>%{label}</b><br>Count: %{value:,.0f}',

            # fonts
            hoverlabel=dict(font=dict(size=18)),
            insidetextfont=dict(size=18),
            outsidetextfont=dict(size=18),
            )

    # Setting 
    fig.update_layout(width=800, height=800)

    # Show the plot
    # fig.show()
    st.plotly_chart(fig)


var_options = ['parent_company', 'material', 'brand_category', 'object', 'brand', 'object_category']

# Create two equal-sized columns
col1, col2 = st.columns(2)

# Widgets for group 1 (left column)
with col1:
    group1 = st.selectbox('Inner Category:', var_options, index=1)
    # threshold_g1 = st.slider('Threshold (inner):', min_value=0, max_value=20, value=2)
    slider_config = get_slider_config(group1)
    threshold_g1 = st.slider('Threshold (inner):', **slider_config)

# Widgets for group 2 (right column)
with col2:
    group2 = st.selectbox('Outer Category:', var_options, index=5)
    slider_config = get_slider_config(group2)
    threshold_g2 = st.slider('Threshold (outer):', **slider_config)

# Check if group1 and group2 are the same, and raise a ValueError if they are
if group1 == group2:
    st.error("Inner and Outer Categories cannot be the same. Please make different selections.")
else:
    create_sunburst_plot(group1, threshold_g1, group2, threshold_g2)

## 3.4 Histogram of LPM 

# select which dataframe to use
df = segments_df

st.divider()
st.header('Litter Per Meter')

## Utilities
def compute_lpm(df, group_column, count_column):
    """Compute LPM for a groupby operation"""
    # Group by the specified column and calculate the sum of the count_column and segment_length
    grouped = df.groupby(group_column).agg({count_column: 'sum', 'segment_length': 'sum'})

    # Calculate LPM for each group
    grouped['LPM'] = grouped[count_column] / grouped['segment_length']

    # Reset the index to have a new DataFrame with the group_column as a regular column
    grouped.reset_index(inplace=True)

    return grouped

# plot LPM
def plot_lpm(lpmdf, group_column, count_column):
    
    # sort
    lpmdf = lpmdf.sort_values(by='LPM', ascending=True)
    
    # Create a bar chart
    title = f'LPM for "{display_map[count_column]}" by {display_map[group_column]}'
    fig = px.bar(
            lpmdf, 
            x='LPM', 
            y=group_column, 
            title=title,
            color_discrete_sequence=litterati_colors
            )

    # Customize the chart appearance
    fig.update_layout(
        width=800, height=800, 
        yaxis=dict(
            title=display_map[group_column], 
            title_font=dict(size=18),
            tickfont=dict(size=15)),
        xaxis=dict(
            title='LPM (Litter per Meter)', 
            title_font=dict(size=18),
            tickfont=dict(size=15)),

        # font of text inside the bars
        font=dict(size=14),
        )

    # update the chart title positioning
    # fig.update_layout(title={'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})

    fig.update_traces(
        texttemplate='%{x:.02f}',
        hovertemplate='<b>%{y}</b><br>LPM: %{x:.02f}',
        hoverlabel=dict(font=dict(size=16)),
    )

    return fig

# Create dropdown widgets for selecting group_column and count_column
group_col_options = ['region', 'urban_rural_desc', 'land_use', 'imd_quintile_cat']
group_column_selector = st.selectbox(
        'Group by', 
        [display_map[c] for c in group_col_options],
        index=0)

count_col_options = ['litter_count', 'count_nosrl', 'count_food', 'count_drink', 'count_wrapper', 'count_bottles_and_cans', 'count_bottle', 'count_can']
count_column_selector = st.selectbox(
        'Count column:',
        [display_map[c] for c in count_col_options],
        index=1)


# Create a function that updates the plot based on dropdown values
def update_plot(group_column, count_column):
    # Reverse lookup from the display_map to get the actual column names
    group_column = [k for k, v in display_map.items() if v == group_column][0]
    count_column = [k for k, v in display_map.items() if v == count_column][0]
    
    lpm_group_df = compute_lpm(df, group_column, count_column)
    fig = plot_lpm(lpm_group_df, group_column, count_column)

    st.plotly_chart(fig)

# Call the update_plot function with the initial selections
update_plot(group_column_selector, count_column_selector)

# Use interactive_output to link the function and the dropdowns
# output = interactive_output(update_plot, {'group_column': group_column_selector, 'count_column': count_column_selector})

# Display the dropdown widgets
#display(group_column_selector, count_column_selector, output)

# Manual usage - disabled
# group_column = 'region'
# count_column = 'count_nosrl'




## 3.X map viz test
# st.map(data=df, 
#        latitude='lat', 
#        longitude='lon', 
#        zoom=5,
#        )
# fig = px.density_mapbox(df, 
#                         lat='lat', lon='lon', 
#                         z = 'imd_score', radius=5,
#                         zoom=6,
#                         #color='brand', 
#                         hover_name='urban_rural_desc', 
#                         #mapbox_style='open-street-map',
#                         mapbox_style='stamen-terrain', 
#                         opacity=0.3,
#                         title='test',
#                         width=800, height=800,
# )

# fig.show()

# st.plotly_chart(fig)

