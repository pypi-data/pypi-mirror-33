from flask_wtf import FlaskForm
from wtforms import SelectField, HiddenField


class ActivateExtraForm(FlaskForm):

    email = HiddenField()
    password = HiddenField()
    extra = HiddenField()

    agent = SelectField('Activate as', choices=(('new', 'New agent'),))
