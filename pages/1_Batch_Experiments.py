import streamlit as st
import pandas as pd
from utils.io import read_file
from utils.csv import get_example_csv

INFO1 = "**Execute several experiments in a batch.**"
INFO2 = "### Upload a CSV file containing input parameters."


st.title("Pharmacy Simulation")

st.markdown(INFO1)

with st.expander("Template you can use for experiments"):
    st.markdown(read_file("./markdown/template_info.md"))
    template_csv = get_example_csv()
    st.dataframe(template_csv, hide_index=True)
    
st.markdown(INFO2)
uploaded_file = st.file_uploader("Choose a .csv file")
if uploaded_file is not None:
    df_experiments = pd.read_csv(uploaded_file)
    st.write("Loaded Experiments")
    st.table(df_experiments)
    
    n_reps = st.number_input("No. of Replications", 2, 1000, value=10, step=1)
    warmup_period = st.number_input("Warm Up Period (minutes)", 0, 1000, value=30, step=10)
    sim_time_mins = st.number_input("Data Collection Period (hours)", 1.0, 10000.0, value=24.0, step=0.5)
    stock_init = st.number_input("Maximum and Initial Stock", 10, 10000, value=250, step=10)
    med_thresh_percent = st.slider("Threshold for Restock (%)", 0, 100, value=50, step=1)