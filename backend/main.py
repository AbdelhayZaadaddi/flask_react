from flask import Flask
from flask_restx import Api, Resource
from config import DevConfig


app = Flask(__name__)
app.config.from_object(DevConfig)
api = Api(app, doc='/doc')

@api.route('/hello')
class HelloResource(Resource):
    def get(self):
        return {"message":"hello world"}
    

if __name__ == '__main__':
    app.run()