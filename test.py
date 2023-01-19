"""
Every function attached to url has to return something
"""
from flask import Flask, flash, request, redirect, url_for, render_template, session
from flask_session import Session
import urllib.request
import os
from os import listdir
from werkzeug.utils import secure_filename


app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads/"
app.secret_key = "Holdon@123"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# execution starts here
@app.route("/")
def home():
    return render_template("base.html")


@app.route("/", methods=["POST"])
def toggle_images():
    global item
    flash("In_toggle")
    files = listdir(UPLOAD_FOLDER)
    if request.form.get("submit_button") == "<<":
        item -= 1
    elif request.form.get("submit_button") == ">>":
        item += 1
    i = item % len(files)
    return render_template("base.html", filename=files[i])


@app.route("/", methods=["POST"])
def upload_image():
    flash("in upload_image")
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        # Get the list of files from webpage
        files = request.files.getlist("file")
        # iterate through list of files
        for file in files:
            if file.filename == "":
                flash("No image selected for uploading")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                return toggle_images()
                # return render_template("base.html", filename=filename)
        # print('upload_image filename: ' + filename)
        flash("Image(s) successfully uploaded")
    else:
        flash("Allowed image types are - png, jpg, jpeg, gif")
        return redirect(request.url)


@app.route("/display/<filename>")
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


if __name__ == "__main__":
    global item
    item = 0
    app.run()
