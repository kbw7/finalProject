import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

def transform(cell):
    """Convert list of dictionaries to comma-separated string."""
    result = ""
    if cell:
        result = ",".join([item["name"] for item in cell])
    return result

def dropKeys(cell):
    """Remove unnecessary keys from nutritional data."""
    cell.pop("id", None)
    cell.pop("corporateProductId", None)
    cell.pop("caloriesFromSatFat", None)
    return cell

def get_menu_for_day():
    """Get all menus for all dining halls for today."""
    today = datetime.now().date()
    formatted_date = today.strftime("%m-%d-%Y")
    
    # Location and meal IDs from the original code
    id_info = [
        {"location": "Bae", "meal" : "Breakfast", "locationID" : "96", "mealID" : "148"},
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
    
    all_menus = []
    
    for item in id_info:
        location_id = item["locationID"]
        meal_id = item["mealID"]
        location = item["location"]
        meal = item["meal"]
        
        base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
        params = {"date": formatted_date, "locationId": location_id, "mealId": meal_id}
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            
            # Process and clean the data
            df = pd.DataFrame(data)
            
            # Only keep today's menu
            today_str = today.strftime("%Y-%m-%d") + "T00:00:00"
            df = df[df["date"] == today_str]
            
            if not df.empty:
                # Clean the data
                df = df.drop_duplicates(subset=["id"], keep="first")
                df = df.drop(columns=["date", "image", "id", "categoryName", "stationOrder", "price"], errors="ignore")
                
                df["allergens"] = df["allergens"].apply(transform)
                df["preferences"] = df["preferences"].apply(transform)
                df["nutritionals"] = df["nutritionals"].apply(dropKeys)
                
                # Add location and meal information
                df["dining_hall"] = location
                df["meal_type"] = meal
                
                # Convert to records format for easier processing
                menu_items = df.to_dict(orient="records")
                all_menus.extend(menu_items)
        
        except requests.RequestException as e:
            st.error(f"Error fetching menu for {location} {meal}: {e}")
            continue
    
    return all_menus

def load_favorite_dishes():
    """
    Load user's favorite dishes from the database or settings.
    For now, we'll hard-code some favorites.
    """
    # This would normally come from a database or user settings
    return [
        "Pizza",
        "Mac and Cheese",
        "Caesar Salad",
        "Chocolate Chip Cookies"
    ]

def get_time_greeting():
    """Return a greeting based on the current time."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"

def check_favorites_and_notify():
    """
    Check if any of the user's favorite dishes are on today's menu
    and generate notifications.
    """
    all_menus = get_menu_for_day()
    favorite_dishes = load_favorite_dishes()
    
    # Store matched favorites for notification
    matches = []
    
    for item in all_menus:
        dish_name = item.get("name", "")
        
        # Check if any favorite is in the dish name (case-insensitive partial match)
        for favorite in favorite_dishes:
            if favorite.lower() in dish_name.lower():
                matches.append({
                    "dish": dish_name,
                    "dining_hall": item["dining_hall"],
                    "meal": item["meal_type"]
                })
    
    return matches

def display_favorite_dish_notifications():
    """Display notifications for favorite dishes in the Streamlit app."""
    st.title(f"{get_time_greeting()} 👋")
    
    matches = check_favorites_and_notify()
    
    if matches:
        st.subheader("🎉 Good news! Your favorite dishes are available today:")
        
        for match in matches:
            with st.container(border=True):
                st.markdown(f"**{match['dish']}** is available for **{match['meal']}** at **{match['dining_hall']}**")
    else:
        st.info("None of your favorite dishes are on the menu today. Check back tomorrow!")
    
    # Display all favorite dishes
    with st.expander("Your Favorite Dishes"):
        favorites = load_favorite_dishes()
        for favorite in favorites:
            st.write(f"• {favorite}")
        
        st.write("You can add more favorites in the Settings page.")

def settings_page():
    """A simple settings page to manage favorite dishes."""
    st.title("Settings")
    st.subheader("Manage Your Favorite Dishes")
    
    favorites = load_favorite_dishes()
    
    # Display current favorites
    st.write("Your current favorite dishes:")
    for i, favorite in enumerate(favorites):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{i+1}. {favorite}")
        with col2:
            # In a real app, this button would remove the dish
            st.button("Remove", key=f"remove_{i}", disabled=True)
    
    # Add new favorite
    st.subheader("Add a New Favorite")
    new_favorite = st.text_input("Dish name")
    if st.button("Add Favorite") and new_favorite:
        st.success(f"Added {new_favorite} to favorites!")
        st.info("Note: In a complete app, this would be saved to the database.")

def main():
    """Main function to run the Streamlit app."""
    # Add a sidebar for navigation
    page = st.sidebar.radio("Navigation", ["Home", "Settings"])
    
    if page == "Home":
        display_favorite_dish_notifications()
    else:
        settings_page()

if __name__ == "__main__":
    main()