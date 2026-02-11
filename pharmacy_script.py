import streamlit as st
from utils.io import read_file
from utils.plotting import create_user_controlled_hist
from utils.name_mappings import get_name_mappings
from pharmacy_sim import (
    Experiment,
    n_runs
)

st.set_page_config(
    page_title="Pharmacy DES",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("A DES Model for a Pharmacy")
st.markdown(read_file("./markdown/scenario.md"))

with st.sidebar:
    st.subheader("Parameters")
    n_counters = st.slider("Number of Pharmacists", 1, 10, value=3, step=1)
    arrival_lambda = st.slider("Arrival Rate", 0.1, 3.0, value=1.5, step=0.1)
    choice_p_percent = st.slider("Prescription probability (%)", 5, 95, value=60, step=5)
    n_reps = st.number_input("No. of Replications", 2, 1000, value=10, step=1)
    warmup_period = st.number_input("Warm Up Period (minutes)", 0, 1000, value=30, step=10)
    sim_time_mins = st.number_input("Data Collection Period (hours)", 1.0, 10000.0, value=24.0, step=0.5)
    travel_time = st.number_input("Travel time from warehouse to pharmacy", 0, 24*60, value=30, step=5)
    travel_variation = st.number_input("Travel time variation (+-)", 0, travel_time, value=10, step=5)
    stock_init = st.number_input("Maximum and Initial Stock", 10, 10000, value=250, step=10)
    med_thresh_percent = st.slider("Threshold for Restock (%)", 0, 100, value=50, step=1)
    check_interval = st.number_input("Restock Check Interval (minutes)", 5, 24*60, value=30, step=5)

    sim_time = sim_time_mins * 60
    med_thresh = (med_thresh_percent / 100) * stock_init
    choice_p = choice_p_percent / 100

new_experiment = Experiment(
    n_counters = n_counters,
    arrival_lambda = arrival_lambda,
    choice_p = choice_p,
    travel_time = travel_time,
    travel_noise = travel_variation
)

if st.button("Run Simulation"):
    with st.spinner("Running Simulation..."):
        results = n_runs(
            experiment = new_experiment,
            warmup_time = warmup_period,
            sim_time = sim_time,
            n = n_reps
        )
        
    st.success("Simulation complete.")

    col1, col2 = st.columns(2)
    
    with col1.expander("Tabular Results", expanded=True):
        st.dataframe(results.describe().round(2).T)
        
    with col2.expander("Histogram", expanded=True):
        fig = create_user_controlled_hist(results, 
                                      name_mappings=get_name_mappings())
        st.plotly_chart(fig)