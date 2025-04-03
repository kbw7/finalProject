import csv
import json
import requests
from datetime import datetime
import time
import os
import pandas as pd
import streamlit as st


idInfo = [{"location": "Bae", "meal" : "Breakfast", "locationID" : "96", "mealID" : "148"},
          {"location": "Bae", "meal" : "Lunch", "locationID" : "96", "mealID" : "149"},
          {"location": "Bae", "meal" : "Dinner", "locationID" : "96", "mealID" : "312"},
          {"location": "Bates", "meal" : "Breakfast", "locationID" : "95", "mealID" : "145"},
          {"location": "Bates", "meal" : "Lunch", "locationID" : "95", "mealID" : "146"},
          {"location": "Bates", "meal" : "Dinner", "locationID" : "95", "mealID" : "311"},
          {"location": "StoneD", "meal" : "Breakfast", "locationID" : "131", "mealID" : "261"},
          {"location": "StoneD", "meal" : "Lunch", "locationID" : "131", "mealID" : "262"},
          {"location": "StoneD", "meal" : "Dinner", "locationID" : "131", "mealID" : "263"},
          {"location": "Tower", "meal" : "Breakfast", "locationID" : "97", "mealID" : "153"},
          {"location": "Tower", "meal" : "Lunch", "locationID" : "97", "mealID" : "154"},
          {"location": "Tower", "meal" : "Dinner", "locationID" : "97", "mealID" : "310"}
        ]

with open("wellesley-dining.csv", "w") as fileToWrite:
    csvWriter = csv.DictWriter(fileToWrite, fieldnames = idInfo[0].keys())
    csvWriter.writeheader()
    csvWriter.writerows(idInfo)

def get_menu(date, locationID, mealID):
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"

    params = {"date" : date, "locationID" : locationID, "mealID" : mealID}

    response = requests.get(base_url, params = params)

    fullUrl = response.url

    data = requests.get(fullUrl).json()

    return data

# add Streamlit option of date widget to add in for write_menus() function

# Add header
st.header("Welcome to our Wellesley Fresh App!")
# Add selectboxes (for date, meal, and location)
# let's do st.form!!
with st.form("Find a menu!"):
    st.header("WFresh")

    user_date = st.date_input("Select a Date", datetime.now().date())
    user_location = st.selectbox("Select location", ["Tower", "Bates", "Lulu", "Stone D"])
    user_meal = st.selectbox("Select meal", ["Breakfast", "Lunch", "Dinner"])

    submit_button = st.form_submit_button("View Menu", type = "primary")

if submit_button:
    get_menu(user_date, user_location, user_meal)
    

# Save those options in variables to add to our functions as arguments

# Call functions and produce menu output