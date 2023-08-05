from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField
from wtforms import SelectField, TextAreaField, DecimalField
from wtforms.validators import InputRequired, Optional, DataRequired


class LogInForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class AddTreatmentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    rank = SelectField('Rank', coerce=int, choices = [
                           (21, "division"),
                           (20, "subdivision"),
                           (19, "class"),
                           (18, "subclass"),
                           (17, "order"),
                           (16, "suborder"),
                           (15, "family"),
                           (14, "subfamily"),
                           (13, "tribe"),
                           (12, "subtribe"),
                           (11, "genus"),
                           (10, "subgenus"),
                           (9, "section"),
                           (8, "subsection"),
                           (7, "series"),
                           (6, "subseries"),
                           (5, "species"),
                           (4, "subspecies"),
                           (3, "variety"),
                           (2, "subvariety"),
                           (1, "form"),
                           (0, "subform")
                       ])
    higher_taxon = StringField('Higher taxon')
    description = TextAreaField('Description')
    phenology = TextAreaField('Phenology')
    habitat = TextAreaField('Habitat')
    distribution = TextAreaField('Distribution')
    notes = TextAreaField('Notes')


class EditTreatmentForm(FlaskForm):
    description = HiddenField(id='description-field')
    phenology = HiddenField(id='phenology-field')
    habitat = HiddenField(id='habitat-field')
    distribution = HiddenField(id='distribution-field')
    notes = HiddenField(id='notes-field')


class AddOccurrenceForm(FlaskForm):
    latitude = StringField('Latitude', validators=[InputRequired()])
    longitude = StringField('Longitude', validators=[InputRequired()])

