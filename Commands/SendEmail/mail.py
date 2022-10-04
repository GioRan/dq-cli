import glob
import logging
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import List

from Utilities.config import props


class Constants:
    port = props['mail']['port']
    domain = props['mail']['domain']
    sender_name = props['mail']['sender_name']
    sender_email = props['mail']['sender_email']
    password = props['mail']['password']


class Mail(Constants):

    def __init__(self) -> None:
        """
        Initialize SMTP Email config
        """
        super().__init__()

        ssl_context = ssl.create_default_context()

        self.service = smtplib.SMTP_SSL(self.domain, self.port, context=ssl_context)
        self.service.login(self.sender_email, self.password)

    def send(self, subject: str, to: str, template: str, payload: dict) -> None:
        """
        Send email

        :param subject: Subject of email
        :type subject: str
        :param to: List of recipients delimited by comma (No Space)
        :type to: str
        :param template: Template name
        :type template: str
        :param payload: Template payload in dictionary format, in respect with the content of Template
        :type payload: dict
        :return: None
        :rtype: None
        """
        mail = MIMEMultipart('alternative')
        mail['Subject'] = subject
        mail['From'] = formataddr((self.sender_name, self.sender_email))
        mail['To'] = to

        html_template = self._get_template(template, **payload)
        body = MIMEText(html_template, 'html')

        mail.attach(body)

        self.service.sendmail(self.sender_email, to_addrs=to.split(','), msg=mail.as_string())

        logging.info(f'{template} email was sent to the ff: {to}')

        self.service.quit()

    def _get_template(self, template_name: str, **kwargs):
        project_folder = os.path.dirname(os.path.realpath(__file__))

        try:
            template = glob.glob(os.path.join(project_folder, 'Templates', f'{template_name}.html'))[0]
            return open(template).read().format(**kwargs)
        except Exception:
            raise ValueError(f'{template_name} does not exist.')

    def list_template(self) -> List[str]:
        project_folder = os.path.dirname(os.path.realpath(__file__))
        templates = glob.glob(os.path.join(project_folder, 'Templates', '*.html'))

        return [os.path.splitext(t.split(os.sep)[-1])[0] for t in templates]

    def _get_recipients_by_cfu(self, cfu: str) -> str:
        return ','.join(props['mail'][f'{cfu}_users'])

    def _parse_list_to_html(self, items: List[str]):
        html = '<ul>\n'

        for item in items:
            html += f'<li>{item}</li>\n'

        html += '</ul>'

        return html
