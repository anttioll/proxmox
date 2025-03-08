from os import environ
from celery import Celery
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session, url_for
from flask_login import current_user, LoginManager, login_required, login_user, logout_user, UserMixin
from waitress import serve
from werkzeug.middleware.proxy_fix import ProxyFix
import redis
import requests
import scripts


load_dotenv()
app = Flask(__name__)
app.secret_key: str = environ.get("SECRET_KEY")
app.wsgi_app = ProxyFix(app.wsgi_app, 
                        x_proto=1, 
                        x_for=1, 
                        x_host=1, 
                        x_port=1, 
                        x_prefix=1, 
                        )
login_manager = LoginManager()
login_manager.init_app(app)
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)
redis_client = redis.Redis(host="localhost", port=6379, db=0)


class User(UserMixin):
    def __init__(self, username: str):
        self.id: str = username


@login_manager.user_loader
def user_loader(username: str) -> object:
    user = User(username=username)
    return user


@app.route("/admin", methods=["GET"])
def index() -> str:
    return redirect(url_for("login"))


@app.route("/admin/login", methods=["GET", "POST"])
def login() -> str:
    if current_user.is_authenticated:
        return redirect(url_for("menu"))
    if request.method == "POST":
        username: str = request.form.get("username")
        password: str = request.form.get("password")
        if scripts.authenticate(username, password):
            user = User(username=username)
            login_user(user)
            return redirect(url_for("menu"))

    return render_template("login.html", title="Login")


@app.route("/admin/logout", methods=["POST"])
def logout() -> str:
    logout_user()

    return redirect(url_for("login"))


@app.route("/admin/menu", methods=["GET"])
@login_required
def menu() -> str:
    return render_template("menu.html", title="Proxmox Script Menu")


@app.route("/admin/run_script/<string:script>", methods=["GET", "POST"])
@login_required
def run_script(script) -> str:
    if script == "create_vms":
        redis_client.set("task_progress", "true")
        create_vms_task.delay()
        return jsonify({"status": "in_progress"})
    elif script == "delete_vms":
        redis_client.set("task_progress", "true")
        delete_vms_task.delay()
        return jsonify({"status": "in_progress"})
    elif script == "passwd":
        scripts.reset_passwords()
        return send_from_directory("/home/proxmox", "passwords.txt", as_attachment=True)
    elif script == "download_passwd_file":
        return send_from_directory("/home/proxmox", "passwords.txt", as_attachment=True)
    elif script == "permissions":
        scripts.set_permissions()
        return redirect(url_for("menu"))
    elif script == "firewall":
        scripts.apply_firewall_rules()
        return redirect(url_for("menu"))

    return jsonify()


@app.route("/admin/task_status", methods=["GET"])
def task_status() -> str:
    if redis_client.get("task_progress") == b"true":
        return jsonify({"status": "in_progress"})
    else:
        return jsonify({"status": "not_in_progress"})


@app.route("/admin/task_complete", methods=["GET", "POST"])
@login_required
def task_complete() -> str:
    """
    GET-metodi suojaa popup-ikkunan jumiin jäämiseltä. Jos menu.html-sivun popup-ikkuna jää jumiin, 
    voidaan mennä osoitteeseen /admin/task_complete ja siitä pääsee helposti eroon.
    """
    redis_client.delete("task_progress")

    return jsonify({"status": "task_complete"})


@celery.task
def create_vms_task() -> str:
    scripts.create_vms()

    return requests.post("http://127.0.0.1:8080/admin/task_complete")
        

@celery.task
def delete_vms_task() -> str:
    scripts.delete_vms()

    return requests.post("http://127.0.0.1:8080/admin/task_complete")


if __name__ == "__main__":
    serve(app, 
          listen="127.0.0.1:8080", 
          url_scheme="https", 
          trusted_proxy="127.0.0.1", 
          trusted_proxy_count=1, 
          trusted_proxy_headers="x-forwarded-proto x-forwarded-for x-forwarded-host x-forwarded-port", 
          )
    #app.run(host="localhost", port="8080")
