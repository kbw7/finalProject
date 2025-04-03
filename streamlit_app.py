import csv
import requests
from datetime import datetime
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

    # New code we are adding
    result = pd.DataFrame(data)

    return result

def transform(cell):
    result = ""
    if cell:
        # result is a string where each allergen in the list in the cell is brought together
        result = ",".join([item["name"] for item in cell])
    
    return result

def dropKeys(cell):
    cell.pop("id")
    cell.pop("corporateProductId")
    cell.pop("caloriesFromSatFat")
    return cell




# Add header
st.header("Welcome to our Wellesley Fresh App!")



# let's do st.form!!
with st.form("Find a menu!"):
    st.header("WFresh")

    user_date = st.date_input("Select a Date", datetime.now().date())

    formatted = user_date.strftime("%m-%d-%Y")
    
    user_location = st.selectbox("Select location", ["Tower", "Bates", "Bae", "Stone D"])

    user_meal = st.selectbox("Select meal", ["Breakfast", "Lunch", "Dinner"])

    for dct in idInfo:
        if (dct["location"] == user_location) and (dct["meal"] == user_meal):
            location = dct["locationID"]
            meal = dct["mealID"]


    submit_button = st.form_submit_button("View Menu", type = "primary")

# if user submits choices
if submit_button:
    df = get_menu(formatted, location, meal)

    #clean df!
    df = df.drop_duplicates(subset= ["id"], keep = "first")
    df = df.drop(columns = ["date", "image", "id", "categoryName", "stationOrder", "price"])

    df["allergens"] = df["allergens"].apply(transform)

    df["preferences"] = df["preferences"].apply(transform)

    df["nutritionals"] = df["nutritionals"].apply(dropKeys)

    # to convert all values into floats, except for col "servingSizeUOM", which would be a string.
    colNames = df.iloc[0].nutritionals.keys()
    for key in colNames:
        if key == "servingSizeUOM":
            df[key] = df["nutritionals"].apply(lambda dct: str(dct["servingSizeUOM"]))
        else:
            df[key] = df["nutritionals"].apply(lambda dct: float(dct[key]))

    df = df.drop("nutritionals", axis = 1)

    for n in df["name"]:
        st.write(n)

    with st.expander("**Expand to see Detailed Dataset of all Meals**"):
        st.write(df)



    





    