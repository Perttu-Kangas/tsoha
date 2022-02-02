from app import app
from flask import render_template, request, redirect


@app.route("/")
def index():
    sections = "list todo"
    # 0 = id, 1 = name, 2 = threads, 3 = messages, 4 = last message
    return render_template("index.html", sections=sections)

