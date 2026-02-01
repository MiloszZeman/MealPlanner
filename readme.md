MealPlanner
A desktop

application to simplify your weekly meal planning and grocery shopping.

Table of Contents
Project Description
Tech Stack
Getting Started Locally
Available Scripts
Project Scope
Project Status
License
Project Description
MealPlanner is a desktop application built with Electron, designed for users who want to streamline their meal planning process. The app helps you save time and reduce the stress of figuring out what to eat and what to buy.

The core problem this application solves is the time-consuming nature of planning meals and creating corresponding shopping lists for an entire week. This often leads to last-minute, unplanned trips to the grocery store. MealPlanner provides a simple, intuitive tool to create weekly meal plans and automatically generate an aggregated shopping list, ensuring you have all the necessary ingredients before you start cooking.

The application works completely offline, giving you full control and privacy over your data.

Tech Stack
Frontend: Python + Tkinter
Backend/Database: SQLite
CI/CD: GitHub Actions
Getting Started Locally
To get a local copy up and running, follow these simple steps.

Prerequisites
Python 3.x
pip
Installation
Clone the repository:


git clone https://github.com/your_username/meal-planner.gitcd meal-planner
Create and activate a virtual environment (recommended):


# For Windowspython -m venv venv.\venv\Scripts\activate# For macOS/Linuxpython3 -m venv venvsource venv/bin/activate
Install dependencies:
(Assuming dependencies will be listed in a requirements.txt file)


pip install -r requirements.txt
Running the Application
Execute the main Python script to launch the application:


python main.py
Available Scripts
python main.py: Runs the main application.
python -m unittest discover: Runs the test suite (assuming tests are in a tests directory).
Project Scope
Included in MVP:
User Profile Management: Create multiple local, password-protected user profiles within a single installation.
Recipe Management: Add, edit, and delete your own recipes, including name, meal categories (breakfast, lunch, dinner), and a list of ingredients.
Ingredient Definition: Specify ingredient details, including name, quantity, and predefined units (grams, milliliters, pieces).
Meal Plan Generation: Automatically generate a random 7-day meal plan (3 meals per day) based on your saved recipes.
Plan Editing: Manually modify the generated meal plan by swapping meals with other available recipes from the same category.
Shopping List Generation: Generate a consolidated, alphabetized shopping list based on the active meal plan. The list aggregates the quantities of all required ingredients.
Responsive UI: The application features a simple, intuitive, and responsive interface that adapts to window resizing.
Excluded from MVP:
Nutritional information calculation (calories, macros) or price estimation.
Social features like sharing recipes between accounts.
Progress tracking for meal plans or shopping lists.
Online functionality, cloud synchronization, or data backups.
Advanced application settings (e.g., password changes, themes).
Printing or exporting plans and lists.
Editing the generated shopping list.
Project Status
Status: In Development 🚧

The project is currently in the development phase for the Minimum Viable Product (MVP). The core features are being implemented as defined in the project scope.

License
This project is licensed under the MIT License. See the LICENSE file for more details.