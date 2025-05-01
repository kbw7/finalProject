
import streamlit as st
from update_database import get_food_entries, delete_food_entry, get_or_create_user
from user_profile import get_user_info
from db_sync import download_db_from_github
from home import render_sidebar
from datetime import datetime

render_sidebar()
download_db_from_github()

if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

user = get_user_info(st.session_state["access_token"])
user_id = get_or_create_user(user["email"])

st.title("Your Past Food Logs")

view_date = st.date_input("Select Date to View", datetime.now().date(), key="view_date")
formatted_view_date = view_date.strftime("%Y-%m-%d")
entries = get_food_entries(user_id, formatted_view_date)

if entries:
    for entry in entries:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 0.5])
            with col1:
                st.markdown(f"**{entry['food_item']}**")
                st.caption(f"{entry['meal_type']} from {entry['dining_hall']}")
                if entry['notes']:
                    st.text(f"Notes: {entry['notes']}")
            with col2:
                st.caption(f"{entry['calories']} cal")
                st.caption(f"{entry['protein']}g protein")
            with col3:
                if st.button("✕", key=f"delete_{entry['entry_id']}"):
                    delete_food_entry(entry["entry_id"])
                    st.rerun()
else:
    st.info("No food logs for this day yet.")

