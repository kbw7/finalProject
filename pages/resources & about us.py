import streamlit as st
from user_profile import render_user_profile
from home import render_sidebar

def render_sidebar():
    """A function to handle the login in the sidebar."""
    blank_square = "https://i.imgur.com/3Th4rvF.png"
    sidebar_image_url = "https://i.imgur.com/oyBooq2.jpeg"


    logo_image_url = "https://i.imgur.com/4vlJszs.png"
    st.markdown(
        f"""
        <style>
        .logo {{
            margin-top: 10px;
            z-index: 1000;
        }}
        </style>
        <div class="logo">
            <img src="{logo_image_url}" alt="Logo" width="600">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Add custom CSS for aligning content at the bottom
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("{sidebar_image_url}");
            background-size: cover;
            background-position: center;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            padding-bottom: 20px;
        }}
        .sidebar-content {{
            text-align: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar content
    st.sidebar.markdown(
        f"""
        <div class="sidebar-content">
            <img src="{blank_square}" alt="Logo" width="350">

        </div>
        """,
        unsafe_allow_html=True,
    )

    if "access_token" in st.session_state:
        render_user_profile()

        if st.sidebar.button("Logout"):
            for key in ["access_token", "oauth_state"]:
                st.session_state.pop(key, None)
            st.rerun()
    else:
        st.sidebar.warning("Not logged in.")
        st.sidebar.markdown("Please log in with your Google Account using your **Wellesley** Email:")
        logged_in = google_login()
        if logged_in:
            st.rerun()

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
