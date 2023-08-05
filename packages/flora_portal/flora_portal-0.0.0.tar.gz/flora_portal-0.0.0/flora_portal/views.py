from flora_portal import app, mysql
from .markup import make_name_simple, make_name_html, clean_html
from . import queries
from . import forms
from flask import render_template, session, jsonify, request
from flask import url_for, redirect, flash
from passlib.hash import sha256_crypt


ranks = {
    0: "subform",
    1: "form",
    2: "subvariety",
    3: "variety",
    4: "subspecies",
    5: "species",
    6: "subseries",
    7: "series",
    8: "subsection",
    9: "section",
    10: "subgenus",
    11: "genus",
    12: "subtribe",
    13: "tribe",
    14: "subfamily",
    15: "family",
    16: "suborder",
    17: "order",
    18: "subclass",
    19: "class",
    20: "subdivision",
    21: "division"
}


@app.route('/taxon/<int:taxon_id>', methods=['GET', 'POST'])
def treatment(taxon_id):
    form = forms.EditTreatmentForm()

    cursor = mysql.get_db().cursor()

    if form.validate_on_submit():
        cursor.execute(queries.UPDATE_TREATMENT,
                       (form.description.data.strip() or None,
                        form.phenology.data.strip() or None,
                        form.habitat.data.strip() or None,
                        form.distribution.data.strip() or None,
                        form.notes.data.strip() or None,
                        taxon_id))
        flash("Successfully updated treatment", "success")

    cursor.execute(queries.SELECT_TREATMENT, (taxon_id))

    taxon = cursor.fetchone()

    if taxon is None:
        return "Invalid taxon ID {}".format(taxon_id)

    cursor.execute(queries.SELECT_IMAGES, (taxon_id))

    images = cursor.fetchall()

    cursor.execute(queries.SELECT_OCCURRENCES, (taxon_id))

    occurrences = cursor.fetchall()

    return render_template('treatment.html',
                           taxon_id=taxon_id,
                           flora_name=taxon[0],
                           name_simple=taxon[1],
                           name_html=taxon[2],
                           parent_id=taxon[3],
                           parent=taxon[4],
                           description=taxon[5],
                           phenology=taxon[6],
                           habitat=taxon[7],
                           distribution=taxon[8],
                           notes=taxon[9],
                           common_names=taxon[10],
                           images=images,
                           occurrences=occurrences,
                           form=form)


@app.route('/taxon/<int:taxon_id>.json')
def treatment_json(taxon_id):
    cursor = mysql.get_db().cursor()
    cursor.execute(queries.SELECT_TREATMENT, (taxon_id))

    taxon = cursor.fetchone()

    if taxon is None:
        return "Invalid taxon ID {}".format(taxon_id)

    cursor.execute(queries.SELECT_IMAGES, (taxon_id))

    images = cursor.fetchall()

    cursor.execute(queries.SELECT_OCCURRENCES, (taxon_id))

    occurrences = cursor.fetchall()

    return jsonify({"name_markup": taxon[0],
                    "parent_id": taxon[1],
                    "parent": taxon[2],
                    "description": taxon[3],
                    "phenology": taxon[4],
                    "habitat": taxon[5],
                    "distribution": taxon[6],
                    "notes": taxon[7],
                    "common_names": taxon[8],
                    "images": images,
                    "occurrences": occurrences})


@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    form = forms.LogInForm()

    if form.validate_on_submit():
        username = form.username.data
        cursor = mysql.get_db().cursor()
        cursor.execute(queries.SELECT_USER, (username))
        user = cursor.fetchone()

        if user is None:
            flash("Invalid username", "error")
        else:
            user_id = user[0]
            is_admin = user[1]
            password_hash = user[2]
            password = form.password.data

            if sha256_crypt.verify(password, password_hash):
                session['user'] = {
                    "id": user_id,
                    "username": username, 
                    "is_admin": is_admin
                }
                return redirect(url_for('dashboard'))
            else:
                flash("Incorrect password", "error")

    return render_template("log_in.html", form=form)


@app.route("/log_out")
def log_out():
    session.pop('user')
    return "Logged out"


"""
@app.route("/log_in", methods=["POST"])
def log_in_post():
    username = request.form['username']
    cursor = get_db().cursor()
    cursor.execute(queries.SELECT_USER, (username))
    user = cursor.fetchone()
    if user is None:
        flash("Invalid username", "error")
        return render_template("log_in.html")
    password = request.form['password']

    user_id = user[0]
    is_admin = user[1]
    password_hash = user[2]

    if sha256_crypt.verify(password, password_hash):
        session['user'] = {
            "id": user_id,
            "username": username, 
            "is_admin": is_admin
        }
        return redirect(url_for('dashboard'))
    flash("Incorrect password", "error")
    return render_template("log_in.html")
"""

