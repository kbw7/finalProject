# Settings page where user enters preferences, allergens, etc. 
import streamlit as st
import pandas as pd
from datetime import datetime
from home import render_sidebar

# To make sure it is not accessible unless they log in
render_sidebar()
if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

st.title("Settings ⚙️")

# Add go-to dining hall preference
st.header("Select your go-to or favorite dining hall (for Home Page Menu)")
favDiningHall = st.selectbox("Choose One", ["Tower", "Bae", "Stone D", "Bates"])

