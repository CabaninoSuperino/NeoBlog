from django import forms
from .models import Post, SubPost
from django.forms import inlineformset_factory


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }


class SubPostForm(forms.ModelForm):
    class Meta:
        model = SubPost
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем класс к каждому полю
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


SubPostFormSet = inlineformset_factory(
    Post,
    SubPost,
    form=SubPostForm,
    fields=['title', 'body'],
    extra=1,
    can_delete=True
)

