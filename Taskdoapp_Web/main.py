#前準備
from flask import Flask, request, render_template, url_for, session, make_response, jsonify
import db
import os
# from io import BytesIO
# import urllib
# from matplotlib.backends.backend_agg import FigureCanvasAgg
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt


app = Flask(__name__)
cursor, connection = db.db_access()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/auth", methods=["POST"])
def user_login():
    session['user_name'] = request.form["userName"]
    user_password = request.form["userPswd"]

    authentification = db.user_login(cursor, session['user_name'], user_password)

    if len(authentification) != 0:
        session['user_id'] = authentification[0]
        return portal()
    else:
        pop('user_name', None)
        return render_template("index.html")


@app.route("/daily")
def daily_task():
    return render_template("daily.html")


@app.route("/daily_task.png")
def graph_daily():
    return db.check_task(session['user_id'], 1, cursor, connection)


@app.route("/weekly")
def weekly_task(): 
    return render_template("weekly.html")


@app.route("/weekly_task.png")
def graph_weekly():
    return db.check_task(session['user_id'], 7, cursor, connection)
   

@app.route("/monthly")
def monthly_task():
    return render_template("monthly.html")


@app.route("/monthly_task.png")
def graph_monthly():
    return db.check_task(session['user_id'], 30, cursor, connection)


@app.route("/new")
def user_new():
    return render_template("new.html")


@app.route("/new/regi", methods=["POST"])
def user_regi():
    user_name = request.form["userName"]
    user_password = request.form["userPswd"]

    authentification = db.user_new(cursor, connection, user_name, user_password)
    if len(authentification) != 0:
        return portal()
    else:
        return render_template("index.html")


@app.route("/tasks/new")
def task_new():
    return render_template("new_task.html")


@app.route("/tasks/regi", methods=["POST"])
def task_regi():
    task_name = request.form["taskName"]
    task_deadday = request.form["deaddate"]
    task_deadtime = request.form["deadtime"]
    task_importance = request.form["importance"]
    task_day = task_deadday + ' ' + task_deadtime

    Frag = db.new_task(cursor, connection, session['user_id'],
    task_name, task_day, task_importance)

    if Frag:
        return portal()
    else:
        return render_template("new_task.html")


@app.route("/tasks/select", methods=["POST"])
def task_select():
    session['task_id'] = request.form["task_id"]
    task_info = db.select_task(cursor, connection, session['user_id'], session['task_id'])
    if task_info != False:
        return render_template("edit_task.html", task_info = task_info)
    else:
        return task_index()


@app.route("/tasks/edit", methods=["POST"])
def task_edit():
    task_name = request.form["taskName"]
    task_deadday = request.form["deaddate"]
    task_deadtime = request.form["deadtime"]
    task_importance = request.form["importance"]
    task_deadline = task_deadday + ' ' + task_deadtime

    db.edit_task(cursor, connection, session['task_id'], task_name, task_deadline, task_importance) 
    session.pop('task_id', None)
    return task_index()


@app.route("/tasks/del", methods=["POST"])
def task_del():
    task_id = request.form["task_id"]
    Frag = db.del_task(cursor, connection, task_id, session['user_id'])
    if Frag == True:
        return task_index()
    else:
        return task_index()


@app.route("/tasks/finish", methods=["POST"])
def task_fin():
    task_id = request.form["task_id"]
    Frag = db.finish_task(cursor, connection, task_id, session['user_id'])
    if Frag == True:
        return task_index()
    else:
        return task_index()


@app.route("/tasks/index")
def task_index():
    tasks = db.catch_task(session['user_id'])
    return render_template("task_index.html", tasks = tasks)


@app.route("/tasks/finished_index")
def task_f_index():
    f_tasks = db.catch_f_task(session['user_id'])
    return render_template("f_task_index.html", f_tasks = f_tasks)


@app.route("/portal")
def portal():
    return render_template("portal.html", username = session['user_name'])


@app.route("/logout")
def logout():
    session.pop('user_name', None)
    session.pop('user_id', None)
    return render_template("index.html")


app.secret_key = os.urandom(24)


############アプリケーションを走らせるときの処理############
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
#########################################################