@app.route("/flora/<int:flora_id>/add", methods=["GET", "POST"])
def add(flora_id):
    if 'user' not in session:
        return "Access denied"
    cursor = mysql.get_db().cursor()
    cursor.execute(queries.CHECK_USER_ACCESS,
                   (session['user']['id'], flora_id))
    user = cursor.fetchone()

    if user is None:
        return "Access denied"

    form = forms.AddTreatmentForm()

    if form.validate_on_submit():
        name_markup = form.name.data
        name_simple = make_name_simple(name_markup)
        name_html = make_name_html(name_markup)

        rank = form.rank.data
        parent = form.higher_taxon.data.strip() or None
        description = clean_html(form.description.data) or None
        phenology = clean_html(form.phenology.data) or None
        habitat = clean_html(form.habitat.data) or None
        distribution = clean_html(form.distribution.data) or None
        notes = clean_html(form.notes.data) or None

        if parent is not None:
            cursor.execute("SELECT id FROM taxa WHERE name_simple = %s",
                           (parent))

            parent_row = cursor.fetchone()
            if parent_row is None:
                flash("Parent taxon does not exist", "error")
                return render_template('add.html', form = form)
            parent_id = parent_row[0]
        else:
            parent_id = None

        cursor.execute(queries.INSERT_TAXON,
                       (flora_id, parent_id, name_simple,
                        name_html, name_markup, rank))

        cursor.execute("SELECT LAST_INSERT_ID()")
        taxon_id = cursor.fetchone()[0]

        cursor.execute(queries.INSERT_TREATMENT,
                       (taxon_id, description, phenology,
                        habitat, distribution, notes))

        flash("Successfully added treatment", "success")

    return render_template('add.html', form=form)


@app.route('/taxon/<int:taxon_id>/add_image', methods=['GET', 'POST'])
def add_image(taxon_id):
    if 'user' not in session:
        return "Access denied"
    cursor = mysql.get_db().cursor()
    cursor.execute(queries.CHECK_USER_ACCESS_BY_TAXON,
                   (session['user']['id'], taxon_id))
    user = cursor.fetchone()

    if user is None:
        return "Access denied"

    if request.method == 'GET':
        return render_template('add_image.html')
    elif request.method == 'POST':
        if 'image' not in request.files:
            flash("No file part")
            return render_template('add_image.html')
        image = request.files['image']
        file_name = image.filename
        if file_name == '':
            flash("No file selected", "error")
            return render_template('add_image.html')
        if '.' in file_name:
            extension = file_name.rsplit('.', -1)[1].lower()
        else:
            extension = None

        cursor.execute(queries.INSERT_IMAGE, (taxon_id, extension))
        cursor.execute("SELECT LAST_INSERT_ID()")
        image_id = cursor.fetchone()[0]

        if (extension is not None and
                extension in app.config['ALLOWED_EXTENSIONS']):
            image.save('{}/{}.{}'.format(app.config['TAXA_IMG_DIR'],
                                         image_id, extension))
            flash("Successfully added image", "success")
            return render_template('add_image.html')
        else:
            flash("Invalid file extension", "error")
            return render_template('add_image.html')


@app.route('/taxon/<int:taxon_id>/add_occurrence', methods=['GET', 'POST'])
def add_occurrence(taxon_id):
    if 'user' not in session:
        return redirect(url_for('log_in'))
    cursor = mysql.get_db().cursor()
    cursor.execute(queries.CHECK_USER_ACCESS_BY_TAXON,
                   (session['user']['id'], taxon_id))
    user = cursor.fetchone()

    if user is None:
        return "Access denied"

    form = forms.AddOccurrenceForm()

    if form.validate_on_submit():
        cursor = mysql.get_db().cursor()
        cursor.execute(queries.INSERT_OCCURRENCE,
                       (taxon_id, form.latitude.data, form.longitude.data))
        flash("Successfully added occurrence record", "success")

    return render_template('add_occurrence.html', form=form)


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('log_in'))
    cursor = mysql.get_db().cursor()
    cursor.execute(queries.SELECT_USER_ACCESS,
                   session['user']['id'])
    access = cursor.fetchall()
    return render_template('dashboard.html', access=access)

