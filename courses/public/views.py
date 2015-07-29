# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session)
from flask.ext.login import login_user, login_required, logout_user

from courses.extensions import login_manager
from courses.user.models import User
from courses.public.forms import LoginForm, SearchForm
from courses.public.umn import get_courses
from courses.user.forms import RegisterForm
from courses.utils import flash_errors
from courses.database import db

blueprint = Blueprint('public', __name__, static_folder="../static")


@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", login_form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        new_user = User.create(username=form.username.data,
                        email=form.email.data,
                        password=form.password.data,
                        active=True)
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route("/about/")
def about():
    form = LoginForm(request.form)
    return render_template("public/about.html", login_form=form)

@blueprint.route("/courses/search/", methods=["GET", "POST"])
def search():
    course_number = None
    compare = None
    previous = False
    form = SearchForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        campus = form.campus.data
        term = form.term.data
        subject = form.subject.data
        if form.course_number:
            course_number = form.course_number.data
            compare = form.compare.data
        data = get_courses(campus, term, subject, course_number, compare)
        try:
            redirect(url_for('.result', data=data))
        except:
            flash_error('Please narrow your search')
    else:
        flash_errors(form)
    return render_template("public/search.html", form=form)

@blueprint.route("/courses/results/")
def result(courses=[]):
    abbreviations = { 'UMNTC': 'Twin Cities', 'UMNRO': 'Rochester', 'UMNCR': 'Crookston',
                       'UMNMO': 'Morris', 'UMNDL': 'Duluth'}
    semesters = { '3': 'Spring', '5': 'Summer', '9': 'Fall'}
    data = request.args['data']  # counterpart for url_for()
    courses = data['courses']
    term_id = data['term']['term_id']
    campus_abr = data['campus']['abbreviation']
    year = '20' + term_id[1:3]
    semester = semesters[term_id[3]]
    campus = abbreviations[campus_abr]
    subject = courses[0]['subject']['description']
    return render_template("public/results.html",
                           courses=courses, 
                           year=year, 
                           semester=semester,
                           campus=campus,
                           subject=subject)
