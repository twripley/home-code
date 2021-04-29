import logging
import time
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser
import os.path
import mysql.connector as mysql


def runReport(config):
    # Parse database connection info
    server = config['KODIDB']['server']
    username = config['KODIDB']['username']
    password = config['KODIDB']['password']
    database = config['KODIDB']['database']

    # Connect to the Infratools database
    conn = mysql.connect(host=server, user=username,
                         password=password, database=database)
    cursor = conn.cursor()

    query = "SELECT c00,premiered,uniqueid_value,uniqueid_type from `movie_view` ORDER BY c00 ASC"

    '''
    c00 = Movie Title
    c03 = Movie Slogan
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    # Parse the output
    bodytext = ""
    for row in rows:
        title = row[0]
        premiered = row[1]
        id = row[2]
        id_type = row[3]

        bodytext += f"<tr style=\"background-color: #f0f0f0; font-size: 12px;\">"
        bodytext += f"<td align=right style=\"padding-right: 10px; padding-top: 2px; padding-bottom: 2px;\">{title}</td>"
        bodytext += f"<td align=center>{premiered}</td>"
        bodytext += f"<td align=center><a href=\"http://imdb.com/title/{id}\">{id}</a></td></tr>"

    # Send email
    send_email(bodytext, config)


def send_email(bodytext, config):
    message = MIMEMultipart("alternative")
    message["From"] = config['EMAIL']['from_email']
    message["To"] = config['EMAIL']['to_email']

    curtime = datetime.fromtimestamp(time.time())
    pretty_time = curtime.strftime("%b %d, %Y")

    message["Subject"] = f"KODI Movies: {pretty_time}"
    h1_text = f"<h1>KODI Movie Report</h1><p>{pretty_time}</p>"

    html = f"""
    <!doctype html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>KODI movie Report</title>
    </head>
    <body style="background-color: #ffffff; font-family: sans-serif; -webkit-font-smoothing: antialiased; font-size: 14px; 
    line-height: 1.4; margin: 0; padding: 0; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;">
    {h1_text}
    <table border="1" cellpadding="0" cellspacing="0" class="main" 
    style="border-collapse: separate; margin: auto; width: 57%; background-color: #f6f6f6;">

    <tr style=\"background-color: #dddddd; font-size: 16px;\">
    <th>Movie Title</th>
    <th>Release Date</th><th>IMDB Link</th></tr>
    {bodytext}
    </table>
    """

    part1 = MIMEText(html, "html")
    message.attach(part1)

    mail_server = config['EMAIL']['mail_server']
    with smtplib.SMTP(mail_server, '25') as server:
        server.sendmail(config['EMAIL']['from_email'],
                        config['EMAIL']['to_email'], message.as_string())


if __name__ == "__main__":
    # Define some logging
    console = logging.getLogger(__name__)
    console.setLevel(logging.INFO)

    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('report-error.log')
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.ERROR)

    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter(
        '%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    c_format.datefmt = "%H:%M:%S"
    f_format.datefmt = "%d-%b-%Y %H:%M:%S"

    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    console.addHandler(c_handler)
    console.addHandler(f_handler)

    if os.path.isfile("config.conf"):
        # Parse the config file
        config = configparser.ConfigParser()
        config.read('config.conf')
    else:
        console.error("Unable to read configuration file: config.conf")
        exit()

    runReport(config)
