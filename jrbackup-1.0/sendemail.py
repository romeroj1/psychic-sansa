#!/usr/bin/env python

import smtplib
import os
import ConfigParser
import backup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

confpath = os.path.dirname(__file__)
config = ConfigParser.ConfigParser()
config.read(confpath + "/backup.conf")


def sendmail(subject=None,strmsg=None):
    '''Sends an email'''
    
    # me == my email address
    # you == recipient's email address
	#Credentials
    username = config.get("Email","usrEmail")
    password = config.get("Email","usrEmailPwd")	
    me = config.get("Email","fromAddr")
    emaillist = backup.splitNreturn(config.get("Email", "EmailList"))
    strmailgw = config.get("Email","smtp")
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ', '.join(emaillist) 


    # Create the body of the message (a plain-text and an HTML version).
    text = strmsg
    html = """<html><head></head><body><p>Hi!<br></p></body></html>"""

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    #msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP(strmailgw)
    #Enable secure connection to gmail smtp
    s.starttls()
    #Set credentials to send email via gmail
    s.login(username,password)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, emaillist, msg.as_string())
    s.quit()