import psycopg2
import to_do_web
from io import BytesIO
import urllib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import math


def db_access():
    connection = psycopg2.connect("host=127.0.0.1 port=5432 dbname=to_do user=postgres password=Sm@120109")
    
    cursor = connection.cursor()

    return cursor, connection


def catch_task(user_id):
    cursor, connection = db_access()
    cursor.execute("SELECT task_id, task_name, task_deadline, task_importance FROM tasks WHERE user_id = (%s) ORDER BY task_deadline", 
    [user_id])
    tasks = []
    for row in cursor:
        tasks.append([row[0], row[1], row[2], row[3]])
    
    return tasks


def catch_f_task(user_id):
    cursor, connection = db_access()
    cursor.execute("SELECT * FROM finished_tasks WHERE user_id = (%s) LIMIT 100", [user_id])
    f_tasks = []
    for row in cursor:
        f_tasks.append([row[0], row[1], row[2]])
    
    return f_tasks


def user_login(cursor, name, password):

    cursor.execute("SELECT user_id, user_name FROM users WHERE user_name = (%s) AND user_pass = (%s)", [name, password])
    user = []
    for row in cursor:
        user.append(row[0])
        user.append(row[1])

    return user


def user_new(cursor, connection, name, password):
   
    cursor.execute("INSERT INTO users(user_name, user_pass) VALUES((%s), (%s))", [name, password])
    connection.commit()
    cursor.execute("SELECT user_id FROM users WHERE user_name = (%s) AND user_pass = (%s)", [name, password])
    user_id = list(cursor.fetchone())

    return [user_id[0], name] 


def check_task(user_id, day_int, cursor, connection):
    day = str(day_int) + (" days")
    cursor.execute("SELECT * FROM tasks WHERE user_id = (%s) AND (task_deadline - current_timestamp) < (%s)", [user_id, day])
    
    tmp = cursor.fetchall()
    task_list = []

    if len(tmp) == 0:
        return False
    else:
        for i in range(len(tmp)):
            urg = to_do_web.cal_urgency(tmp[i][3], day_int)
            task_list.append([i+1, tmp[i][2], tmp[i][3], tmp[i][4], urg])
        
        return to_do_web.draw_figure(task_list, day_int)



def new_task(cursor, connection, user_data, task_name, task_deadline, task_importance):
    
    cursor.execute("INSERT INTO tasks(user_id, task_name, task_deadline, task_importance) VALUES((%s), (%s), (%s), (%s))"
    , [user_data, task_name, task_deadline, task_importance])
    connection.commit()
    
    return True


def select_task(cursor, connection, user_id, task_id):
    cursor.execute("SELECT * FROM tasks WHERE user_id = (%s) AND task_id = (%s)",[user_id, task_id])
    check = []
    for row in cursor:
        check.append(row)
    if len(check) != 0:
        day, time = check[0][3].date(), check[0][3].time()
        selected = [check[0][2], day, time, check[0][4]]
        return selected
    else:
        return False


def edit_task(cursor, connection, task_id, task_name, task_deadline, task_importance):
    cursor.execute("UPDATE tasks SET task_name = (%s), task_deadline = (%s), task_importance = (%s) WHERE task_id = (%s)"
    , [task_name, task_deadline, task_importance, task_id])
    connection.commit()
    return True
    

def del_task(cursor, connection, del_num, user_id):
    cursor.execute("SELECT task_id FROM tasks WHERE task_id = (%s) AND user_id = (%s)", [del_num, user_id])
    check = []
    for row in cursor:
        check.append(row)
    if len(check) != 0:
        cursor.execute("DELETE FROM tasks WHERE task_id = (%s)", [del_num])
        connection.commit()
        return True
    else:
        return False


def finish_task(cursor, connection, del_num, user_id):
    cursor.execute("SELECT task_id FROM tasks WHERE task_id = (%s) AND user_id = (%s)", [del_num, user_id])
    check = []

    for row in cursor:
        check.append(row)

    if len(check) != 0:
        cursor.execute("SELECT * FROM tasks WHERE task_id = (%s)", [del_num])
        tmp = list(cursor.fetchone())
        cursor.execute("INSERT INTO finished_tasks(task_name, finish_date, user_id) VALUES((%s), current_timestamp, (%s))", [tmp[2], tmp[1]])
        cursor.execute("DELETE FROM tasks WHERE task_id = (%s)", [del_num])
        connection.commit()
        
        return True
    else:
        return False


if __name__ == '__main__':
    db_access()