#!/usr/bin/env python
#coding=utf-8 
import datetime
import time
import smtplib
import configparser
import argparse
import sys 
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from python_freeipa import ClientMeta


def parse_config(cliargs):
    """
        Parse config file to obtain login credentials and
        address of remote FreeIPA system.
    """
    config = configparser.ConfigParser()
    config.read(cliargs.config)
    ipa_user = config['Login']['user']
    ipa_password = config['Login']['password']
    ipa_hostname = config['Login']['hostname']
    ipa_notify_days_remaining = config['Option']['notify_days_remaining']
    ipa_email_from = config['Option']['email_from']
    ipa_email_subject = config['Option']['email_subject']
    ipa_email_body = config['Option']['email_body'] 
    return ipa_user, ipa_password, ipa_hostname, ipa_notify_days_remaining, ipa_email_from, ipa_email_subject, ipa_email_body


def ipa_connect(ipa_user, ipa_password, ipa_hostname):
    """
        Connect and login to FreeIPA system with a secured
        SSL connection.
    """
    client = ClientMeta(ipa_hostname, verify_ssl='/etc/ipa/ca.crt')
    client.login(ipa_user, ipa_password)
    return client


def ipa_fetch_user_attr(client):
    """
        Get all users from directory with an email address
        to be able to notify them.
    """
    ipa_users_emails = {}
    ipa_users_notification = {}
    ipa_users_attr = client.user_find()
    for single_user in ipa_users_attr["result"]:
        if "mail" in single_user:		
            ipa_user_mail = single_user["mail"][0]
            ipa_user_uid = single_user["uid"][0]
            ipa_users_emails[ipa_user_uid]=ipa_user_mail
            for date in single_user["krbpasswordexpiration"]:
                ipa_user_password_expr = date["__datetime__"][:-7]
            ipa_users_notification[ipa_user_mail] = ipa_user_password_expr
    return ipa_users_emails, ipa_users_notification


def ipa_notify_user(ipa_notify_mails, ipa_email_from, ipa_email_subject, ipa_email_body, ipa_notify_uid):
    """
        Generate password expire mail and send them via local MTA
        to make sure this'll be queued when remote MTA is unreachable.
    """
    server = "localhost"
    body = 'Oi {} {}'.format(ipa_notify_uid,ipa_email_body)
    msg = MIMEMultipart()
    msg['From'] = ipa_email_from 
    msg['To'] = COMMASPACE.join(ipa_notify_mails)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = ipa_email_subject
    msg.attach(MIMEText(body))
    smtp = smtplib.SMTP(server)
    smtp.sendmail(ipa_email_from, ipa_notify_mails, msg.as_string())
    smtp.close()


def ipa_pwexpire_check(ipa_users_notification, ipa_users_emails, ipa_notify_days_remaining, ipa_email_from, ipa_email_subject, ipa_email_body):
    """
        Check if users password is going to expire within the
        next few days.
    """
    for single_user in ipa_users_emails:
	single_mail = ipa_users_emails[single_user]
        ipa_date_expr = ipa_users_notification[single_mail]
        ipa_date_now = time.strftime("%Y%m%d")
        start_date = datetime.datetime.strptime(ipa_date_expr, "%Y%m%d")
        end_date = datetime.datetime.strptime(ipa_date_now, "%Y%m%d")
        ipa_days_left = abs((end_date-start_date).days)
        if ipa_days_left < ipa_notify_days_remaining:
            ipa_notify_mails = []
            ipa_notify_mails.append(single_mail)
            ipa_notify_user(ipa_notify_mails, ipa_email_from, ipa_email_subject, ipa_email_body, single_user)


def main():
    """
        Run the main programm
    """
    argparser = argparse.ArgumentParser(description='FreeIPA password expire notificator.')
    argparser.add_argument('-C', '--config', type=str, help='Path to config file')
    cliargs = argparser.parse_args()

    if cliargs.config is None:
        print "Error: Please define config file."
        sys.exit(2)

    ipa_user, ipa_password, ipa_hostname, ipa_notify_days_remaining, ipa_email_from, ipa_email_subject, ipa_email_body = parse_config(cliargs)
    client = ipa_connect(ipa_user, ipa_password, ipa_hostname)
    ipa_users_emails, ipa_users_notification = ipa_fetch_user_attr(client)
    ipa_pwexpire_check(ipa_users_notification, ipa_users_emails, ipa_notify_days_remaining, ipa_email_from, ipa_email_subject, ipa_email_body)


main()
