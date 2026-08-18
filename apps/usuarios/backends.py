from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailAuthBackend(ModelBackend):
    """
    Autentica usando una dirección de correo electrónico.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Intenta buscar al usuario usando el correo electrónico
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        
        # Si el usuario existe, verifica la contraseña
        if user.check_password(password):
            return user
        return None
        
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None