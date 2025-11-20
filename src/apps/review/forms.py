from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...'
            })
        }
        labels = {
            'rating': 'Rating',
            'comment': 'Comment',
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('comment',)
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Write your reply here...'
            })
        }
        labels = {
            'comment': 'Reply'
        }