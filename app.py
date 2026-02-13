from flask import Flask
from routers.auth import auth_blueprint
from routers.workshops import workshops_blueprint
from routers.users import users_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
     r"/*": {"origins": ["http://localhost:5173", "https://art-live.netlify.app"]}}, supports_credentials=True)

app.register_blueprint(auth_blueprint)
app.register_blueprint(workshops_blueprint)
app.register_blueprint(users_blueprint)


@app.route('/')
def index():
  return "Hello, world!!!!"

if __name__ == '__main__':
  app.run()
