from django.db.models import Q
from django.contrib.auth.backends import ModelBackend

from .models import CustomUser as User

class AuthBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
        try:
           return User.objects.get(pk=user_id)
        except User.DoesNotExist as e:
           print(f'ERROR AUTH: {e}')
           return None

    def authenticate(self, request, username, password):

        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )

        except User.DoesNotExist as e:
            print(f'ERROR AUTH: {e}')
            return None

        if user.check_password(password):
            return user

        else:
            return None