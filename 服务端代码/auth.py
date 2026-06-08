"""用户认证 Blueprint（登录/注册/登出）"""
from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template("login.html", error="请输入用户名和密码")

        user = User.find_by_username(username)
        if user is None:
            return render_template("login.html", error="用户不存在")

        from werkzeug.security import check_password_hash
        if not check_password_hash(user.password_hash, password):
            return render_template("login.html", error="密码错误")

        login_user(user)
        next_page = request.args.get("next")
        return redirect(next_page or url_for("index"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not password:
            return render_template("register.html", error="请填写所有字段")
        if len(username) < 2 or len(username) > 20:
            return render_template("register.html", error="用户名长度 2-20 个字符")
        if len(password) < 4:
            return render_template("register.html", error="密码至少 4 位")
        if password != confirm:
            return render_template("register.html", error="两次密码不一致")

        existing = User.find_by_username(username)
        if existing:
            return render_template("register.html", error="用户名已存在")

        user = User.create(username, password)
        login_user(user)
        return redirect(url_for("index"))

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
