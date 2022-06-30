from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Тут обязательно должен быть какой-нибудь текст. '
            'Введи что-нибудь,ну пожалуйста 😥'
        )
        self.fields['group'].empty_label = (
            'Тут можно выбрать группу, если желаете 🙂'
        )

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Введите текст',
            'group': 'Выберите группу'
        }
        help_text = {
            'text': 'Любую абракадабру',
            'group': 'Из уже существующих'
        }


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = (
            'Тут обязательно должен быть какой-нибудь текст. '
            'Оставьте положительный коммент,ну пожалуйста 😥'
        )

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Введите текст'
        }
        help_text = {
            'text': 'Можно оставить положительный коммент'
        }
