from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators
from wtforms.fields.html5 import EmailField

from pipet.forms import LoginForm, OrganizationForm
from pipet.models import db, Organization, User


blueprint = Blueprint('pipet', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=request.form['email']).first()
        if not user:
            org = Organization()
            user = User(email=request.form['email'], organization=org)

        user.refresh_validation_hash()
        user.send_confirmation_email()
        db.session.add(user)
        db.session.commit()
        return "Check your inbox"
    return render_template('index.html', form=form)


@blueprint.route('/login/<validation_hash>')
def login_with_validation(validation_hash):
    user = User.query.filter_by(validation_hash=validation_hash).first_or_404()
    login_user(user)
    return redirect(url_for('index'))


@blueprint.route('/organization', methods=['GET', 'POST'])
@login_required
def organization():
    form = OrganizationForm(obj=current_user.organization)

    if form.validate_on_submit():
        current_user.organization.name = request.form['name']
        current_user.organization.database_credentials = request.form['database_credentials']
        db.session.add(current_user.organization)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('organization.html', form=form)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
