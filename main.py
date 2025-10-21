from flask import Flask, render_template

app = Flask(__name__)
app.route('/global')
def globalSite() -> str:
   return "PLACEHOLDER"
@app.route('/')
def main() -> str :
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
