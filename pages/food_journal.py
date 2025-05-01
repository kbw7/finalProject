import csv
import requests
import json
import sqlite3
import os
import uuid
from datetime import datetime
import pandas as pd
import streamlit as st

from home import render_sidebar
from user_profile import get_user_info
from db_sync import download_db_from_github, push_db_to_github
from update_database import (
    init_db,
    get_or_create_user,
    add_food_entry,
    get_food_entries,
    delete_food_entry
)

# Initialize sidebar and download database
render_sidebar()
download_db_from_github()

# Ensure user is logged in
if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

# Get user info
access_token = st.session_state.get("access_token")
user = get_user_info(access_token)
userId = get_or_create_user(user["email"])

# Session state setup
if 'selected_dishes' not in st.session_state:
    st.session_state['selected_dishes'] = []
if 'meal_notes' not in st.session_state:
    st.session_state['meal_notes'] = ""

# Menu data
idInfo = [
    {"location": "Bae", "meal": "Breakfast", "locationID": "96", "mealID": "148"},
    {"location": "Bae", "meal": "Lunch", "locationID": "96", "mealID": "149"},
    {"location": "Bae", "meal": "Dinner", "locationID": "96", "mealID": "312"},
    {"location": "Bates", "meal": "Breakfast", "locationID": "95", "mealID": "145"},
    {"location": "Bates", "meal": "Lunch", "locationID": "95", "mealID": "146"},
    {"location": "Bates", "meal": "Dinner", "locationID": "95", "mealID": "311"},
    {"location": "StoneD", "meal": "Breakfast", "locationID": "131", "mealID": "261"},
    {"location": "StoneD", "meal": "Lunch", "locationID": "131", "mealID": "262"},
    {"location": "StoneD", "meal": "Dinner", "locationID": "131", "mealID": "263"},
    {"location": "Tower", "meal": "Breakfast", "locationID": "97", "mealID": "153"},
    {"location": "Tower", "meal": "Lunch", "locationID": "97", "mealID": "154"},
    {"location": "Tower", "meal": "Dinner", "locationID": "97", "mealID": "310"}
]

def fetch_all_menu_items():
    menu_items = []
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%m-%d-%Y")

    for item in idInfo:
        try:
            params = {
                "date": formatted_date,
                "locationId": item["locationID"],
                "mealId": item["mealID"]
            }
            response = requests.get("https://dish.avifoodsystems.com/api/menu-items/week", params=params)
            response.raise_for_status()
            data = response.json()
            for food_item in data:
                food_item["dining_hall"] = item["location"]
                food_item["meal_type"] = item["meal"]
                menu_items.append(food_item)
        except requests.RequestException as e:
            st.error(f"Error fetching menu for {item['location']} {item['meal']}: {e}")

    return menu_items

def extract_nutritional_info(nutritionals):
    if not nutritionals:
        return 0.0, 0.0, 0.0, 0.0
    return (
        float(nutritionals.get("calories", 0) or 0),
        float(nutritionals.get("protein", 0) or 0),
        float(nutritionals.get("carbohydrates", 0) or 0),
        float(nutritionals.get("fat", 0) or 0)
    )

# ---------- UI ---------- #
st.title("Wellesley Food Journal")
tab1, tab2 = st.tabs(["Log Food", "View Journal"])

