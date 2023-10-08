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

## 2. App layout

st.title('KBT: Interactive Visualizations')
st.markdown('Draft. **Last updated: 2023 October 4**')
st.markdown('*Data and results are under review and subject to change*')
st.divider()

## 3. Visualization 

df = full_df
# st.write(full_df.head(3).T)

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
            textinfo='percent+label', 
            insidetextfont=dict(color='white'),
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

# Create a slider widget for the threshold
threshold = st.slider(
        'Threshold:', 
        min_value=0, max_value=20, 
        step=1, 
        value=2
        )

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
        minsize=15,   # set the font size 
        mode='hide'))   # if mode is 'hide', text will be hidden when the wedge is too small
    
    # Customize hover text and textinfo
    fig.update_traces(
            #textinfo='label+value+percent parent',
            textinfo='label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}'
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
    threshold_g1 = st.slider('Threshold (inner):', min_value=0, max_value=20, value=2)

# Widgets for group 2 (right column)
with col2:
    group2 = st.selectbox('Outer Category:', var_options, index=5)
    threshold_g2 = st.slider('Threshold (outer):', min_value=0, max_value=20, value=2)

# Check if group1 and group2 are the same, and raise a ValueError if they are
if group1 == group2:
    st.error("Inner and Outer Categories cannot be the same. Please make different selections.")
else:
    create_sunburst_plot(group1, threshold_g1, group2, threshold_g2)

## Xxxx map viz test
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

