import streamlit as st

def google_login():
    """
    Simplified mock Google login function for development.
    In a real app, this would use OAuth with Google.
    """
    st.sidebar.info("This is a mock login for development.")
    
    with st.sidebar.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit and email and password:
            # Set session state to indicate logged in
            st.session_state["access_token"] = "fake-token"
            st.session_state["user_email"] = email
            st.session_state["user_name"] = email.split('@')[0].title()
            st.session_state["user_picture"] = "https://i.pravatar.cc/60"
            return True
            
    return False