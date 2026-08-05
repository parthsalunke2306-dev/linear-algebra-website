from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserSignUpForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'autocomplete': 'given-name'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'autocomplete': 'family-name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com', 'autocomplete': 'email'})
    )
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'autocomplete': 'username'})
    )
    password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password (min 8 characters)', 'autocomplete': 'new-password'})
    )
    confirm_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password', 'autocomplete': 'new-password'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter your password.")
        return cleaned_data


class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address or Username', 'autocomplete': 'username'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'autocomplete': 'current-password'})
    )


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if self.user_instance and User.objects.filter(email__iexact=email).exclude(pk=self.user_instance.pk).exists():
            raise ValidationError("This email address is already used by another account.")
        return email


class UserPasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    new_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password (min 8 chars)'})
    )
    confirm_new_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password and new_password != confirm_new_password:
            self.add_error('confirm_new_password', "New passwords do not match.")
        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your registered email address', 'autocomplete': 'email'})
    )


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password (min 8 chars)'})
    )
    confirm_new_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password and new_password != confirm_new_password:
            self.add_error('confirm_new_password', "Passwords do not match.")
        return cleaned_data


# Math Calculator Forms
class GaussianForm(forms.Form):
    matrix_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 4,
            'placeholder': '1 2 -1 8\n-3 -1 2 -11\n2 1 2 -3'
        }),
        initial='1 2 -1 8\n-3 -1 2 -11\n2 1 2 -3',
        help_text='Enter augmented matrix [A|b] row by row. Separate numbers with spaces.'
    )

class VectorsForm(forms.Form):
    v1_x = forms.FloatField(initial=3.0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    v1_y = forms.FloatField(initial=4.0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    v1_z = forms.FloatField(initial=0.0, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    v2_x = forms.FloatField(initial=0.0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    v2_y = forms.FloatField(initial=2.0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    v2_z = forms.FloatField(initial=5.0, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class GramSchmidtForm(forms.Form):
    vectors_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 4,
            'placeholder': '1 1 0\n1 0 1\n0 1 1'
        }),
        initial='1 1 0\n1 0 1\n0 1 1',
        help_text='Enter each vector on a new line with space-separated components.'
    )

class CofactorForm(forms.Form):
    matrix_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 4,
            'placeholder': '3 1 2\n0 -1 4\n2 1 5'
        }),
        initial='3 1 2\n0 -1 4\n2 1 5',
        help_text='Enter a square matrix row by row.'
    )
    expand_by = forms.ChoiceField(
        choices=[('row', 'Row'), ('col', 'Column')],
        initial='row',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    index = forms.IntegerField(
        initial=1,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='1-indexed Row or Column to expand along.'
    )

class DiagonalizationForm(forms.Form):
    matrix_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 4,
            'placeholder': '4 1\n2 3'
        }),
        initial='4 1\n2 3',
        help_text='Enter a square matrix row by row.'
    )
