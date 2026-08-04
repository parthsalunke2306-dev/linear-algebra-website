from django import forms
from .models import SiteSetting, TopicModule, SavedPreset

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

class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = ['site_title', 'hero_subtitle', 'curriculum_badge', 'show_code_inspector']
        widgets = {
            'site_title': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_subtitle': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'curriculum_badge': forms.TextInput(attrs={'class': 'form-control'}),
            'show_code_inspector': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TopicModuleForm(forms.ModelForm):
    class Meta:
        model = TopicModule
        fields = ['topic_code', 'title', 'unit', 'description', 'icon_class', 'icon_color_class', 'is_active', 'display_order']
        widgets = {
            'topic_code': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon_class': forms.TextInput(attrs={'class': 'form-control'}),
            'icon_color_class': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
