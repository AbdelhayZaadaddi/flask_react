from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from config import DevConfig
from models import Recipe, User
from exts import db
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(DevConfig)
db.init_app(app)
migrate = Migrate(app, db)
JWTManager(app)

api = Api(app, doc='/docs')

#model {serializer}
recipe_model = api.model(
    "Recipe",
    {
        "id":fields.Integer(),
        "title":fields.String(),
        "description":fields.String()
    }
)

signup_model = api.model(
    "Signup",
    {
        "id":fields.Integer(),
        "username":fields.String(),
        "email":fields.String(),
        "password":fields.String()
    }
)

login_model = api.model(
    "Login",
    {
        "username":fields.String(),
        "password":fields.String()
    }
)

@api.route('/hello')
class HelloResource(Resource):
    @api.marshal_list_with(recipe_model)
    def get(self):
        recipes = Recipe.query.all()

        return recipes
    
@api.route('/signup')
class SignUp(Resource):
    @api.expect(signup_model)
    def post(self):
        data = request.get_json()

        username = data.get('username')
        email = data.get('email')
        db_user = User.query.filter_by(username = username).first()
        db_user_email = User.query.filter_by(email = email).first()
        if db_user is not None or db_user_email is not None:
            return jsonify ({"message":f"User with username {username} already exists or email {email} already exists"})

        new_user = User(
            username = data.get('username'),
            email = data.get('email'),
            password = generate_password_hash(data.get('password'))
        )

        new_user.save()

        return jsonify({"messages":"User created successfully"})

@api.route('/login')
class Login(Resource):

    @api.expect(login_model)
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        db_user = User.query.filter_by(username=username).first()

        if db_user and check_password_hash(db_user.password, password):
            # i stoped here
            pass



@api.route('/recipes')
class RecipesResource(Resource):
    @api.marshal_list_with(recipe_model)
    def get(self):
        """ Get all recipes"""

        recipes = Recipe.query.all()

        return recipes

    @api.marshal_with(recipe_model)
    @api.expect(recipe_model)
    def post(self):
        """Create a new recipe"""
        data = request.get_json()

        new_recipe = Recipe(
            title = data.get('title'),
            description = data.get('description')
        )

        new_recipe.save()

        return new_recipe, 201

@api.route("/recipe/<int:id>")
class RecipeResource(Resource):

    @api.marshal_with(recipe_model)
    def get(self, id):
        """Get a recipe by id"""
        recipe = Recipe.query.get_or_404(id)

        return recipe
    
    @api.marshal_with(recipe_model)
    def put(self, id):
        """Update a recipe by id"""
        recipe_to_update = Recipe.query.get_or_404(id)
        data = request.get_json()

        # Retrieve 'title' and 'description' from the request data
        title = data.get('title')
        description = data.get('description')

        # Check if title and description are provided
        if title is not None and description is not None:
            # Update the recipe
            recipe_to_update.update(title, description)
            return recipe_to_update, 200
        else:
            return {"message": "Both title and description are required"}, 400
        
    @api.marshal_with(recipe_model)
    def delete(self, id):
        """Delete a recipe by id"""

        recipe_to_delete = Recipe.query.get_or_404(id)

        recipe_to_delete.delete()
        
        return recipe_to_delete, 200


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'Recipe': Recipe
    }

if __name__ == '__main__':
    app.run()