# --- LOG FOOD TAB --- #
with tab1:
    st.header("Log Your Meals")
    if 'all_menu_items' not in st.session_state:
        with st.spinner("Loading menu items..."):
            st.session_state['all_menu_items'] = fetch_all_menu_items()

    food_options = []
    food_item_map = {}
    for item in st.session_state['all_menu_items']:
        name = item.get('name', '')
        if name:
            label = f"{name} ({item['dining_hall']} - {item['meal_type']})"
            food_options.append(label)
            food_item_map[label] = item
    food_options.sort()

    col1, col2 = st.columns(2)
    log_date = col1.date_input("Date", datetime.now().date())
    meal_type = col2.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])

    selected_food = st.selectbox("Search for food item", options=[""] + food_options, index=0, key="food_search")

    if selected_food and st.button("Add to Meal"):
        selected_item = food_item_map.get(selected_food)
        if selected_item:
            food_name = selected_item.get('name', '')
            dining_hall = selected_item.get('dining_hall', '')
            item_meal_type = selected_item.get('meal_type', '')
            calories, protein, carbs, fat = extract_nutritional_info(selected_item.get('nutritionals', {}))

            st.session_state['selected_dishes'].append({
                "name": food_name,
                "dining_hall": dining_hall,
                "meal_type": item_meal_type,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat
            })
            st.success(f"Added {food_name} to your meal!")
            st.rerun()

    if st.session_state['selected_dishes']:
        st.subheader("Selected Items for this Meal")
        total_calories = total_protein = total_carbs = total_fat = 0

        for i, dish in enumerate(st.session_state['selected_dishes']):
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 0.5])
                col1.write(f"**{dish['name']}**")
                col1.caption(f"From: {dish['dining_hall']}")
                col2.caption(f"Calories: {dish['calories']:.1f}")
                col2.caption(f"Protein: {dish['protein']:.1f}g")
                col2.caption(f"Carbs: {dish['carbs']:.1f}g")
                col2.caption(f"Fat: {dish['fat']:.1f}g")
                if col3.button("\u2715", key=f"remove_{i}"):
                    st.session_state['selected_dishes'].pop(i)
                    st.rerun()

            total_calories += dish['calories']
            total_protein += dish['protein']
            total_carbs += dish['carbs']
            total_fat += dish['fat']

        st.subheader("Meal Totals")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", f"{total_calories:.1f}")
        c2.metric("Protein", f"{total_protein:.1f}g")
        c3.metric("Carbs", f"{total_carbs:.1f}g")
        c4.metric("Fat", f"{total_fat:.1f}g")

        st.session_state['meal_notes'] = st.text_area("Notes", st.session_state['meal_notes'])

        if st.button("Log Complete Meal"):
            formatted_date = log_date.strftime("%Y-%m-%d")
            for dish in st.session_state['selected_dishes']:
                add_food_entry(
                    userId, formatted_date, meal_type, dish['name'],
                    dish['dining_hall'], st.session_state['meal_notes'],
                    dish['calories'], dish['protein'], dish['carbs'], dish['fat']
                )
            push_db_to_github()
            st.success("Meal logged and database updated!")
            st.session_state['selected_dishes'] = []
            st.session_state['meal_notes'] = ""
            st.rerun()
    else:
        st.info("Search and add items to your meal.")

# --- VIEW JOURNAL TAB --- #
with tab2:
    st.header("Your Food Journal")
    view_date = st.date_input("Select Date to View", datetime.now().date(), key="view_date")
    formatted_view_date = view_date.strftime("%Y-%m-%d")
    entries = get_food_entries(userId, formatted_view_date)

    if entries:
        meal_entries = {}
        for entry in entries:
            meal_entries.setdefault(entry['meal_type'], []).append(entry)

        for meal, group in meal_entries.items():
            st.subheader(meal)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calories", f"{sum(e['calories'] for e in group):.1f}")
            c2.metric("Protein", f"{sum(e['protein'] for e in group):.1f}g")
            c3.metric("Carbs", f"{sum(e['carbs'] for e in group):.1f}g")
            c4.metric("Fat", f"{sum(e['fat'] for e in group):.1f}g")

            for entry in group:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 0.5])
                    col1.markdown(f"**{entry['food_item']}**")
                    col1.caption(f"Dining Hall: {entry['dining_hall']}")
                    if entry['notes']:
                        col1.text(f"Notes: {entry['notes']}")
                    col2.caption(f"Calories: {entry['calories']}")
                    col2.caption(f"Protein: {entry['protein']}g")
                    col2.caption(f"Carbs: {entry['carbs']}g")
                    col2.caption(f"Fat: {entry['fat']}g")
                    if col3.button("\u2715", key=f"delete_button_{entry['entry_id']}"):
                        delete_food_entry(entry['entry_id'])
                        push_db_to_github()
                        st.rerun()
    else:
        st.info(f"No entries for {view_date.strftime('%B %d, %Y')}.")