from scrapy.conf import settings
from scrapy.mail import MailSender


mailer = MailSender(
    mailfrom=settings['EMAIL_FROM'],
    smtphost=settings['EMAIL_SMTP_HOST'],
    smtpport=settings['EMAIL_SMTP_PORT'],
    smtpuser=settings['EMAIL_SMTP_USER'],
    smtppass=settings['EMAIL_SMTP_PASS'],
    smtptls=False
)


class TfspiderPipeline(object):

    def process_item(self, item, spider):
        """
        Email new members.
        """
        if not item:
            return {'count': 0}

        body = ""
        for member in item.values():
            body += "{username}, {age}, {city} -> {url} \n".format(
                username=member['username'],
                age=member['age'],
                city=member['city'],
                url='https://www.thaifriendly.com/{username}'.format(username=member['username'])
            )

        mailer.send(
            to=[settings['EMAIL_RECEIVER']],
            subject="New TF members",
            body=body
        )

        return {'count': len(item)}
