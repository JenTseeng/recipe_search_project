from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
import os
from resources import recipeProcessing, userInteraction
from model import *
from flask import Flask, render_template, request, flash, redirect, session

app = Flask(__name__)
app.secret_key = "ABC"

# Jinja to raise errors for undefined vars
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


@app.route("/registration")
def new_user():
    """Show registration form"""

    return render_template("registration.html")


@app.route("/confirm_registration", methods=['POST'])
def add_user():
    """Add new user."""

    email_to_check = request.form.get('email')
    pw = request.form.get('pw')

    # Redirect and request different login in email unavailable
    if User.query.filter(User.email==email_to_check).first():
        flash("User already exists. Please enter a different email or login.")
        return redirect("/registration")

    # add user to db
    else:
        user = User(email=email_to_check, password=pw)
        db.session.add(user)
        db.session.commit()

        flash("Successfully registered!")
        return redirect("/")


@app.route('/login')
def login():
    """Login page"""
    
    return render_template("login.html")


@app.route('/check_login', methods = ["POST"])
def check_login():
    """Check credentials"""

    email_to_check = request.form.get('email')
    pw = request.form.get('pw')
    user = User.query.filter(User.email==email_to_check, User.password==pw).first()

    # log in user with valid credentials
    if user:
        session['user_id'] = user.user_id
        flash("You are now logged in!")
        return redirect("/users/{}".format(user.user_id))

    # alert for incorrect credentials
    else:
        flash("Credentials incorrect. Please try again.")
        return redirect("/login") 


@app.route('/users/<user_id>')
def show_user_details(user_id):
    """User detail page"""

    user = User.query.get(int(user_id))
    return render_template("user_info.html", user=user)


@app.route('/select_diets')
def show_diet_selection_page():
    """Dietary option selection page"""

    diets = DietType.query.all()

    return render_template("diet_selection.html", diets = diets)


@app.route('/update_diet', methods=['POST'])
def update_diet_preferences():
    """Update diet preferences based on user input"""

    diets = request.form.getlist('diets')
    user_id = session['user_id']
    userInteraction.update_diet_preference(user_id, diets)

    flash("Diet preferences updated")
    return redirect("/users/{}".format(user_id))


@app.route('/logout')
def logout():
    """Logout page"""

    del session['user_id']
    flash("You are now logged out!")
    return redirect("/")


@app.route("/recipe_search")
def show_recipe_search_form():
    """Show recipe search form"""

    return render_template("recipe_search.html")


@app.route("/ingredient_search")
def show_ingred_search_form():
    """Show ingredient search form"""
    # TODO: create DB with units of UI and add loop in Jinja

    return render_template("ingredient_search.html")


@app.route("/standard_results", methods=['GET'])
def find_recipes():
    """Search for recipes with keywords"""

    query = request.args.get('search_field')
    num_recipes = 5
    excluded = None

    diet, health = userInteraction.set_diet_info(session)
    recipes = recipeProcessing.get_recipes(query, diet, health, num_recipes, 
                                        excluded)

    return render_template("search_results.html", recipes=recipes)


@app.route("/ingredient_results", methods=['GET'])
def find_recipes_with_ingred_limits():
    """Recipe Search with ingredient qty checks"""

    # check for API calls remaining
    requests_left = requestTracking.check_api_call_budget()
    diet, health = userInteraction.set_diet_info(session)
    excluded = None

    if requests_left:
        query = request.args.get('search_field')
        min_amt = request.args.get('min_qty')
        max_amt = request.args.get('max_qty')
        unit = request.args.get('unit')

        recipes = get_recipes_with_ingred_limit(query, min_amt, max_amt, unit, diet, 
                                            health, excluded)

        return render_template("search_results.html", recipes=recipes)

    else:
        flash("No API calls remaining, perhaps try a regular recipe request")
        redirect("/standard_results")


######################## Trials with APIs ###########################

# url= 'https://api.edamam.com/api/nutrition-data'
# payload = {'app_id':app.ingred_id, 'app_key':app.ingred_key,'ingr':'1 cup flour'}
# response = requests.get(url, params=payload)

# response = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/", headers={"X-RapidAPI-Key": "0259f0d9e1msha4cc9f28bb5ed5ep1deaf8jsn6ff56d1c04da"})
# response = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/food/jokes/random",headers={"X-RapidAPI-Key": "0259f0d9e1msha4cc9f28bb5ed5ep1deaf8jsn6ff56d1c04da"})
# response = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/cuisine",headers={"X-RapidAPI-Key": "0259f0d9e1msha4cc9f28bb5ed5ep1deaf8jsn6ff56d1c04da"})


if __name__ == "__main__":
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)
    DebugToolbarExtension(app)
    
    app.run(host="0.0.0.0")
    