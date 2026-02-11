import streamlit as st
import pandas as pd
from utils.io import read_file
from utils.csv import get_example_csv, create_experiments
from utils.plotting import experiment_summary_frame
from pharmacy_model import n_runs

def run_all(
    experiments,
    warmup_period,
    sim_time,
    n_reps = 5
):
    print("Model experiments:")
    print(f"No. experiments to execute = {len(experiments)}\n")

    experiment_results = {}
    
    for exp_name, experiment in experiments.items():
        print(f"Running {exp_name}", end=" => ")
        results = n_runs(
            experiment, warmup_period, sim_time, n_reps
        )
        print("done.\n")
        
        experiment_results[exp_name] = results
        
    print("All experiments are complete.")

    return experiment_results

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
    sim_time = sim_time_mins * 60
    med_thresh = (med_thresh_percent / 100) * stock_init
    
    if st.button("Execute Experiments"):
        experiments = create_experiments(df_experiments)
        with st.spinner("Running all experiments..."):
            results = run_all(
                experiments,
                warmup_period,
                sim_time,
                n_reps
            )
            st.success("Done!")
            
        df_results = experiment_summary_frame(results)
        st.dataframe(df_results.round(2))
        
    
    
