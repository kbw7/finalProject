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

    email = user.get("email") # trying this out instead of accessing var. user from home.py 

    st.title("Welcome " + email[0:5] + "!")

    # go-to dining hall!
    st.write("Select your favorite or go-to dining hall to have on your Home Page and click Submit once you have picked your dining hall!")
    favHall = st.selectbox("Select", ["Tower", "Bates", "Bae", "Stone D"])
    st.write("You Selected " + favHall)


    submitDiningHall = st.button("Submit", key = "diningHall")

    if submitDiningHall:
        # allergens
        if "count" not in st.session_state:
            st.session_state.count = 0

        aviAllergens = ["Peanut", "Soy", "Dairy", "Egg", "Wheat", "Sesame", "Shellfish", "Fish", "Tree Nut", ]

        st.write("Do you have any allergies? (Click the Submit button if you have or have not selected any of the following allergens)")
        titleCols = st.columns(2)
        titleCols[0].write("Allergens")
        titleCols[1].write("Check for Yes")

        if "allergens" not in st.session_state:
            st.session_state["allergens"] = False

        for x in aviAllergens:
            c1, c2 = st.columns(2)
            c1.write(x)
            with c2:
                st.checkbox("", key = f"allergen_{x}")

                
        st.write(st.session_state)

        # if submitAllergens:
        #     if any_allergens_selected():
        #         userAllergens = [x.split("allergen_")[-1] for key in st.session_state if key.startswith("allergen_")]
        #     else:
        #         userAllergens = "None"

    

        #     # Dietary Restrictions
        #     restrictions = ["Vegetarian", "Vegan", "Gluten Sensitive", "Halal", "Kosher", "Lactose-Intolerant"]

        #     st.write("Do you have any dietary restrictions/preferences? (Click the Submit button if you have or have not selected any of the following restrictions/preferences)")

        #     titleCols = st.columns(2)
        #     titleCols[0].write("")
        #     titleCols[1].write("Check for Yes")

        #     for x in restrictions:
        #         c1, c2 = st.columns(2)
        #         c1.write(x)
        #         with c2:
        #             st.checkbox("", key = f"restrict_{x}")

            
        #     submitRestrictions = st.button("Submit", key = "dietaryRestrictions")

        #     if submitRestrictions:
        #         if any_restrictions_selected():
        #             userDietaryRestrictions = [x.split("restrict_")[-1] for key in st.session_state if key.startswith("restrict_")]
        #         else:
        #             userDietaryRestrictions = "None"

        
        #         st.write("You're all set up! Click Next to Get Started with our App")
        #         next = st.button("Next", key = "nextPageHome")

        #         if next:
        #             store_new_user_info(email, favHall, userAllergens, userDietaryRestrictions) 
        #             st.sucess(f"Saved!")

                    # push_db_to_github()
                                 




    

    
        
    