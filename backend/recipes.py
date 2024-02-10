from flask import request
from flask_restx import Namespace, Resource, fields
from models import Recipe
from flask_jwt_extended import jwt_required



recipe_ns = Namespace('recipe', description="A namespace for Reacipes")

#model {serializer}
recipe_model = recipe_ns.model(
    "Recipe",
    {
        "id":fields.Integer(),
        "title":fields.String(),
        "description":fields.String()
    }
)



@recipe_ns.route('/hello')
class HelloResource(Resource):
    @recipe_ns.marshal_list_with(recipe_model)
    def get(self):
        recipes = Recipe.query.all()

        return recipes





@recipe_ns.route('/recipes')
class RecipesResource(Resource):
    @recipe_ns.marshal_list_with(recipe_model)
    def get(self):
        """ Get all recipes"""

        recipes = Recipe.query.all()

        return recipes

    @recipe_ns.marshal_with(recipe_model)
    @recipe_ns.expect(recipe_model)
    @jwt_required()
    def post(self):
        """Create a new recipe"""
        data = request.get_json()

        new_recipe = Recipe(
            title = data.get('title'),
            description = data.get('description')
        )

        new_recipe.save()

        return new_recipe, 201




@recipe_ns.route("/recipe/<int:id>")
class RecipeResource(Resource):

    @recipe_ns.marshal_with(recipe_model)
    def get(self, id):
        """Get a recipe by id"""
        recipe = Recipe.query.get_or_404(id)

        return recipe
    
    @recipe_ns.marshal_with(recipe_model)
    @jwt_required()
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
        
    @recipe_ns.marshal_with(recipe_model)
    @jwt_required()
    def delete(self, id):
        """Delete a recipe by id"""

        recipe_to_delete = Recipe.query.get_or_404(id)

        recipe_to_delete.delete()
        
        return recipe_to_delete, 200