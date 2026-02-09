import streamlit as st

from pharmacy_sim import (
    Experiment,
    n_runs
)

st.title("A DES Model for a Pharmacy")

n_counters = 3
arrival_lambda = 1.5
choice_p = 0.5
n_reps = 10
warmup_period = 30
sim_time = 24 * 60

new_experiment = Experiment(
    n_counters = n_counters,
    arrival_lambda = arrival_lambda,
    choice_p = choice_p,
)

results = n_runs(
    experiment = new_experiment,
    warmup_time = warmup_period,
    sim_time = sim_time,
    n = n_reps
)

print(results.describe().round(2).T)