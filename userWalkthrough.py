import streamlit as st
import sqlite3
from update_database import store_new_user_info
from db_sync import push_db_to_github


def any_allergens_selected(): # Source - Prof. Eni code
    # Sees if user selected any allergens
    return any(key.startswith("allergen_") and value is True
               for key, value in st.session_state.items()
    )

def any_restrictions_selected(): # Source - Prof. Eni code
    # Sees if user selected any allergens
    return any(key.startswith("restrict_") and value is True
               for key, value in st.session_state.items()
    )

# new user function
def newUser(user):
    if "access_token" not in st.session_state:
        st.warning("Please Log In for Access! 🔒")
        st.stop()

    email = user.get("email")
    st.title("Welcome " + email[0:5] + "!")

    # Favorite dining hall selection
    st.write("Select your favorite or go-to dining hall to have on your Home Page and click Submit once you have picked your dining hall!")
    favHall = st.selectbox("Select", ["Tower", "Bates", "Bae", "Stone D"])
    st.write("You Selected " + favHall)

    # Save dining hall when user clicks this
    if "dining_submitted" not in st.session_state:
        st.session_state["dining_submitted"] = False
    if st.button("Submit Dining Hall"):
        st.session_state["dining_submitted"] = True

    # Allergen Section (always rendered!)
    if st.session_state["dining_submitted"]:
        st.subheader("Allergy Information")
        st.write("Are you allergic to any of the following?")

        aviAllergens = ["Peanut", "Soy", "Dairy", "Egg", "Wheat", "Sesame", "Shellfish", "Fish", "Tree Nut"]

        titleCols = st.columns(2)
        titleCols[0].write("Allergen")
        titleCols[1].write("Check if Yes")

        for allergen in aviAllergens:
            c1, c2 = st.columns(2)
            c1.write(allergen)
            with c2:
                st.checkbox("", key=f"allerg_{allergen}")

        if "allergen_submitted" not in st.session_state:
            st.session_state["allergen_submitted"] = False

        if st.button("Submit Allergens"):
            st.session_state["allergen_submitted"] = True

        if st.session_state["allergen_submitted"]:
            userAllergens = [
                key.split("allerg_")[-1]
                for key in st.session_state
                if key.startswith("allerg_") and st.session_state[key]
            ]
            st.success(f"✅ You selected: {', '.join(userAllergens) if userAllergens else 'None'}")

    

        # Dietary Restrictions
        restrictions = ["Vegetarian", "Vegan", "Gluten Sensitive", "Halal", "Kosher", "Lactose-Intolerant"]

        st.write("Do you have any dietary restrictions/preferences? (Click the Submit button if you have or have not selected any of the following restrictions/preferences)")

        titleCols = st.columns(2)
        titleCols[0].write("")
        titleCols[1].write("Check for Yes")

        for x in restrictions:
            c1, c2 = st.columns(2)
            c1.write(x)
            with c2:
                st.checkbox("", key = f"restrict_{x}")

        if "restriction_submitted" not in st.session_state:
            st.session_state["restriction_submitted"] = False

        if st.button("Submit Dietary Restrictions/Preferences"):
            st.session_state["restriction_submitted"] = True

        if st.session_state["restriction_submitted"]:
            userDietaryRestrictions = [
                key.split("restrict_")[-1]
                for key in st.session_state
                if key.startswith("restrict_") and st.session_state[key]
            ]
            st.success(f"✅ You selected: {', '.join(userDietaryRestrictions) if userDietaryRestrictions else 'None'}")
            

            st.write("You're all set up! Click Next to Get Started with our App")

            next = st.button("Next", key = "nextPageHome")

            if next:
                store_new_user_info(email, favHall, str(userAllergens), str(userDietaryRestrictions)) 
                st.success(f"Saved!")

                push_db_to_github()
                                 




    

    
        
    