import streamlit as st
from lamport_sim import run_simulation
import io
import sys

st.title("Lamport Mutual Exclusion Simulation")

n = st.slider("Number of Processes", 2, 6, 3)

if st.button("Run Simulation"):
    buffer = io.StringIO()
    sys.stdout = buffer

    run_simulation(n)

    sys.stdout = sys.__stdout__

    st.text_area("Simulation Output", buffer.getvalue(), height=400)