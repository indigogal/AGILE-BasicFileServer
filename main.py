from os import environ
import os
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from werkzeug.utils import secure_filename
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, send_file, session, url_for, request

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = environ.get("APP_SECRET_KEY")

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id= environ.get("AUTH0_CLIENT_ID"),
    client_secret = environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs = {
        "scope": "openid profile email"
    },
    server_metadata_url=f"https://{environ.get('AUTH0_DOMAIN')}/.well-known/openid-configuration"

)

@app.route('/global')
def globalSite() -> str:
    files = [f for f in os.listdir('storage') if os.path.isfile(os.path.join('storage',f))]
    return render_template("global.html",files=files)

@app.route('/aboutus')
def aboutUs() -> str:
    return render_template("aboutus.html")

@app.route('/')
def main() -> str :
    return render_template("index.html")

@app.route('/login')
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route('/callback', methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/global")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + str(environ.get("AUTH0_DOMAIN"))
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("globalSite", _external=True),
                "client_id": environ.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/download/<filename>")
def download(filename: str):
    return send_file(os.path.join("./storage",filename),as_attachment=True)

@app.route("/upload",methods=["POST"])
def upload():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
         file.filename = secure_filename(file.filename)
         file.save(f'./storage/{file.filename}')
    return redirect(url_for('globalSite'))

if __name__ == "__main__":
    app.run(debug=True,host="localhost",port=environ.get("PORT",1738))
