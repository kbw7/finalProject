import streamlit as st

def render_user_profile():
    """Display user profile information in the sidebar."""
    if "user_name" in st.session_state:
        st.sidebar.write(f"Logged in as: {st.session_state['user_name']}")
        if "user_picture" in st.session_state:
            st.sidebar.image(st.session_state["user_picture"], width=60)