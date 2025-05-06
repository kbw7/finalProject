import streamlit as st
from datetime import datetime
from home import render_sidebar, get_params, dfKeys
from user_profile import get_user_info
from update_database import add_food_entry, get_food_entries, delete_food_entry, fetch_user_info
from db_sync import download_db_from_github, push_db_to_github
import requests
from collections import defaultdict
import ast

st.set_page_config(page_title="Log Meals", layout="wide")
render_sidebar()
download_db_from_github()

if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()


user = get_user_info(st.session_state["access_token"])
user_record = fetch_user_info(user["email"])
user_id = fetch_user_info(user["email"])[0]
user_allergens = []
# user_preferences = [] not enough time to look into dietary restrictions/preferences

# Code below from ChatGPT 

# Learning about the ast (Abstract Syntax Trees) library

# ast.literal_eval() is a safe version of eal() that only evaluations
# Python literals such as strings, numbers, lists, dicts, etc.

# Example: safe parsing of a string that looks like a list
# ast.literal_eval('[1, 2, 3]')
# # ➝ [1, 2, 3]

if user_record:
    try:
        user_allergens = ast.literal_eval(user_record[3]) if user_record[3] else []
        user_preferences = ast.literal_eval(user_record[4]) if user_record[4] else []
    except Exception as e:
        st.warning("Could not parse stored user allergies/preferences.")

if 'selected_dishes' not in st.session_state:
    st.session_state['selected_dishes'] = []

tab1, tab2, tab3 = st.tabs(["Select", "Log", "Journal"])

def dropKeys(cell): # from home, drop irrelevant keys
    cell.pop("id", None)
    cell.pop("corporateProductId", None)
    cell.pop("caloriesFromSatFat", None)
    return cell

with tab1:
    col1, col2, col3 = st.columns(3)
    selected_date = col1.date_input("Select Date", datetime.now().date())
    selected_location = col2.selectbox("Dining Hall", ["Bates", "Lulu", "Stone D", "Tower"]) # Changed this to just be the list of diningHalls - Kaurvaki
    selected_meal = col3.selectbox("Select Meal", ["Breakfast", "Lunch", "Dinner"]) 

    apply_custom_filter = st.checkbox("Apply my saved allergy and dietary preferences to filter menu")
    
    # Using variable "location" for getting the parameters because "Bae" is in the API but community knows dining hall as "Lulu" and not really "Bae"
    # See more detailed note in home.py under homePage() method in about line 210 - Kaurvaki
    if selected_location == "Lulu":
        location = "Bae"
    else:
        location = selected_location

    location_id, meal_id = get_params(dfKeys, location, selected_meal)

    params = {
        "date": selected_date.strftime("%m-%d-%Y"),
        "locationID": location_id,
        "mealID": meal_id
    }
    r = requests.get("https://dish.avifoodsystems.com/api/menu-items", params=params)
    items = r.json()

    if items:
        st.subheader(f"{selected_meal} at {selected_location}")
        header = st.columns([3, 1.5, 2.5, 0.5])
        header[0].markdown("**Dish**")
        header[1].markdown("**Calories**")
        header[2].markdown("**Station**")
        header[3].markdown("**Log**")
        for i, item in enumerate(items):
            name = item.get("name", "")
            station = item.get("stationName", "")
            allergies = [a['name'] for a in item.get("allergens", [])]
            preferences = [p['name'] for p in item.get("preferences", [])]

            if apply_custom_filter:
                if any(allergen in user_allergens for allergen in allergies):
                    continue
                if user_preferences and not any(pref in preferences for pref in user_preferences):
                    continue

            nutrition = item.get("nutritionals", {})
            nutrition = dropKeys(nutrition) if nutrition else {}
            calories = nutrition.get("calories", 0.0)
            protein = nutrition.get("protein", 0.0)
            carbs = nutrition.get("carbohydrates", 0.0)
            fat = nutrition.get("fat", 0.0)

            row = st.columns([3, 1.5, 2.5, 0.5])  # tighter layout
            row[0].write(name)
            row[1].write(f"{calories} cal")
            row[2].write(station)
            checked = row[3].checkbox("", key=f"add_{selected_meal}_{name}_{i}")
            if checked and name not in [x['name'] for x in st.session_state['selected_dishes']]:
                st.session_state['selected_dishes'].append({
                    "name": name,
                    "dining_hall": selected_location, # This will stay "selected_location" instead of "location" variable because Aileen later pulls from this to show entries in "Journal" tab so if user ate at "Lulu" we don't want them to see "Bae"
                    "meal_type": selected_meal,
                    "calories": float(calories),
                    "protein": float(protein),
                    "carbs": float(carbs),
                    "fat": float(fat)
                })
            elif not checked: # Added this in case the user unchecked a meal because then we don't want to save that entry in session_state. Found that if user selected a meal and then unchecked it, the meal would still be under "Log"
                index = 0 # Since I don't know the index of the unchecked dish dictionary... I need to find the index so I am using a counter - Kaurvaki
                for dish in st.session_state["selected_dishes"]:
                    if dish["name"] == name: # if it is the unchecked dish, then exit loop and remove that dish using that index.
                        break
                    else:
                        index = index + 1

                # Source on removing from list - https://www.w3schools.com/python/python_lists_remove.asp
                st.session_state["selectedDishes"].pop(index)




