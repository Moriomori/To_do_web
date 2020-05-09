# coding: utf-8
from flask import Flask, request, render_template, url_for, session, make_response, jsonify
import psycopg2
import matplotlib.pyplot as plt
import japanize_matplotlib
import datetime
from io import BytesIO
import urllib
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import math


def cal_urgency(deadline, fday):
    fsec = 24 * 60
    td = deadline - datetime.datetime.now()
    urgency = int((math.exp(-1 * td.total_seconds() / (fsec * 60)) * 1000))
    return urgency


def draw_figure(task_list, day_int):
    x_list = []
    fig = plt.figure(figsize=(6, 4), dpi=100)
    for i in range(len(task_list)):
        plt.scatter(task_list[i][4], task_list[i][3], label = task_list[i][1])
        x_list.append(task_list[i][4])

    xmax, xmin = max(x_list) + 100, min(min(x_list) - 100, 0)
    
    plt.hlines([50],xmin, xmax, linestyle = 'solid')
    plt.vlines([(xmin + xmax) / 2], 0, 100,linestyle = 'solid')
    plt.xlabel("緊急度")
    plt.ylabel("重要度")
    plt.ylim(0, 100)
    plt.xlim(xmax, xmin)
    plt.title(str(day_int) + "日間タスク一覧")
    plt.legend(bbox_to_anchor=(1.05, 0.5, 0.5, .1), loc='upper left', borderaxespad=0)
    plt.subplots_adjust(left=0.1, right=0.52, bottom=0.24, top=0.82)
    fig.patch.set_alpha(0)

    # canvasにプロットした画像を出力
    canvas = FigureCanvasAgg(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    data = png_output.getvalue()
    # HTML側に渡すレスポンスを生成する
    response = make_response(data)
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Length'] = len(data)
    return response




    