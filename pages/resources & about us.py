import streamlit as st
from home import render_sidebar

render_sidebar()
if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

st.subheader("Mission Statement")
st.write("WellesleyCrave is an app made by CS248 students: Kaurvaki, Aileen, and Rebecca. Our app's purpose is to make the food logging experience for Wellesley students a positive one! All of the information regarding food is sourced from Wellesley Fresh AVI.")

st.subheader("Contact Information")
st.write("If you have any questions or concerns regarding the WellesleyCrave app, please email any of us!")
st.markdown("* Kaurvaki Bajpai (kb120@wellesley.edu)")
st.markdown("* Aileen Du (ad128@wellesley.edu)")
st.markdown("* Rebecca Hsia (rh109@wellesley.edu)")

st.write("If you have any questions or concerns with Wellesley Fresh...")
st.markdown("* You can text the Manager -> **781-531-9113**")
st.markdown("* There is also the Wellesley Fresh website and Here is the link to their Contact Page: http://wellesleyfresh.com/connect-with-us.html")

st.subheader("Feedback!")
st.write("Our app is a work in progress! There are a lot of features that we have not implemented yet and we would love to hear your feedback on your experience using WellesleyCrave so we can improve the user experience! Click the button below to fill out our User Feedback Form.")
st.link_button("User Feedback Form", "https://forms.gle/1gE8nPThvnYzgMsCA", type = "secondary", disabled = False)