with tab2:
    st.header("Selected Foods")
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

        # metrics shows a number in a nice, bold box with a label on top
        st.markdown("### Macronutrient Breakdown")
        stat_cols = st.columns(4)
        stat_cols[0].metric("Calories", f"{total_cal:.1f}")
        stat_cols[1].metric("Protein", f"{total_pro:.1f}g")
        stat_cols[2].metric("Carbs", f"{total_carb:.1f}g")
        stat_cols[3].metric("Fat", f"{total_fat:.1f}g")

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
            push_db_to_github()
            st.session_state['last_logged_date'] = log_date
            st.success("Meal successfully logged and synced!")

            # Reset selected dishes
            st.session_state['selected_dishes'] = []
            
            # Clear checkbox states by creating new keys
            for key in list(st.session_state.keys()):
                if key.startswith("add_"):
                    del st.session_state[key]
            
            # Force a rerun to update the UI
            st.rerun()
            st.write(st.session_state['selected_dishes'])
    else:
        st.info("No items selected yet from the menu.")

with tab3:
    st.header("Your Past Food Logs")
    view_date = st.date_input("Select Date to View", st.session_state.get("last_logged_date", datetime.now().date()), key="view_date")
    formatted_view_date = view_date.strftime("%Y-%m-%d")

    # Get entries for a date
    entries = get_food_entries(user_id, formatted_view_date)

    if entries:
        # Group by meal type
        grouped_by_meal = defaultdict(list)
        for entry in entries:
            grouped_by_meal[entry['meal_type']].append(entry)

        # For each meal, group by notes
        # We want to group by notes as it is useful if they comment on meals
        for meal_type, meal_entries in grouped_by_meal.items():
            grouped_by_notes = defaultdict(list)
            for entry in meal_entries:
                grouped_by_notes[entry['notes']].append(entry)
            
            # Display each group of foods under its meal and note
            for note, note_entries in grouped_by_notes.items():
                total_cal = sum(e['calories'] for e in note_entries)
                total_pro = sum(e['protein'] for e in note_entries)
                total_carb = sum(e['carbs'] for e in note_entries)
                total_fat = sum(e['fat'] for e in note_entries)

                with st.expander(f"🍽️ {meal_type} — {len(note_entries)} items | {total_cal:.0f} cal"):
                    st.caption(f"**Total:** {total_pro:.1f}g protein, {total_carb:.1f}g carbs, {total_fat:.1f}g fat")
                    if note:
                        st.markdown(f"**Notes:** {note}")

                    for entry in note_entries:
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([3, 1, 0.5])
                            with col1:
                                st.markdown(f"**{entry['food_item']}**")
                                st.caption(f"{entry['dining_hall']}")
                            with col2:
                                st.caption(f"{entry['calories']} cal")
                                st.caption(f"{entry['protein']}g protein")
                            with col3:
                                if st.button("✕", key=f"delete_{entry['entry_id']}"):
                                    delete_food_entry(entry["entry_id"])
                                    push_db_to_github()
                                    st.rerun()
    else:
        st.info("No food logs for this day yet.")
