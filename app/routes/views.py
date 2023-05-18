from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models.database import db, Researchers

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template('index.html')

@views.route('/projects')
@login_required
def projects():
    return render_template('projects.html')


@views.route('/project')
@login_required
def project():
    return render_template('project.html')