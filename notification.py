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


def add_favorite_dish(user_id, dish_name):
    """Add a favorite dish for a user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute(
            "INSERT INTO user_favorites (user_id, dish_name) VALUES (?, ?)",
            (user_id, dish_name)
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        # Dish already exists as a favorite
        success = False
    
    conn.close()
    return success

def delete_favorite_dish(user_id, dish_name):
    """Delete a favorite dish for a user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute(
        "DELETE FROM user_favorites WHERE user_id = ? AND dish_name = ?",
        (user_id, dish_name)
    )
    
    conn.commit()
    conn.close()
    return True

def get_user_favorite_dishes(user_id):
    """Get all favorite dishes for a user"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute(
        "SELECT dish_name FROM user_favorites WHERE user_id = ?",
        (user_id,)
    )
    
    rows = c.fetchall()
    favorites = [row['dish_name'] for row in rows]
    conn.close()
    
    return favorites

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

def check_favorites_available(user_id):
    """Check if any favorite dishes are available today"""
    
    # Get user's favorite dishes using the context manager
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("SELECT dish_name FROM user_favorites WHERE user_id = ?", (user_id,))
            favorites = [row['dish_name'] for row in c.fetchall()]
        except sqlite3.OperationalError:
            # If there's still an error, return empty list
            favorites = []
    
    # If no favorites, return empty list
    if not favorites:
        return []
    
    # Menu data
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
    
    # Check current menu for favorites
    for info in idInfo:
        try:
            # Get menu for this location/meal
            base_url = "https://dish.avifoodsystems.com/api/menu-items"
            params = {"date": today, "locationID": info["locationID"], "mealID": info["mealID"]}
            response = requests.get(base_url, params=params)
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
        except:
            # Skip this menu if there's an error
            pass
    
    # Convert from defaultdict to list of dishes with their locations
    result = []
    for dish_name, locations in available_dishes.items():
        result.append({
            'dish_name': dish_name,
            'locations': locations
        })
    
    return result