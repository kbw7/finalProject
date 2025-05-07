import streamlit as st
import pandas as pd
import sqlite3
import requests
from datetime import datetime
from collections import defaultdict
from contextlib import contextmanager

from db_sync import get_db_path
DB_PATH = get_db_path()

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def add_favorite_dish(email, dish_name):
    """Add a favorite dish to the user's favorites column."""
    favorites = get_user_favorite_dishes(email)
    if dish_name in favorites:
        return False  # Already exists

    favorites.append(dish_name)
    new_fav_str = ",".join(favorites)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET favorites = ? WHERE email = ?", (new_fav_str, email))
    conn.commit()
    conn.close()
    return True

def delete_favorite_dish(email, dish_name):
    favorites = get_user_favorite_dishes(email)
    if dish_name not in favorites:
        return False

    favorites.remove(dish_name)
    new_fav_str = ",".join(favorites)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET favorites = ? WHERE email = ?", (new_fav_str, email))
    conn.commit()
    conn.close()
    return True

def get_user_favorite_dishes(email):
    """Fetch favorite dishes from the users table (new format)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT favorites FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()

    if row and row[0]:
        return row[0].split(",")  # Assumes comma-separated string
    return []

def get_menu_items(date, location_ids, meal_ids):
    """Get menu items for specified date, locations, and meals"""
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
    all_menu_items = []
    
    # Process each location and meal combination
    for location_id in location_ids:
        for meal_id in meal_ids:
            params = {
                "date": date,
                "locationId": location_id,
                "mealId": meal_id
            }
            
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                menu_items = response.json()
                
                # Add the location ID and meal ID to each item for reference
                for item in menu_items:
                    item['locationId'] = location_id
                    item['mealId'] = meal_id
                
                all_menu_items.extend(menu_items)
            except requests.RequestException as e:
                st.error(f"Error fetching menu: {e}")
    
    return all_menu_items

def check_favorites_available(user_email):
    """Check if any favorite dishes are available today without relying on get_all_menus_for_week"""
    try:
        # Get user's favorite dishes
        favorites = get_user_favorite_dishes(user_email)
        
        # If no favorites, return empty list
        if not favorites:
            return []
        
        # Menu data - all dining halls and meal options
        idInfo = [
            {"location": "Bae", "meal": "Breakfast", "locationID": 96, "mealID": 148},
            {"location": "Bae", "meal": "Lunch", "locationID": 96, "mealID": 149},
            {"location": "Bae", "meal": "Dinner", "locationID": 96, "mealID": 312},
            {"location": "Bates", "meal": "Breakfast", "locationID": 95, "mealID": 145},
            {"location": "Bates", "meal": "Lunch", "locationID": 95, "mealID": 146},
            {"location": "Bates", "meal": "Dinner", "locationID": 95, "mealID": 311},
            {"location": "Stone D", "meal": "Breakfast", "locationID": 131, "mealID": 261},
            {"location": "Stone D", "meal": "Lunch", "locationID": 131, "mealID": 262},
            {"location": "Stone D", "meal": "Dinner", "locationID": 131, "mealID": 263},
            {"location": "Tower", "meal": "Breakfast", "locationID": 97, "mealID": 153},
            {"location": "Tower", "meal": "Lunch", "locationID": 97, "mealID": 154},
            {"location": "Tower", "meal": "Dinner", "locationID": 97, "mealID": 310}
        ]
        
        # Today's date
        today = datetime.now().date().strftime("%m-%d-%Y")
        
        # Store available favorites - use a dictionary to group by dish name
        available_dishes = defaultdict(list)
        
        # Check each dining hall and meal combination
        for info in idInfo:
            try:
                # Direct API call for today's menu
                base_url = "https://dish.avifoodsystems.com/api/menu-items"
                params = {
                    "date": today, 
                    "locationID": info["locationID"], 
                    "mealID": info["mealID"]
                }
                
                response = requests.get(base_url, params=params, timeout=10)
                menu_items = response.json()
                
                # Check each menu item against favorites
                for item in menu_items:
                    item_name = item.get('name', '').lower()
                    
                    # Check if any favorite matches this menu item
                    for fav in favorites:
                        if fav.lower() in item_name or item_name in fav.lower():
                            # Add this location/meal to the dish
                            dish_info = {
                                'location': info["location"],
                                'meal': info["meal"],
                                'station': item.get('stationName', '')
                            }
                            # Use the menu item name as the key
                            available_dishes[item.get('name')].append(dish_info)
            except Exception as e:
                # Skip this dining hall/meal if there's an error, but print for debugging
                print(f"Error fetching menu for {info['location']} {info['meal']}: {e}")
                continue
        
        # Convert from defaultdict to list of dishes with their locations
        result = []
        for dish_name, locations in available_dishes.items():
            result.append({
                'dish_name': dish_name,
                'locations': locations
            })
        
        # For debugging
        print(f"Found {len(result)} favorite dishes available")
        
        return result
    
    except Exception as e:
        # Catch any unexpected errors
        print(f"Unexpected error in check_favorites_available: {e}")
        import traceback
        print(traceback.format_exc())
        return []

@st.cache_data(ttl=3600)
def get_all_menus_for_week(days=7):
    """Fetch all menu items from the past `days` days across all dining halls."""
    idInfo = [
        {"location": "Bae", "meal": "Breakfast", "locationID": 96, "mealID": 148},
        {"location": "Bae", "meal": "Lunch", "locationID": 96, "mealID": 149},
        {"location": "Bae", "meal": "Dinner", "locationID": 96, "mealID": 312},
        {"location": "Bates", "meal": "Breakfast", "locationID": 95, "mealID": 145},
        {"location": "Bates", "meal": "Lunch", "locationID": 95, "mealID": 146},
        {"location": "Bates", "meal": "Dinner", "locationID": 95, "mealID": 311},
        {"location": "Stone D", "meal": "Breakfast", "locationID": 131, "mealID": 261},
        {"location": "Stone D", "meal": "Lunch", "locationID": 131, "mealID": 262},
        {"location": "Stone D", "meal": "Dinner", "locationID": 131, "mealID": 263},
        {"location": "Tower", "meal": "Breakfast", "locationID": 97, "mealID": 153},
        {"location": "Tower", "meal": "Lunch", "locationID": 97, "mealID": 154},
        {"location": "Tower", "meal": "Dinner", "locationID": 97, "mealID": 310}
    ]

    all_items = []

    for delta in range(days):
        date_str = (datetime.now() - pd.Timedelta(days=delta)).strftime("%m-%d-%Y")
        for info in idInfo:
            try:
                r = requests.get(
                    "https://dish.avifoodsystems.com/api/menu-items",
                    params={"date": date_str, "locationID": info["locationID"], "mealID": info["mealID"]}
                )
                menu_items = r.json()
                for item in menu_items:
                    item['location'] = info["location"]
                    item['meal'] = info["meal"]
                    item['date'] = date_str
                    all_items.append(item)
            except:
                continue

    return all_items