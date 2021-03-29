from matplotlib.backends.backend_agg import RendererAgg
import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import altair as alt
import numpy as np

st.set_page_config(layout='wide')
matplotlib.use("agg")

_lock = RendererAgg.lock

sns.set_style('darkgrid')
row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.beta_columns(
    (1.5, 2, .2, 1, .1))

row0_1.title('RL for Layout Design Optimization :milky_way:')

with row0_2:
    st.write('')
    st.write('')

row0_2.subheader(
    'by Bekay')


row1_spacer1, row1_1, row1_spacer2 = st.beta_columns((.1, 3.2, .1))
@st.cache
def load_csv():
    df_input = pd.DataFrame()  
    df_input=pd.read_csv(input,sep=None ,engine='python', encoding='utf-8',
                            parse_dates=True,
                            infer_datetime_format=True)
    return df_input
    
with row1_1:
    ready_step1=False
    st.subheader('1. Data loading :open_file_folder:')
    st.write("Import a learning history csv file.")
    with st.beta_expander("Data format"): 
        st.write("Upload Training History CSV file for EDA")

    input = st.file_uploader('')
    
    if input:
        with st.spinner('Loading data..'):
            df = load_csv()
            col_name = list(df.columns)
            st.write(df)
            ready_step1=True




with row1_1:
    st.subheader('2. Learning Curve :mag:')
    st.write("Look into the learning curve")
    with st.beta_expander("Plot"): 
        st.write(" ")
    
    if ready_step1:
        df_copy = df.copy()
        selec_x = st.selectbox("Select X-axis: ", (col_name))
        st.write('Selected: ', selec_x)
        selec_y =  st.multiselect('Selected Variable for Y-axis',col_name,col_name)

        source = pd.DataFrame(df_copy[selec_y].values.round(2),columns=selec_y,index = pd.Index(df_copy[selec_x],name='x'))

        # Create a selection that moving average interval
        mv_avg_interval = st.select_slider('Moving Average',[0,5,10,15,20,25,30])
        if mv_avg_interval ==0:
            source = source.reset_index().melt('x', var_name='Legend', value_name='y')
        else:
            source = source.rolling(mv_avg_interval, min_periods=1).mean()
            source = source.reset_index().melt('x', var_name='Legend', value_name='y')
        st.write('Selected Moving Average Interval: ', mv_avg_interval)
        
        # Create a selection that chooses the nearest point & selects based on x-value
        nearest = alt.selection(type='single', nearest=True, on='mouseover',
                                fields=['x'], empty='none')
        line = alt.Chart(source).mark_line(interpolate='basis').encode(
        x=alt.X('x:Q', axis=alt.Axis(title=selec_x)),
        y='y:Q',
        color='Legend:N')

        # Transparent selectors across the chart. This is what tells us
        # the x-value of the cursor
        selectors = alt.Chart(source).mark_point().encode(
            x='x:Q',
            opacity=alt.value(0),
        ).add_selection(
            nearest
        )

        # Draw points on the line, and highlight based on selection
        points = line.mark_point().encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        )

        # Draw text labels near the points, and highlight based on selection
        text = line.mark_text(align='left', dx=5, dy=-5).encode(
            text=alt.condition(nearest, 'y:Q', alt.value(' '))
        )

        # Draw a rule at the location of the selection
        rules = alt.Chart(source).mark_rule(color='gray').encode(
            x='x:Q',
        ).transform_filter(
            nearest
        )

        # Put the five layers into a chart and bind the data
        lr_curve = alt.layer(
            line, selectors, points, rules, text
        ).properties(
            width=600, height=500
        )
        
        st.altair_chart(lr_curve,use_container_width=True)