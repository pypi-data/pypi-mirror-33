from flask import render_template, session, abort, request, redirect, url_for, current_app, flash
from flask_login import login_required
from . import system
from .. import db
from ..email import send_email
from ..models import User
from flask_sqlalchemy import get_debug_queries





@system.route('/userlist', methods=['GET', 'POST'])
@login_required
def userlist():
    """
    获取用户列表
    :return:
    """

    return render_template('bey/system/users.html')


