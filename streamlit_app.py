import streamlit as st
import pandas as pd
import numpy as np
# import plotly.express as px

st.title('Test Dashboard using streamlit')

nosrl_df = pd.read_csv("data/nosrl_data_20230825-120846.csv")
#segments_df = pd.read_csv("data/segment_data_20230901-104355.csv")

df = nosrl_df

fig = px.density_mapbox(df, 
                        lat='lat', lon='lon', 
                        z = 'imd_score', radius=5,
                        zoom=6,
                        #color='brand', 
                        hover_name='urban_rural_desc', 
                        #mapbox_style='open-street-map',
                        mapbox_style='stamen-terrain', 
                        opacity=0.3,
                        title='test',
                        width=800, height=800,
)

# fig.show()
st.plotly_chart(fig)

