from flask import Flask
from routers.auth import auth_blueprint
from routers.workshops import workshops_blueprint

app = Flask(__name__)

app.register_blueprint(auth_blueprint)
app.register_blueprint(workshops_blueprint)


@app.route('/')
def index():
  return "Hello, world!!!!"

app.run(debug=True, port=5001)
