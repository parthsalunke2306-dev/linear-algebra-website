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

class GaloisFieldForm(forms.Form):
    question_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control font-monospace',
            'rows': 3,
            'placeholder': 'Type or paste your math question here (e.g., "Verify that F_3 = {0,1,2} forms a field under addition and multiplication modulo 3.")'
        }),
        initial='Verify that F₂ = {0,1} forms a field under addition and multiplication modulo 2.',
        help_text='Type your question, select a preset, or upload an image.'
    )
    image_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,.pdf'
        })
    )
    modulus = forms.IntegerField(
        initial=2,
        min_value=2,
        max_value=29,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    task = forms.ChoiceField(
        choices=[
            ('verify_field_axioms', 'Verify All 11 Field Axioms'),
            ('find_inverses', 'Determine Additive & Multiplicative Inverses'),
            ('construct_tables', 'Construct Addition & Multiplication Tables'),
            ('check_field', 'Determine Whether Set Forms a Field')
        ],
        initial='verify_field_axioms',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    confirm_action = forms.CharField(required=False, widget=forms.HiddenInput(), initial='detect')

    element_a = forms.IntegerField(
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    element_b = forms.IntegerField(
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    operation = forms.ChoiceField(
        choices=[('add', 'Addition (+ mod p)'), ('mul', 'Multiplication (· mod p)')],
        initial='add',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class GF2Form(GaloisFieldForm):
    """Alias for backwards compatibility."""
    pass

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

from .supabase_client import is_email_authorized

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

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not is_email_authorized(email):
            raise forms.ValidationError(f"Access Denied: '{email}' is not an authorized email address for this application.")
        return email

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

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not is_email_authorized(email):
            raise forms.ValidationError(f"Access Denied: '{email}' is not authorized to register. Please use an authorized email address.")
        return email

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
            'required': True
        })
    )

