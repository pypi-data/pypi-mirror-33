from flask import jsonify, request, current_app, url_for

from app.jobs.extend import stertTxss
from app.jobs.flow import getHaproxyData
from . import api
import  json



@api.route('/autoextend', methods=['GET', 'POST'])
def autoextend():
    """
    获取
    :param app:
    :return:
    """

    appname = request.form['appname']
    serviceport =request.form['serviceport']
    min = request.form['min']
    max = request.form['max']


    stertTxss(appname,serviceport,int(min),int(max))



    # interval = request.form['interval']
    # target = request.form['target']
    # outtime = request.form['outtime']



    return json.dumps({"success":True,"code":"0000","msg":"autoextend_success"})




@api.route('/flowmonitoring', methods=['GET', 'POST'])
def flowmonitoring():
    """
    获取
    :param app:
    :return:
    """

    getHaproxyData()


    return json.dumps({"success":True,"code":"0000","msg":"flowmonitoring_success"})

