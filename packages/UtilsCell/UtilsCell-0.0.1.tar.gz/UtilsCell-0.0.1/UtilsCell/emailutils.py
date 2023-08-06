#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr



def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def handle_attachment(abs_file):
    part = MIMEApplication(open(abs_file, 'rb').read())
    part.add_header('Content-Disposition', 'attachment',
                    filename=os.path.basename(abs_file))
    return part


def send(mail_user=None,
         mail_pass=None,
         mail_server='smtp.qq.com',
         mail_port='465',
         to_addr=None,
         title=None,
         mail_body=None,
         attachments=None):
    '''
    :param mail_user:
    :param mail_pass:
    :param mail_server:
    :param mail_port:
    :param to_addr:
    :param title:
    :param mail_body:
    :param attachments:
    :return:
    '''
    try:
        msg = MIMEMultipart()

        msg["From"] = _format_addr("<%s>" % mail_user)
        msg["To"] = _format_addr("<%s>" % ",".join(to_addr))
        msg["Subject"] = Header(title, "utf-8").encode()

        html_start = '<font size="5" face="arial"><pre>'
        html_end = '</pre></font>'
        body = MIMEText(html_start + mail_body + html_end,
                        _subtype='html', _charset='utf-8')
        msg.attach(body)

        if attachments:
            for abs_file_path in attachments:
                msg.attach(handle_attachment(abs_file_path))

        server = smtplib.SMTP_SSL(mail_server, mail_port)
        # server.starttls()
        # server.set_debuglevel(1)

        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, to_addr, msg.as_string())
        server.quit()

        return dict(result=True)
    except Exception as e:
        return dict(result=False, details=e)
