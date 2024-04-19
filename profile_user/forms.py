from django import forms
from django.contrib.auth.models import User
from . import models

class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = '__all__'
        exclude = ('user', )

class UserForm(forms.ModelForm):
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Password',
        help_text="If you're logged and don't want to change your password, leave it blank."
    )

    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Confirm password',
        help_text="If you're logged and don't want to change your password, leave it blank."
    )

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'password2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_error_msgs = {}

        user_data = data['username']

        if user_data == 'AnonymousUser':
            password_data = data['password3']
            password2_data = data['password4']
        else:
            password_data = data['password']
            password2_data = data['password2']
        email_data = data['email']

        # poderia fazer também da seguinte forma:
        # user_data = cleaned.get('username')

        user_db = User.objects.filter(username=user_data).first()
        email_db = User.objects.filter(email=email_data).first()

        error_msg_user_exists = 'User already exists'
        error_msg_email_exists = 'Email already exists'
        error_password_needing = 'Must fulfill password'
        error_non_match_password = "Passwords doesn't match"
        error_short_password = 'Password must have at least 6 characters'


        # Usuários logados: atualização
        if self.user:
            if user_db:
                if user_data != user_db.username:
                    validation_error_msgs['username'] = error_msg_user_exists

            if email_db:
                if email_data != email_db.email:
                    validation_error_msgs['email'] = error_msg_email_exists

            if password_data:
                if password_data != password2_data:
                    validation_error_msgs['password'] = error_non_match_password
                    validation_error_msgs['password2'] = error_non_match_password

                if len(password_data) < 6:
                    validation_error_msgs['password'] = error_short_password

        # Usuários não logados: cadastro
        else:
            
            if user_db:
                validation_error_msgs['username'] = error_msg_user_exists

            if email_db:
                validation_error_msgs['email'] = error_msg_email_exists

            if not password_data:
                validation_error_msgs['password'] = error_password_needing

            if not password2_data:
                validation_error_msgs['password2'] = error_password_needing

            if password_data != password2_data:
                validation_error_msgs['password'] = error_non_match_password
                validation_error_msgs['password2'] = error_non_match_password

            if len(password_data) < 6:
                validation_error_msgs['password'] = error_short_password

        if validation_error_msgs:
            raise(forms.ValidationError(validation_error_msgs))