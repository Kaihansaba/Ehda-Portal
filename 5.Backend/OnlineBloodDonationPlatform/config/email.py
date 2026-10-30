"""
An SMTP email backend that never breaks a page.

Django's own password-reset view sends mail itself (not through
accounts.notifications.notify), so a blocked or failing SMTP server
would otherwise turn "Forgot password?" into a 500 error. This backend
logs the problem and reports the messages as not sent instead.
"""
import logging

from django.core.mail.backends.smtp import EmailBackend


logger = logging.getLogger(__name__)


class SafeSMTPEmailBackend(EmailBackend):

    def send_messages(self, email_messages):
        try:
            return super().send_messages(email_messages)
        except Exception:
            logger.exception("Could not send %d email(s) by SMTP", len(email_messages or []))
            return 0
