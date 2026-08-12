from django import forms

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

class GF2Form(forms.Form):
    element_a = forms.IntegerField(
        initial=1,
        widget=forms.Select(attrs={'class': 'form-select'}, choices=[(0, '0'), (1, '1')])
    )
    element_b = forms.IntegerField(
        initial=1,
        widget=forms.Select(attrs={'class': 'form-select'}, choices=[(0, '0'), (1, '1')])
    )
    operation = forms.ChoiceField(
        choices=[('add', 'Addition (+ mod 2 / XOR)'), ('mul', 'Multiplication (· mod 2 / AND)')],
        initial='add',
        widget=forms.Select(attrs={'class': 'form-select'})
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


# ------------------------------------------------------------------------------
# AUTHENTICATION FORMS (Supabase Auth Integration)
# ------------------------------------------------------------------------------

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'required': True
        })
    )

class SignUpForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Alex Mercer',
            'required': True
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'required': True
        })
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'At least 8 characters',
            'required': True
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'required': True
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please re-enter passwords.")
        return cleaned_data

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'required': True
        })
    )

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'required': True
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'required': True
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get("new_password")
        pwd2 = cleaned_data.get("confirm_password")
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class ProfileUpdateForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': True,
            'placeholder': 'Enter your full name'
        })
    )
    avatar_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control d-none',
            'id': 'avatarFileInput',
            'accept': 'image/png, image/jpeg, image/webp, image/gif, image/svg+xml'
        })
    )
    avatar_preset = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'avatarPresetInput'})
    )
    avatar_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'avatarUrlInput'})
    )
    remove_avatar = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'removeAvatarInput'})
    )

    def clean_avatar_file(self):
        file = self.cleaned_data.get('avatar_file')
        if not file:
            return None
        
        # Max file size: 5MB
        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            raise forms.ValidationError("Profile picture file size cannot exceed 5MB.")
        
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg')
        if not file.name.lower().endswith(valid_extensions):
            raise forms.ValidationError("Supported image formats are JPG, PNG, WEBP, GIF, and SVG.")
        
        return file


