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
from update_database import getUserFavDiningHall
from notification import check_favorites_available


# -- Prof. Eni code start -- #
st.set_page_config(page_title="Wellesley Crave", layout="centered")

DEBUG = False # keep False when testing Google Login


# To access db
download_db_from_github()

# Access Logged-In User Email
access_token = st.session_state.get("access_token")

if not access_token:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

user = get_user_info(access_token)
if not user:
    st.error("Unable to fetch user information. Please log in again.")
    st.stop()

st.session_state["user_id"] = user["email"]


def render_sidebar():
    """A function to handle the login in the sidebar."""
    blank_square = "https://i.imgur.com/3Th4rvF.png"
    sidebar_image_url = "https://i.imgur.com/oyBooq2.jpeg"


    logo_image_url = "https://i.imgur.com/4vlJszs.png"
    st.markdown(
        f"""
        <style>
        .logo {{
            margin-top: 10px;
            z-index: 1000;
        }}
        </style>
        <div class="logo">
            <img src="{logo_image_url}" alt="Logo" width="600">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Add custom CSS for aligning content at the bottom
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("{sidebar_image_url}");
            background-size: cover;
            background-position: center;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            padding-bottom: 20px;
        }}
        .sidebar-content {{
            text-align: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar content
    st.sidebar.markdown(
        f"""
        <div class="sidebar-content">
            <img src="{blank_square}" alt="Logo" width="350">

        </div>
        """,
        unsafe_allow_html=True,
    )

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

    return meal


def homePage(): # only show once user has walkthrough!
    # Add navigation Bar
    # Source - https://docs.streamlit.io/develop/tutorials/multipage/st.page_link-nav

    userMeal = greeting_Menu()

    # ------------------------------------Aileen's code-------------------------------------------------- #
    # Display notification for favorite dish
    available_favs = check_favorites_available(st.session_state["user_id"])

    if available_favs:
        st.markdown("### 🔔 Favorite Dishes Available Today!")
        for fav in available_favs:
            dish = fav["dish_name"]
            for loc in fav["locations"]:
                st.success(f"**{dish}** available at {loc['location']} ({loc['meal']}) - {loc['station']}")

    userDiningHall = getUserFavDiningHall(user)

    # Prof. Eni function get_params()
    location_id, meal_id = get_params(dfKeys,
                                        userDiningHall,
                                        userMeal)

    d = datetime.date.today()

    df = get_menu(d, location_id, meal_id)

    # We only want today's menu... not the whole week
    # format of date data in df: 2025-04-14T00:00:00
    today = d.strftime("%Y") + "-" + d.strftime("%m") + "-" + d.strftime("%d") + "T00:00:00"

    df = df[df["date"] == today]  # only today's meals

    if df.empty:
        st.warning(f"No menu available for {userMeal} at {userDiningHall} today.")
        return  # Exit early so nothing else runs

    # cleaning up df
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


    # Menu Title and Info.
    st.subheader(userMeal + " Today at " + userDiningHall)

    with st.container(border = True):
        dish, calories, protein, fat, carbs, journal = st.columns(6)

        with dish:
            st.markdown("**Dish**")

        with calories:
            st.write("Calories")

        with protein:
            st.write("Protein")

        with fat:
            st.write("Fat")

        with carbs:
            st.write("Carbs")


        with journal:
             st.write("Add to Journal")

        num = 0

        for index, row in df.iterrows():
            dish, calories, protein, fat, carbs, journal = st.columns(6)
            with dish:
                st.write(row["name"])

            with calories:
                st.write(str(row["calories"]))

            with protein:
                st.write(row["protein"])

            with fat:
                st.write(str(row["fat"]) + "g")

            with carbs:
                st.write(str(row["carbohydrates"]) + "g")

            # with journal:
            #     st.button("Add", key = num)
            #     num += 1

    

#----------------- HOME Page -----------------#
# Show login

init_db()
print("Database initialized.")

render_sidebar()

if "access_token" not in st.session_state:
    st.warning("Please Log In for Access! 🔒")
    st.stop()

# After user logs in, have to call new_user() to see if new user needs walkthrough
check = checkNewUser(user.get("email"))

if check: # if new user, then go through walkthrough
    newUser(user)

homePage()
