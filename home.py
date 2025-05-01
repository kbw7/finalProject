import streamlit as st
from auth import google_login
from user_profile import render_user_profile
import datetime
import pandas as pd
import requests
from user_profile import get_user_info
from db_sync import download_db_from_github
from userWalkthrough import newUser
from update_database import checkNewUser
from update_database import init_db

# -- Prof. Eni code start -- #
st.set_page_config(page_title="Wellesley Crave", layout="centered")

DEBUG = False # keep False when testing Google Login


# To access db
download_db_from_github()


def render_sidebar():
    """A function to handle the login in the sidebar."""
    st.sidebar.header("Login")

    if "access_token" in st.session_state:
        render_user_profile()

        if st.sidebar.button("Logout"):
            for key in ["access_token", "oauth_state"]:
                st.session_state.pop(key, None)
            st.rerun()

    else:
        st.sidebar.warning("Not logged in.")
        st.sidebar.markdown("Please log in with your Google Account using your **Wellesley** Email:")
        logged_in = google_login()
        if logged_in:
            st.rerun()



# This data can also be in a CSV file and then directly loaded from the file
data = [
    {'location': 'Bae', 'meal': 'Breakfast', 'locationID': 96, 'mealID': 148},
    {'location': 'Bae', 'meal': 'Lunch', 'locationID': 96, 'mealID': 149},
    {'location': 'Bae', 'meal': 'Dinner', 'locationID': 96, 'mealID': 312},
    {'location': 'Bates', 'meal': 'Breakfast', 'locationID': 95, 'mealID': 145},
    {'location': 'Bates', 'meal': 'Lunch', 'locationID': 95, 'mealID': 146},
    {'location': 'Bates', 'meal': 'Dinner', 'locationID': 95, 'mealID': 311},
    {'location': 'Stone D', 'meal': 'Breakfast', 'locationID': 131, 'mealID': 261},
    {'location': 'Stone D', 'meal': 'Lunch', 'locationID': 131, 'mealID': 262},
    {'location': 'Stone D', 'meal': 'Dinner', 'locationID': 131, 'mealID': 263},
    {'location': 'Tower', 'meal': 'Breakfast', 'locationID': 97, 'mealID': 153},
    {'location': 'Tower', 'meal': 'Lunch', 'locationID': 97, 'mealID': 154},
    {'location': 'Tower', 'meal': 'Dinner', 'locationID': 97, 'mealID': 310},
]
# Create a dataframe to make it easy to look up the IDs
dfKeys = pd.DataFrame(data)

# Build a sorted list of unique locations.
locations = sorted({item["location"] for item in data}) # this is a set
meals = sorted({item["meal"] for item in data})

def get_params(df, loc, meal):
    """Return locationID and mealID"""
    matching_df = df[(df["location"] == loc) & (df["meal"] == meal)]
    location_id = matching_df["locationID"].iloc[0]
    meal_id = matching_df["mealID"].iloc[0]
    return location_id, meal_id

# -- Prof. Eni code end -- #

# Kaurvaki code #
# Functions
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

def greeting_Menu():
    # Greeting at Top of Page
    device_datetime = datetime.datetime.now()

    hour = int(device_datetime.strftime("%H"))

    meal = ""

    greeting = ""
    if hour >= 1 and hour <= 10:
        greeting = "Good Morning ☀️"
        meal = "Breakfast"

    elif hour >= 11 and hour <= 16:
        greeting = "Good Afternoon ❤️ "
        meal = "Lunch"

    elif hour >= 17 and hour <= 23:
        greeting = "Good Evening 🌙"
        meal = "Dinner"

    st.title(greeting)


def homePage(): # only show once user has walkthrough!
    # Add navigation Bar
    # Source - https://docs.streamlit.io/develop/tutorials/multipage/st.page_link-nav

    greeting_Menu()

    # # preferred menu - retrieve user favHall from db
    # conn = sqlite3.connect(DB_PATH) # adding local path to private repo
    # c = conn.cursor()

    # c.execute("SELECT diningHall FROM users WHERE email = ?", (user.get("email"),))

    # diningHall = c.fetchone()[0]


    # # Prof. Eni function get_params()
    # location_id, meal_id = get_params(dfKeys,
    #                                     diningHall,
    #                                     meal)

    # d = datetime.date.today()

    # df = get_menu(d, location_id, meal_id)
    # # We only want today's menu... not the whole week
    # # format of date data in df: 2025-04-14T00:00:00

    # today = d.strftime("%Y") + "-" + d.strftime("%m") + "-" + d.strftime("%d") + "T00:00:00"

    # df = df[df["date"] == today] # only shows today's meals

    # # cleaning up df
    # df = df.drop_duplicates(subset= ["id"], keep = "first")
    # df = df.drop(columns = ["date", "image", "id", "categoryName", "stationOrder", "price"])

    # df["allergens"] = df["allergens"].apply(transform)

    # df["preferences"] = df["preferences"].apply(transform)

    # df["nutritionals"] = df["nutritionals"].apply(dropKeys)

    # # to convert all values into floats, except for col "servingSizeUOM", which would be a string.
    # colNames = df.iloc[0].nutritionals.keys()
    # for key in colNames:
    #     if key == "servingSizeUOM":
    #         df[key] = df["nutritionals"].apply(lambda dct: str(dct["servingSizeUOM"]))
    #     else:
    #         df[key] = df["nutritionals"].apply(lambda dct: float(dct[key]))

    # df = df.drop("nutritionals", axis = 1)


    # # Menu Title and Info.
    # st.subheader(meal + " Today at " + diningHall)

    # dish, calories, category = st.columns(3)

    # with dish:
    #     st.write("Dish")

    # with calories:
    #     st.write("Calories")

    # with category:
    #     st.write("Category")

    # # with journal:
    # #     st.write("Add to Journal")

    # num = 0

    # for index, row in df.iterrows():
    #     dish, calories, category = st.columns(3)
    #     with dish:
    #         st.write(row["name"])

    #     with calories:
    #         st.write(row["calories"])

    #     with category:
    #         st.write(row["stationName"])

        # with journal:
        #     st.button("Add", key = num)
        #     num += 1

#----------------- HOME Page -----------------#
# Show login
if __name__ == "__main__":
    init_db()
    print("Database initialized.")

render_sidebar()

if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

 # Access Logged-In User Email
access_token = st.session_state.get("access_token")
user = get_user_info(access_token)

# After user logs in, have to call new_user() to see if new user needs walkthrough
check = checkNewUser(user.get("email"))

if check: # if new user, then go through walkthrough
    newUser(user)

homePage()
