from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return six.text_type(str(user.pk))+six.text_type(str(timestamp))+six.text_type(user.is_email_verified)

generate_token = TokenGenerator()