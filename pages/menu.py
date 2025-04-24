# Some code taken from Milestone 1 assignment
import streamlit as st
import pandas as pd
import csv
import requests
from datetime import datetime
from home import render_sidebar

# MENU PAGE
render_sidebar()
if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

st.title("AVI MENU")

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

def get_menu(date, locationID, mealID):
    base_url = "https://dish.avifoodsystems.com/api/menu-items"
    params = {"date": date, "locationID": locationID, "mealID": mealID}
    response = requests.get(base_url, params=params)
    data = response.json()
    return pd.DataFrame(data)

with st.form("usda_form"):
    usda_query = st.text_input("Custom Search", placeholder="ex.banana, egg, mac and cheese...")
    usda_submit = st.form_submit_button("Search USDA Database")

if usda_submit and usda_query:
    USDA_API_KEY = "rlj3A5DuEvKSU5kApge850sesah6DKfungjCGusF"
    usda_url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    params = {
        "query": usda_query,
        "pageSize": 5,
        "api_key": USDA_API_KEY
    }

    response = requests.get(usda_url, params=params)

    if response.status_code != 200:
        st.error("Could not fetch USDA data.")
    else:
        data = response.json().get("foods", [])

        if not data:
            st.write("No foods found. Try another item.")
        else:
            for food in data:
                st.subheader(food.get("description", "Food"))
                st.write("**Brand:**", food.get("brandOwner", "N/A"))

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    calories = next((nutrient["value"] for nutrient in food["foodNutrients"] if nutrient["nutrientName"] == "Energy"), "N/A")
                    st.metric("Calories", f"{calories} kcal")

                with col2:
                    protein = next((nutrient["value"] for nutrient in food["foodNutrients"] if nutrient["nutrientName"] == "Protein"), "N/A")
                    st.metric("Protein", f"{protein} g")

                with col3:
                    carbs = next((nutrient["value"] for nutrient in food["foodNutrients"] if nutrient["nutrientName"] == "Carbohydrate, by difference"), "N/A")
                    st.metric("Carbs", f"{carbs} g")

                with col4:
                    fat = next((nutrient["value"] for nutrient in food["foodNutrients"] if nutrient["nutrientName"] == "Total lipid (fat)"), "N/A")
                    st.metric("Fat", f"{fat} g")

def transform(cell):
    return ",".join([item["name"] for item in cell]) if cell else ""

def dropKeys(cell):
    cell.pop("id", None)
    cell.pop("corporateProductId", None)
    cell.pop("caloriesFromSatFat", None)
    return cell

with st.form("Find a menu!"):
    st.header("WFresh")

    user_date = st.date_input("Select a Date", datetime.now().date())
    formatted = user_date.strftime("%m-%d-%Y")

    user_location = st.selectbox("Select location", ["Tower", "Bates", "Bae", "StoneD"])
    submit_button = st.form_submit_button("View Full Menu", type="primary")

if submit_button:
    location_meals = [dct for dct in idInfo if dct["location"] == user_location]
    meal_order = ["Breakfast", "Lunch", "Dinner"]

    for meal_name in meal_order:
        info = next((m for m in location_meals if m["meal"] == meal_name), None)
        if info:
            st.markdown(
                f"""
                <h1 style='background-color: #1a4ca3; color: white; padding: 10px; border-radius: 5px; text-align: center;'>
                    {meal_name}
                </h1>
                """,
                unsafe_allow_html=True
            )
            df = get_menu(formatted, info["locationID"], info["mealID"])

            if df.empty:
                st.write(f"No {meal_name} menu available.")
                continue

            # Clean up DataFrame
            df = df.drop_duplicates(subset=["id"], keep="first")
            df = df.drop(columns=["date", "image", "id", "categoryName", "stationOrder", "price"], errors="ignore")

            df["allergens"] = df["allergens"].apply(transform)
            df["preferences"] = df["preferences"].apply(transform)
            df["nutritionals"] = df["nutritionals"].apply(dropKeys)

            colNames = df.iloc[0].nutritionals.keys()
            for key in colNames:
                if key == "servingSizeUOM":
                    df[key] = df["nutritionals"].apply(lambda dct: str(dct["servingSizeUOM"]))
                else:
                    df[key] = df["nutritionals"].apply(lambda dct: float(dct[key]))

            df = df.drop("nutritionals", axis=1)

            # Column layout
            col1, col2, col3 = st.columns([5, 2, 3])
            with col1:
                st.markdown("**Dish**")
            with col2:
                st.markdown("**Calories**")
            with col3:
                st.markdown("**Category**")

            for _, row in df.iterrows():
                col1, col2, col3 = st.columns([5, 2, 3])
                with col1:
                    st.write(row.get("name", "N/A"))
                with col2:
                    st.write(row.get("calories", "—"))
                with col3:
                    st.write(row.get("stationName", "—"))
