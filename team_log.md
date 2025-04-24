# Team Log 📝
## Details Final Project Progress and Team Contributions
**By Aileen, Rebecca, and Kaurvaki**

**`April 2nd`**

Aileen, Rebecca, and Kaurvaki all got together to meet up at the Science Center on Wednesday evening to work on Milestone 1. Aileen and Kaurvaki were at Crystal's office hours and reviewed Assignment 5 code to see what we had in common. Rebecca had class but met up with us once her class was over. We all worked together at one table with our laptops where we used Kaurvaki's laptop for the main coding. Everyone sat around Kaurvaki's laptop and we walked through our plan of how we would use our Assignment 5 code and Streamlit app planning to create our Wellesley Fresh Menu application. We brainstormed the layout of the app and decided to use st.form(). We really liked the calendar feature that ChatGPT came up with so we decided to use that code along with how to format it to have hyphen format. Once we added our Streamlit code, we customized our Streamlit app and learned more about config.toml. Then, we deployed the app and finished!
Everyone contributed equally and were involved in this milestone!


**`April 9th`**

**Kaurvaki** - For our app design, I worked on the user login and home dashboard pages in Canva and wrote about them in our Google Slides presentation.

**Aileen** - For the prototype, I worked on the food journal and the setting page, and wrote about how our ideas and designs for these pages connect to the Value Sensitive Design and Data Feminism.

**Rebecca** - For our prototype on canva, I worked on the data visualizations, community forums, and menu page and connected our design choices to VSD and data feminism in our presentation.

**Whole Team** - We met up virtually on Tuesday (April 8) to go over Milestone 2 and started planning what kind of app we wanted and brainstormed features. We met up again in-person on Wednesday (April 9) at Crystal's office hours (Aileen and I, Rebecca joined after her class) and continued working on designing the app on Canva and working on our Google Slides presentation. We finalized details like app name, color scheme, formatting, etc. Then, we worked on our team contract on a shared Google Doc. Finally, we worked on the ER diagramming using Draw.io and the whiteboards at the Science Center! We all met up today (right now as I'm writing) to wrap up our presentation and write this team log. Through our meetings, we made a lot of progress and worked efficiently together.

**`April 17th`**

**Aileen** - I worked on setting up the SQLite database and connected it to the food journal logging system. I also implemented the backend logic so that meal entries are saved and correctly displayed through the journal page.

**Kaurvaki** - I worked on the Home Page where I reviewed the User Authentication code that Professor Eni provided and added all of that into our app. Then, I worked on the greeting for our app that would change based on time of day and since I am still figuring out how to do user preferences linked to account, I added a selectbox for users to pick their "go-to" or favorite dining hall (temporary) and as a result, the menu for that time of day of that dining hall would appear... for example, if it was 1 PM, the app would say "Good Afternoon" and after selecting "Bates" you would see the Bates lunch menu for today. I also figured out how to link the food journal and menu pages to the home page by looking at online sources. Since we don't want users to be able to access the journal page unless they log in, I made the page inaccessible unless the user logged in (and added warnings at the top of the page for them to log in to see the page).

**Rebecca** - I worked on the menu page which showed breakfast, lunch, and dinner all on one page and and implemented the USDA FoodData API for searching for custom ingredients. I also worked on a few visualizations.

**Whole Team** - We met up online on Monday to go over Milestone 3 and delegate tasks. Tuesday, we met up again to give progress reports and further delegate work if people needed help or decided they wanted to do more. Thursday, our group met up to go over our work and then add their respective work to the main app files. Rebecca and Aileen had to leave early for work so Kaurvaki linked home page with the other pages and finished up remaining tasks. This week was pretty busy for all of us and we did not spend as much time as we wanted on this week's milestone. Kaurvaki was busy with Ruhlman this week. Rebecca had ongoing rehearsals and was not feeling well. Aileen and Kaurvaki both had golf as well. We hope to continue working and adding more features for our app!

**`April 24th`**

**Aileen** - This week I worked mainly on the notification function. I wrote all the related functions like add_favorite_dish and delete_favorite_dish in notification.py and then import them in settings.py to make the code clean. The notification system was designed to cross-reference the user's preferred dishes from their profile with the daily menus retrieved from the AVI Fresh API. To complete this functionality, I wrote conditional logic that checks current day's each menu item against the user's favorites list before generating relevant alerts. I also tried to link the add button from the homepage, but the code was very buggy and after working with Kauvaki on Thursday, we decided to delete this quick log function from the home page for now.

**Kaurvaki**

**Rebecca** - This week I worked on refining the menu page to match what it looks like on the home page and making the metrics page. For the metrics page, I went through streamlit app demos online and took inspiration from their graphs. Because our database is currently empty, I also asked chatgpt to generate a fake data to demo what the visualizations could look like. I also found a resource online that had information about transition graphs using the retentioneering library, which I found cool and tried very hard to make work but it ultimately wouldn't work with my version of python. I really wanted the functionality of transition graphs but could not figure out how to do it using plotly, so I asked chatgpt to guide me through how it worked. Our review of session state during class was especially helpful when implementing buttons to toggle between visualizations.

**Whole Team**
