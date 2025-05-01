import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from update_database import (
    init_db, get_or_create_user, add_food_entry, get_food_entries, delete_food_entry
)
from user_profile import get_user_info

# ---------- Setup ----------
init_db()
st.title("Wellesley Dining")

# ---------- Authentication ----------
# (Update with real auth method)
user = {"email": "test@wellesley.edu"}
user_id = get_or_create_user(user["email"])

# ---------- Constants ----------
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
        except requests.RequestException:
            continue
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

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["View Menu", "Log Food", "Food Journal"])

# ---------- Tab 1: Menu ----------
with tab1:
    st.header("Dining Hall Menu")
    selected_date = st.date_input("Choose Date", datetime.now().date(), key="menu_date")
    selected_location = st.selectbox("Dining Hall", ["Tower", "Bates", "Bae", "StoneD"])
    if st.button("Load Menu"):
        meals = [d for d in idInfo if d["location"] == selected_location]
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            info = next((m for m in meals if m["meal"] == meal), None)
            if info:
                st.subheader(meal)
                params = {
                    "date": selected_date.strftime("%m-%d-%Y"),
                    "locationID": info["locationID"],
                    "mealID": info["mealID"]
                }
                r = requests.get("https://dish.avifoodsystems.com/api/menu-items", params=params)
                data = r.json()
                for item in data:
                    st.markdown(f"**{item['name']}** - {item['stationName']} - {item.get('calories', 'N/A')} cal")

# ---------- Tab 2: Log Food ----------
with tab2:
    st.header("Log Your Meal")
    if 'all_menu_items' not in st.session_state:
        st.session_state['all_menu_items'] = fetch_all_menu_items()
    if 'selected_dishes' not in st.session_state:
        st.session_state['selected_dishes'] = []
    if 'meal_notes' not in st.session_state:
        st.session_state['meal_notes'] = ""

    food_options = []
    food_map = {}
    for item in st.session_state['all_menu_items']:
        label = f"{item['name']} ({item['dining_hall']} - {item['meal_type']})"
        food_options.append(label)
        food_map[label] = item

    col1, col2 = st.columns(2)
    log_date = col1.date_input("Date", datetime.now().date())
    meal_type = col2.selectbox("Meal", ["Breakfast", "Lunch", "Dinner", "Snack"])
    selected_food = st.selectbox("Choose item", [""] + food_options)

    if selected_food and st.button("Add Item"):
        item = food_map[selected_food]
        cal, pro, carb, fat = extract_nutritional_info(item.get("nutritionals", {}))
        st.session_state['selected_dishes'].append({
            "name": item["name"], "dining_hall": item["dining_hall"],
            "meal_type": item["meal_type"], "calories": cal,
            "protein": pro, "carbs": carb, "fat": fat
        })
        st.rerun()

    for i, d in enumerate(st.session_state['selected_dishes']):
        st.markdown(f"**{d['name']}** ({d['dining_hall']}) - {d['calories']} cal")
        if st.button("Remove", key=f"remove_{i}"):
            st.session_state['selected_dishes'].pop(i)
            st.rerun()

    st.session_state['meal_notes'] = st.text_area("Meal Notes", st.session_state['meal_notes'])

    if st.button("Log Meal"):
        for d in st.session_state['selected_dishes']:
            add_food_entry(
                user_id, log_date.strftime("%Y-%m-%d"), meal_type, d["name"], d["dining_hall"],
                st.session_state['meal_notes'], d["calories"], d["protein"], d["carbs"], d["fat"]
            )
        st.success("Meal logged.")
        st.session_state['selected_dishes'] = []
        st.session_state['meal_notes'] = ""
        st.rerun()

# ---------- Tab 3: Journal ----------
with tab3:
    st.header("Your Food Journal")
    view_date = st.date_input("View Date", datetime.now().date(), key="journal_date")
    journal_entries = get_food_entries(user_id, view_date.strftime("%Y-%m-%d"))

    if not journal_entries:
        st.info("No entries for selected date.")
    else:
        for entry in journal_entries:
            with st.container(border=True):
                st.markdown(f"**{entry['food_item']}** ({entry['dining_hall']})")
                st.caption(f"{entry['meal_type']} - {entry['calories']} cal, {entry['protein']}g protein")
                if entry["notes"]:
                    st.caption(f"Notes: {entry['notes']}")
                if st.button("Delete", key=f"del_{entry['entry_id']}"):
                    delete_food_entry(entry["entry_id"])
                    st.rerun()