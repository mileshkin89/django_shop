from datetime import datetime

from django import forms
from .models import Product, SubCategory, MasterCategory


class ProductForm(forms.ModelForm):
    master_category = forms.ModelChoiceField(
        queryset=MasterCategory.objects.all(),
        label='Master Category',
        required=True,
    )
    sub_category = forms.ModelChoiceField(
        queryset=SubCategory.objects.none(),
        label='Sub Category',
        required=True,
    )

    class Meta:
        model = Product
        fields = [
            'master_category',
            'sub_category',
            'article_type',
            'product_display_name',
            'usage_type',
            'gender',
            'season',
            'year',
            'image_url',
            'base_colour',
        ]
        widgets = {
            'product_display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'article_type': forms.Select(attrs={'class': 'form-select'}),
            'usage_type': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'season': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'base_colour': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'product_display_name': 'Product name',
            'article_type': 'Type of product',
            'usage_type': 'Type of use',
            'gender': 'Gender',
            'season': 'Season',
            'year': 'Year of release',
            'image_url': 'Image link',
            'base_colour': 'Main color',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'master_category' in self.data:
            try:
                master_id = int(self.data.get('master_category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(master_category_id=master_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.article_type:
            self.fields['sub_category'].queryset = SubCategory.objects.filter(
                master_category=self.instance.article_type.sub_category.master_category
            ).order_by('name')

            self.fields['master_category'].initial = (
                self.instance.article_type.sub_category.master_category
            )

            self.fields['article_type'].queryset = self.instance.article_type.__class__.objects.filter(
                sub_category=self.instance.article_type.sub_category
            ).order_by('name')

        if 'sub_category' in self.data:
            try:
                sub_id = int(self.data.get('sub_category'))
                self.fields['article_type'].queryset = self.instance.article_type.__class__.objects.filter(sub_category_id=sub_id).order_by('name')
            except (ValueError, TypeError):
                pass


    def clean_article_type(self):
        """
        Validate that the chosen article_type belongs to the selected sub_category.
        Runs automatically when Django cleans the 'article_type' field.
        """
        article_type = self.cleaned_data.get('article_type')
        sub_category = self.cleaned_data.get('sub_category')

        if article_type and sub_category:
            if article_type.sub_category != sub_category:
                raise forms.ValidationError(
                    "The current type does not belong to this subcategory."
                )

        return article_type

    def clean_year(self):
        year = self.cleaned_data.get('year')

        if year < 1999:
            raise forms.ValidationError(
                "The item is too vintage. Let's say it's older than 1999."
            )
        elif year > datetime.now().year:
            raise forms.ValidationError(
                "We do not sell products from the future."
            )


    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
        return instance