# -*- coding: utf-8 -*-
from log4python.Log4python import log
from config import config_monitor_pwd
from sendMail import SendMail
logger = log("report_monitor")


def send_mail(subject, mail_body, attach_file):
    username = config_monitor_pwd['email_info']['username']
    password = config_monitor_pwd['email_info']['password']
    ews_url = config_monitor_pwd['email_info']['ews_url']
    receive_mail = config_monitor_pwd['email_info']['receive_mail']
    primary_smtp_address = config_monitor_pwd['email_info']['primary_smtp_address']

    mail = SendMail(username, password, ews_url, primary_smtp_address)
    mail.mail_receiver(receive_mail)
    mail.mail_assemble(subject, mail_body, attach_file)
    mail.send_mail()


if __name__ == '__main__':
    # send mail
    csv_file = "%s/%s" % ("/var/log/", u"Access.csv")
    csv_detail_file = "/var/log/test.txt"
    send_mail(u"Title",
              u"\n日期：%s; 人员：%s；\n访问，见附件：%s\n见附件：%s\n\n" , [csv_file, csv_detail_file])