#For ModelBackEnd : connexion par mail et password
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            print(f"NO USER WITH EMAIL={username}")
            return None
        else:
            if user.check_password(password):
                return user
            print(f"{password} is not a correct password for {user.username}")
        return None

