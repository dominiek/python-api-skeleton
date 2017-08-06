
import pystmark
import constants
import logging

def send_mail(to, subject, text, sender=constants.MAILER_FROM):
    if constants.ENVIRONMENT == 'test':
        logging.warn('Skipping sending mail to {} due to ENVIRONMENT == test'.format(to))
        return
    message = pystmark.Message(
        sender=sender, to=to, subject=subject,
        text=text)
    pystmark.send(message, api_key=constants.MAILER_POSTMARK_API_KEY)
    logging.info('Send mail to {} with subject `{}`'.format(to, subject))
