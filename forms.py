from wtforms import Form, widgets, StringField, SelectMultipleField
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class UserForm(Form):
    name = StringField('name', validators=[DataRequired()])
    surname = StringField('surname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    per_choices = [('Read', 'Read'), ('Write', 'Write'), ('Delete', 'Delete')]
    permissions = MultiCheckboxField('permissions', choices=per_choices)
