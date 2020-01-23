#!/usr/bin/env python

import mysql.connector
from configs import db_config as conf


def db_fetch(hire_start, hire_end):

    db = mysql.connector.connect(
        user=conf.mysql['user'],
        password=conf.mysql['passwd'],
        host=conf.mysql['host'],
        database=conf.mysql['db'])

    dcursor = db.cursor()
    query = ("SELECT DISTINCT url FROM abuse_bot WHERE date BETWEEN '%s' AND '%s' GROUP BY url")
    print("db_fetch INFO:")
    print("hire_start = " + str(hire_start))
    print("hire_end= " + str(hire_end))
    out_tw = (query % (hire_start, hire_end))
    print("query = " + str(out_tw))
    final_result = list()
    for result in dcursor.execute(out_tw, multi=True):
        final_result = [list(i) for i in result.fetchall()]
    dcursor.close()
    db.close()
    final_res = sorted(final_result)
    print(final_res)
    print (len(final_res))
    return final_res


def db_insert(date, feed, url):

    db = mysql.connector.connect(
        user=conf.mysql['user'],
        password=conf.mysql['passwd'],
        host=conf.mysql['host'],
        database=conf.mysql['db'])

    dcursor = db.cursor()
    error = False
    sql = ( "INSERT INTO abuse_bot(date, feed, url) "
            "VALUES(%s, %s, %s)")
    vls = (date, feed, url)
    
    try:
        dcursor.execute(sql, vls)
        db.commit()
    except Exception as e:
        error = e
        db.rollback()
        
    dcursor.close()
    db.close()
    return error


def db_insert_raw(date, feed, url):
    
    db = mysql.connector.connect(
        user=conf.mysql['user'],
        password=conf.mysql['passwd'],
        host=conf.mysql['host'],
        database=conf.mysql['db'])

    dcursor = db.cursor()
    error = False
    sql = ("INSERT INTO abuse_bot_train(date, feed, url) "
           "VALUES(%s, %s, %s)")
    vls = (date, feed, url)

    try:
        dcursor.execute(sql, vls)
        db.commit()
    except Exception as e:
        error = e
        db.rollback()

    dcursor.close()
    db.close()
    return error