from flask import Flask, render_template, request, Response
import os


app = Flask(__name__,
            template_folder=os.path.join("..", "Frontend", "templates"),
            static_folder=os.path.join("..", "Frontend", "static"))

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)