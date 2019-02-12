"""Models and database functions for recipe project."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Technique(db.Model):
    """Cooking Technique"""

    __tablename__ = "techniques"

    technique_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    technique = db.Column(db.String(30))
    
    def __repr__(self):

        return f"<Technique technique_id={self.technique_id} technique={
                                                            self.technique}>"


class Course(db.Model):
    """Course classification for a recipe"""

    __tablename__ = "courses"

    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course = db.Column(db.String(30))
    
    def __repr__(self):

        return f"<Course course_id={self.course_id} course={self.course}>"


class Timeframe(db.Model):
    """Time required to make recipe"""

    __tablename__ = "timeframes"

    timeframe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    timeframe = db.Column(db.String(30))
    
    def __repr__(self):

        return f"<Timeframe timeframe_id={self.timeframe_id} timeframe={self.timeframe}>"


class Complexity(db.Model):
    """Complexity of recipe"""

    __tablename__ = "complexities"

    complexity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    complexity = db.Column(db.String(20))
    
    def __repr__(self):

        return f"<complexity level ={self.complexity}>"


class Ingredient(db.Model):
    """Ingredient for a recipe"""

    __tablename__ = "ingredients"

    ingredient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    ingredient = db.Column(db.String(30))
    
    def __repr__(self):

        return f"<Ingredient_id={self.ingredient_id} name={self.ingredient}>"


class Pantry(db.Model):
    """Pantry linking users with stable ingredients"""

    __tablename__ = "pantries"

    pantry_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'))
    
    def __repr__(self):

        return f"<Pantry item for user id: {self.user_id}>"


class IngredientPreference(db.Model):
    """Preferences of users for an ingredient"""

    __tablename__ = "ingredient_preferences"

    ingredient_pref_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'))
    ingred_rating = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):

        return f"<Ingredient preference id={self.ingredient_pref_id
                                                } for user id {self.user_id}>"

class Diet(db.Model):
    """Diet Categories"""

    __tablename__ = "diets"

    diet_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    diet = db.Column(db.String(30))
    
    def __repr__(self):

        return f"<Diet_id={self.diet_id} diet={self.diet}>"


class DietPreference(db.Model):
    """Dietary restrictions/preferences of a user"""

    __tablename__ = "diet_preferences"

    diet_pref_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    diet_id = db.Column(db.Integer, db.ForeignKey('diets.diet_id'))
    strictness = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):

        return f"<Dietary Preference id={self.diet_pref_id
                                        } for user id: {self.user_id}>"


class Cuisine(db.Model):
    """Cuisine types"""

    __tablename__ = "cuisines"

    cuisine_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    cuisine = db.Column(db.String(50))
    
    def __repr__(self):

        return f"<Cuisine cuisine_id={self.cuisine_id} name={self.cuisine}>"


class CuisinePreference(db.Model):
    """Cuisine preference for user"""

    __tablename__ = "cuisine_preferences"

    cuisine_pref_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    cuisine_id = db.Column(db.Integer, db.ForeignKey('cuisines.cuisine_id'))
    cuisine_rating = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):

        return f"<Cuisine preference id={self.cuisine_pref_id
                                            } for user id: {self.user_id}>"


class User(db.Model):
    """User of recipe website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(64), nullable=True)

    rating = db.relationship("Rating")
    

    def __repr__(self):

        return f"<User user_id={self.user_id} email={self.email}>"


class Rating(db.Model):
    """Rating of recipe website."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer)

    # Define relationships to user
    user = db.relationship("User")

    def __repr__(self):

        return f"<Rating rating_id={self.rating_id} recipe_id={self.recipe_id}>"


class SavedRecipe(db.Model):
    """Saved recipe"""

    __tablename__ = "saved_recipes"

    record_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    recipe_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __repr__(self):

        return f"<Rating rating_id={self.rating_id}>"


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///recipe'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def predict_user_rating(title, user_id):

    m = Movie.query.filter_by(title=title).one()
    u = User.query.get(user_id)

    recipe = u.recipe

    other_recipe = Rating.query.filter_by(movie_id=m.movie_id).all()
    other_users = [r.user for r in other_recipe]

    users_w_commonality = []

    for rating in recipe:
        # print("********Movie********", rating.movie.title)
        movie_id = rating.movie_id
        # print("********movie_id******", movie_id)
        common_recipe = Rating.query.filter(Rating.movie_id==movie_id).all()
        users = [r.user for r in common_recipe]
        # print("********common_recipe*******", common_recipe)
        users_w_commonality.extend(users)

    unique_users = set(users_w_commonality)
    return unique_users

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")