import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt

# Sample data
daily_macros = pd.DataFrame({
    'nutrient': ['Protein', 'Carbs', 'Fat'],
    'grams': [65, 220, 55]
})

# Pie chart showing macronutrient distribution
st.subheader("Today's Macronutrient Balance")
fig = alt.Chart(daily_macros).mark_arc().encode(
    theta=alt.Theta(field="grams", type="quantitative"),
    color=alt.Color(field="nutrient", type="nominal", 
                   scale=alt.Scale(range=["#5B8C5A", "#6B9AC4", "#D4A373"])),
    tooltip=['nutrient', 'grams']
).properties(width=300, height=300)
st.altair_chart(fig, use_container_width=True)

# Sample data for 7 days
dates = pd.date_range(start="2023-04-01", periods=7)
weekly_data = pd.DataFrame({
    'date': dates,
    'protein': [65, 40, 55, 85, 90, 52, 65],
    'carbs': [255, 210, 225, 205, 240, 235, 195],
    'fat': [35, 52, 55, 40, 55, 80, 50]
})

# Format the dates properly
weekly_data['formatted_date'] = weekly_data['date'].dt.strftime('%a %d')  # Abbreviated weekday and day

st.subheader("Weekly Nutrition Trends")
weekly_data_melted = pd.melt(weekly_data, id_vars=['date', 'formatted_date'], 
                            value_vars=['protein', 'carbs', 'fat'],
                            var_name='nutrient', value_name='grams')

chart = alt.Chart(weekly_data_melted).mark_line(point=True).encode(
    x=alt.X('formatted_date:N', title='Date', sort=None, 
           axis=alt.Axis(labelAngle=0)),  # Set label angle to 0 for horizontal labels
    y=alt.Y('grams:Q', title='grams'),
    color=alt.Color('nutrient:N', 
                   scale=alt.Scale(range=["#D4A373", "#5B8C5A", "#6B9AC4"])),  # Protein, Carbs, Fat
    tooltip=['formatted_date', 'nutrient', 'grams']
).properties(
    height=300,
    background='#e8f0da'  # Light green background matching your example
)

st.altair_chart(chart, use_container_width=True)

dining_data = pd.DataFrame({
    'dining_hall': ['Bates', 'Tower', 'Stone-Davis', 'Bao'],
    'visits': [14, 8, 5, 3]
})

st.subheader("Your Dining Hall Visits This Month")
chart = alt.Chart(dining_data).mark_bar().encode(
    x=alt.X('dining_hall:N', sort='-y'),
    y='visits:Q',
    color=alt.Color('dining_hall:N', 
                   scale=alt.Scale(range=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])),
    tooltip=['dining_hall', 'visits']
).properties(height=300)
st.altair_chart(chart, use_container_width=True)

forum_data = pd.DataFrame({
    'forum': ['Plant-Based Eating', 'Cultural Recipes', 'Allergy Support', 'Meal Prep Tips', 'Sustainability'],
    'posts': [42, 28, 35, 18, 23],
    'members': [120, 85, 95, 60, 70]
})

st.subheader("Community Forum Activity")
chart = alt.Chart(forum_data).mark_bar().encode(
    y=alt.Y('forum:N', sort='-x'),
    x='posts:Q',
    color=alt.Color('forum:N'),
    tooltip=['forum', 'posts', 'members']
).properties(height=300)
st.altair_chart(chart, use_container_width=True)

# Generate sample data
dates = pd.date_range(start='2023-04-01', end='2023-04-30')
meal_counts = np.random.randint(0, 4, size=len(dates))  # 0-3 meals logged per day
data = pd.DataFrame({'date': dates, 'meals_logged': meal_counts})

# Extract components for the calendar view
data['day'] = data['date'].dt.day
data['week'] = data['date'].dt.isocalendar().week - data['date'].dt.isocalendar().week.min()
data['month'] = data['date'].dt.month
data['weekday'] = data['date'].dt.weekday

st.subheader("Meal Logging Calendar - April 2023")
# Create the heatmap
heatmap = alt.Chart(data).mark_rect().encode(
    x='day:O',
    y='weekday:O',
    color=alt.Color('meals_logged:Q', scale=alt.Scale(scheme='blues')),
    tooltip=['date', 'meals_logged']
).properties(width=600)

# Add text labels for the weekdays
weekday_labels = alt.Chart(pd.DataFrame({
    'weekday': range(7),
    'label': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
})).mark_text(align='right').encode(
    y='weekday:O',
    text='label'
).properties(width=600)

st.altair_chart(heatmap, use_container_width=True)