from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse
from . import models
from . import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import copy
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.forms.models import model_to_dict


# Create your views here.

class BaseProfile(View):
    template_name = 'profile_user/create.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.cart = copy.deepcopy(self.request.session.get('cart', {}))

        self.profile = None

        if self.request.user.is_authenticated:
            self.profile = models.Profile.objects.filter(
                user=self.request.user
            ).first()

            self.context = {
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    user=self.request.user,
                    instance=self.request.user,
                ),
                'profileform': forms.ProfileForm(
                    data=self.request.POST or None,
                    instance=self.profile,
                )
            }
        else:
            self.context = {
                'userform': forms.UserForm(
                    data=self.request.POST or None
                ),
                'profileform': forms.ProfileForm(
                    data=self.request.POST or None
                )
            }

        self.userform = self.context['userform']
        self.profileform = self.context['profileform']

        if self.request.user.is_authenticated:
            self.template_name = 'profile_user/update.html'

        self.render = render(self.request, self.template_name, self.context)

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name, self.context)


class Create(BaseProfile):
    def post(self, *args, **kwargs):
        if not self.userform.is_valid() or not self.profileform.is_valid():
            return self.render

        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('password')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')
        

        # user logado
        if self.request.user.is_authenticated:
            user = get_object_or_404(User, username=self.request.user.username)
            user.username = username
            keys_to_exclude = ['password', 'password2']
            filtered_dict = {key: value for key, value in self.userform.cleaned_data.items() if key not in keys_to_exclude}
            
        
            if password:
                if not check_password(password, user.password):
                    messages.success(self.request, 'Password edited!')
                    user.set_password(password)

            elif model_to_dict(models.User.objects.get(id=self.request.user.pk), exclude='id' 'password' 'password2' 'last_login' 'is_superuser' 'groups' 'user_permissions' 'is_staff' 'date_joined' 'is_active') != filtered_dict:
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                messages.success(self.request, 'Your info was edited successfully!')
                user.save()

            if not self.profile:
                self.profileform.cleaned_data['user'] = user
                profile = models.Profile(**self.profileform.cleaned_data)
                messages.success(self.request, 'Profile created!')
                profile.save()
            elif model_to_dict(models.Profile.objects.get(user_id=self.request.user.pk), exclude='id' 'user') != self.profileform.cleaned_data:
                profile = self.profileform.save(commit=False)
                profile.user = user
                messages.success(self.request, 'Profile was edited successfully!')
                profile.save()

        # user novo
        else:
            user = self.userform.save(commit=False)
            user.set_password(password)
            user.save()

            profile = self.profileform.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(self.request, 'User registered successfully!')

        if password:
            authentic = authenticate(self.request, username=user, password=password)

            if authentic:
                login(self.request, user=user)

        self.request.session['cart'] = self.cart
        self.request.session.save()
        
        return redirect('product:cart')

class Edit(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Edit')

class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')
        if not username or not password:
            messages.error(self.request, 'Invalid user or password')
            return redirect('profile_user:create')
        
        user = authenticate(
            self.request, username=username, password=password
        )

        if not user:
            messages.error(self.request, 'Invalid user or password')
            return redirect('profile_user:create')

        
        login(self.request, user=user)
        messages.success(self.request, "You're logged and can finish your purchase!")

        return redirect('product:cart')

class Logout(View):
    def get(self, *args, **kwargs):
        self.cart = copy.deepcopy(self.request.session.get('cart', {}))

        logout(self.request)

        self.request.session['cart'] = self.cart
        self.request.session.save()

        return redirect('product:list')