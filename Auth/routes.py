from flask import Blueprint, render_template, flash, url_for, redirect, request
from flask_login import login_user, login_required, logout_user
from models import db, Tenant, Landlord, Users, Admin
from .form import *
from datetime import datetime
import random

auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.route("/landlord-signup", methods=["POST", "GET"])
def landlord_signup():
  form = LandlordRegistrationForm()
  if form.validate_on_submit():
    new_landlord = Landlord(
      first_name = form.first_name.data,
      last_name = form.last_name.data,
      email = form.email_address.data,
      phone = form.phone_number.data,
      date = datetime.now(),
      unique_id = random.randint(100000,999999),
      account_type = "Landlord",
      passwords = form.password.data,
    )
    db.session.add(new_landlord)
    db.session.commit()
    flash(f"Account created successfully", category="success")
    return redirect(url_for("auth.landlord_login"))

  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"{err_msg}", category="danger")

  return render_template("landlord.html", form=form)

@auth.route("/landlord-login", methods=["POST", "GET"])
def landlord_login():
  form = LandlordLoginForm()
  if form.validate_on_submit():
    landlord = Landlord.query.filter_by(unique_id=form.landlord_id.data).first()
    if not landlord:
      flash(f"No user with that Landlord ID", category="danger")
      return redirect(url_for("auth.landlord_login"))
    elif landlord and landlord.check_password_correction(attempted_password=form.password.data):
      login_user(landlord, remember=True)
      flash(f"Login successfull, welcome {landlord.first_name}",category="success")
      next = request.args.get("next")
      return redirect(next or url_for("landlord.landlord_dashboard"))
    else:
      flash(f"Invalid credentials", category="danger")
      return redirect(url_for("auth.landlord_login"))

  return render_template("landlord_login.html", form=form)

@auth.route("/tenant-signup", methods=["POST", "GET"])
def tenant_signup():
  form = TenantRegistrationForm()
  if form.validate_on_submit():
    new_tenant = Tenant(
      first_name = form.first_name.data,
      last_name = form.last_name.data,
      email = form.email_address.data,
      phone = form.phone_number.data,
      date = datetime.now(),
      unique_id = random.randint(100000,999999),
      passwords = form.password.data,
      account_type = "Tenant",
      landlord = Landlord.query.filter_by(unique_id=form.landlord_id.data).first().id,
      properties = Properties.query.filter_by(property_id=form.property_id.data).first().id,
    )
    db.session.add(new_tenant)
    db.session.commit()
    flash(f"Account created successfully", category="success")
    return redirect(url_for("auth.tenant_login"))

  if form.errors != {}:
    for err_msg in form.errors.values():
      flash(f"{err_msg}",category="danger")

  return render_template("tenant.html", form=form)

@auth.route("/tenant-login", methods=["POST", "GET"])
def tenant_login():
  form = TenantLoginForm()
  if form.validate_on_submit():
    tenant = Tenant.query.filter_by(unique_id=form.tenant_id.data).first()
    if not tenant:
      flash(f"No user with that Tenant ID", category="danger")
      return redirect(url_for('auth.tenant_login'))
    if tenant and tenant.check_password_correction(attempted_password=form.password.data):
      login_user(tenant, remember=True)
      flash(f"Login successfull", category="success")
      return redirect(url_for("tenant.tenant_dashboard"))
    else:
      flash(f"Invalid credentials", category="danger")
      return redirect(url_for('auth.tenant_login'))

  return render_template("tenant_login.html", form=form)

@auth.route("/signup", methods=["POST", "GET"])
def signup():
  form = UserRegistrationForm()
  try:
    if form.validate_on_submit():
      member = Users(
        first_name = form.first_name.data,
        second_name = form.second_name.data,
        last_name = form.last_name.data,
        email = form.email_address.data,
        phone = form.phone_number.data,
        date = datetime.now(),
        unique_id = random.randint(100000,999999),
        account_type = "member",
        passwords = form.password.data,
      )
      db.session.add(member)
      db.session.commit()
      flash(f"User registered successfully", category="success")
      return redirect(url_for("auth.signin"))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"{err_msg}", category="danger")
        return redirect(url_for("auth.signup"))
  except Exception as e:
    flash(f"{repr(e)}", category="danger")
    return redirect(url_for("auth.signup"))

  return render_template("signup.html", form=form)

@auth.route("/signin", methods=["POST", "GET"])
def signin():
  form = UserLoginForm()
  if form.validate_on_submit():
    user = (
      Users.query.filter_by(email=form.email_address.data).first() or Landlord.query.filter_by(email=form.email_address.data).first() or Tenant.query.filter_by(email=form.email_address.data).first() or Admin.query.filter_by(email=form.email_address.data).first()
    )
    if not user:
      flash(f"No user with that email", category="danger")
      return redirect(url_for("auth.signin"))
    elif user and user.check_password_correction(attempted_password=form.password.data):
      login_user(user, remember=True)
      flash(f"Login successfull",category="success",)
      next = request.args.get("next")
      return redirect(next or url_for("main.index"))
    else:
      flash(f"Invalid login credentials", category="danger")
      return redirect(url_for("auth.signin"))

  return render_template("signin.html", form=form)

@auth.route("/admin-login", methods=["POST", "GET"])
def admin_login():
  form = AdminLoginForm()
  if form.validate_on_submit():
    admin = Admin.query.filter_by(unique_id=form.admin_id.data).first()
    if not admin:
      flash("No admin with that ID", category="danger")
      return redirect(url_for('auth.admin_login'))
    elif admin and admin.check_password_correction(attempted_password=form.password.data):
      login_user(admin, remember=True)
      flash("Login successfull", category="success")
      return redirect(url_for('admin.admin'))
    else:
      flash("Invalid credentials", category="danger")
      return redirect(url_for('auth.admin_login'))

  return render_template("admin_login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
  logout_user()
  flash(f"Logged out successfully!", category="success")
  return redirect(url_for("auth.signin"))