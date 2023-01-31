"""
Every function attached to url has to return something
"""
from flask import Flask, flash, request, redirect, url_for, render_template, session
from flask_session import Session
import urllib.request
import os
import yaml
import csv
import numpy as np
import shutil
from shutil import make_archive
from os import listdir
from werkzeug.utils import secure_filename


app = Flask(__name__)

STATIC_FOLDER = "static/"
UPLOAD_FOLDER = "static/uploads/"
app.secret_key = "Holdon@123"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def write_yaml(data, file):
    """A function to create and write YAML file"""
    with open(file, "w") as f:
        yaml.dump(data, f)


def create_csv(path2, current):
    """A function to create .txt files of same name as img folder"""
    global files
    os.chdir(current)
    os.chdir(path2)
    for file in files:
        f = open(os.path.splitext(file)[0] + str(".csv"), "w")


def create_dir():
    dir = "static"
    folder_name = "data"
    label_folder = "labels"
    # path1 is "static/data"
    path1 = os.path.join(dir, folder_name)
    # path2 is "static/data/labels"
    path2 = os.path.join(path1, label_folder)
    # making labels folder
    if not os.path.exists(path1):
        os.mkdir(path1)
    if not os.path.exists(path2):
        os.mkdir(path2)
    # making yaml file
    yaml_file = str(label_folder) + str(".yaml")
    return path1, path2, yaml_file


def init_label_store():
    global label_store
    global files
    for file in files:
        label_store[file] = []


def make_labels(label_list):
    current = os.getcwd()
    label_dict = {}
    label_dict["labels"] = {}
    path1, path2, yaml_file = create_dir()
    # changing to labels directory
    os.chdir(path1)
    # making dictionary
    for i in range(len(label_list)):
        label_dict["labels"][i] = label_list[i]
    f = open(yaml_file, "w")
    write_yaml(label_dict, yaml_file)
    create_csv(path2, current)
    os.chdir(current)


def no_images():
    flash("No images uploaded, please upload images for labelling")
    return render_template("labelling.html", label_list=label_list)


def check_labels():
    global label_store
    global files
    flag = 1
    for f in files:
        if f not in label_store:
            flag = 0
            break
    return flag


def zip_csv():
    global label_store
    files = listdir(UPLOAD_FOLDER)
    path = "static/data/labels"
    os.chdir(path)
    for file in files:
        file_name = os.path.splitext(file)[0]
        label_store[file] = np.multiply(label_store[file], 1)
        with open(file_name + str(".csv"), "w") as f:
            out = csv.writer(f, delimiter=",")
            out.writerow(label_store[file])
        flash(file_name)
        flash(label_store[file])
    os.chdir("../")
    shutil.make_archive("labels_y", "zip", "labels")
    flash("zip of labels created in " + str(os.getcwd()))
    files_csv = listdir("labels")
    os.chdir("labels")
    for file in files_csv:
        os.remove(file)


"""
Execution starts here:
"""
@app.route("/")
def home():
    return render_template("base.html")


@app.route("/", methods=["POST"])
def upload_image():
    # flash("in upload_image")
    if request.method == "POST":
        files = request.files.getlist("file")
        # iterate through list of files and save files with allowed extensions
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            else:
                flash("Allowed image types are - png, jpg, jpeg, gif. Please try again")
                return redirect(request.url)
                break
        p = "s" if len(files) > 1 else ""
        flash(
            str(len(files))
            + " "
            + "file"
            + p
            + " "
            + "uploaded to uploads folder successfully"
        )
        return render_template("base.html")


@app.route("/labels", methods=["POST", "GET"])
def labels():
    global label_list
    global files
    # flash("in labels")
    if request.method == "POST":
        if request.form.get("save") == "Save labels":
            # flash("in save labels")
            files = listdir(UPLOAD_FOLDER)
            make_labels(label_list)
            init_label_store()
            if files:
                return render_template(
                    "labelling.html", filename=files[0], label_list=label_list
                )
            else:
                no_images()
        else:
            result = request.form.get("labels")
            label_list.append(result)
            return render_template("base.html", label_list=label_list)


@app.route("/toggle", methods=["POST"])
def toggle_images():
    global item
    global label_list
    global label_store
    global files
    binary_list = []
    # flash("In_toggle")
    tags = request.form.getlist("tags")
    # flash(tags)
    if len(files) != 0:
        if request.form.get("submit_button") == "<<":
            item -= 1
        elif request.form.get("submit_button") == ">>":
            item += 1
        i = item % len(files)
        if tags:
            # flash("in if tags")
            for l in label_list:
                binary_list.append(l in tags)
            label_store[files[i]] = binary_list
        elif not label_store[files[i]]:
            flash("please add at least one label for this image")
        return render_template(
            "labelling.html",
            filename=files[i],
            label_list=label_list,
            label_store=label_store,
        )
    else:
        no_images()


@app.route("/ziplabels", methods=["POST"])
def zip_labels():
    global files
    global label_store
    global label_list
    if not check_labels():
        flash("labels not added for all images")
    elif request.method == "POST":
        if request.form.get("submit_button") == "Download labels":
            zip_csv()
    return render_template(
        "labelling.html",
        filename=files[0],
        label_list=label_list,
        label_store=label_store,
    )


@app.route("/display/<filename>")
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


if __name__ == "__main__":
    global item, label_list, label_store, files
    item = 0
    label_list = []
    label_store = {}
    if not os.path.exists(STATIC_FOLDER):
        os.mkdir(STATIC_FOLDER)
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    files = listdir(UPLOAD_FOLDER)
    app.run(debug=True)
