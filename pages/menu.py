import streamlit as st
import pandas as pd
from datetime import datetime
from home import render_sidebar, get_params, dfKeys
from user_profile import get_user_info
from update_database import get_or_create_user, add_food_entry
from db_sync import download_db_from_github
import requests

st.set_page_config(page_title="Menu + Logging", layout="wide")
render_sidebar()
download_db_from_github()

if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

user = get_user_info(st.session_state["access_token"])
user_id = get_or_create_user(user["email"])

if 'selected_dishes' not in st.session_state:
    st.session_state['selected_dishes'] = []

st.title("Dining Menu & Food Logger")
tab1, tab2 = st.tabs(["Menu + Add", "Currently Logging"])

with tab1:
    col1, col2 = st.columns(2)
    selected_date = col1.date_input("Select Date", datetime.now().date())
    selected_location = col2.selectbox("Dining Hall", sorted(dfKeys["location"].unique()))

    for meal in ["Breakfast", "Lunch", "Dinner"]:
        location_id, meal_id = get_params(dfKeys, selected_location, meal)

        params = {
            "date": selected_date.strftime("%m-%d-%Y"),
            "locationID": location_id,
            "mealID": meal_id
        }
        r = requests.get("https://dish.avifoodsystems.com/api/menu-items", params=params)
        items = r.json()

        if not items:
            continue

        st.subheader(f"{meal} at {selected_location}")
        for item in items:
            name = item.get("name", "")
            station = item.get("stationName", "")
            nutrition = item.get("nutritionals", {})
            calories = nutrition.get("calories", "N/A")
            row = st.columns([4, 1, 2, 2])
            row[0].write(name)
            row[1].write(f"{calories} cal")
            row[2].write(station)
            added = row[3].selectbox("Add?", ["No", "Yes"], key=f"add_{meal}_{name}")
            if added == "Yes" and name not in [x['name'] for x in st.session_state['selected_dishes']]:
                st.session_state['selected_dishes'].append({
                    "name": name,
                    "dining_hall": selected_location,
                    "meal_type": meal,
                    "calories": float(calories) if calories else 0.0,
                    "protein": 0.0, "carbs": 0.0, "fat": 0.0
                })

with tab2:
    st.header("Foods Selected for Logging")
    if st.session_state['selected_dishes']:
        total_cal, total_pro, total_carb, total_fat = 0, 0, 0, 0
        for i, d in enumerate(st.session_state['selected_dishes']):
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
            c1.write(d["name"])
            c2.write(f"{d['calories']} cal")
            c3.write(f"{d['protein']}g")
            c4.write(f"{d['carbs']}g")
            c5.write(f"{d['fat']}g")
            total_cal += d['calories']
            total_pro += d['protein']
            total_carb += d['carbs']
            total_fat += d['fat']

        st.write("---")
        st.metric("Total Calories", f"{total_cal:.1f}")
        st.metric("Total Protein", f"{total_pro:.1f}g")
        st.metric("Total Carbs", f"{total_carb:.1f}g")
        st.metric("Total Fat", f"{total_fat:.1f}g")

        log_date = st.date_input("Log Date", datetime.now().date(), key="log_date")
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"], key="meal_type")
        notes = st.text_area("Meal Notes")

        if st.button("Log Meal Entry"):
            for d in st.session_state['selected_dishes']:
                add_food_entry(
                    user_id,
                    log_date.strftime("%Y-%m-%d"),
                    meal_type,
                    d['name'],
                    d['dining_hall'],
                    notes,
                    d['calories'],
                    d['protein'],
                    d['carbs'],
                    d['fat']
                )
            st.success("Meal successfully logged!")
            st.session_state['selected_dishes'] = []
    else:
        st.info("No items selected yet from the menu.")

