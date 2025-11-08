from django.db import models
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField

from .choices import SeasonChoices, GenderChoices


class MasterCategory(models.Model):
    name = models.TextField(unique=True)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "catalog:product_list_by_master",
            kwargs={"master_slug": self.slug}
        )


class SubCategory(models.Model):
    master_category = models.ForeignKey(
        'MasterCategory',
        on_delete=models.RESTRICT,
        related_name='sub_categories',
    )
    name = models.TextField()
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)

    class Meta:
        unique_together = (('master_category', 'name'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "catalog:product_list_by_sub",
            kwargs={
                "master_slug": self.master_category.slug,
                "sub_slug": self.slug,
            },
        )


class ArticleType(models.Model):
    sub_category = models.ForeignKey(
        'SubCategory',
        on_delete=models.RESTRICT,
        related_name='article_types',
    )
    name = models.TextField()
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)

    class Meta:
        unique_together = (('sub_category', 'name'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "catalog:product_list_by_article",
            kwargs={
                "master_slug": self.sub_category.master_category.slug,
                "sub_slug": self.sub_category.slug,
                "article_slug": self.slug,
            },
        )


class BaseColour(models.Model):
    name = models.TextField(unique=True)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)

    def __str__(self):
        return self.name


class Season(models.Model):
    name = models.CharField(max_length=10, choices=SeasonChoices.choices, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)

    def __str__(self):
        return self.name


class UsageType(models.Model):
    name = models.TextField(unique=True)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.IntegerField(unique=True, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, null=True, blank=True)
    year = models.SmallIntegerField(null=True, blank=True)
    product_display_name = models.TextField()
    description = models.TextField(null=True, blank=True)
    image_url = models.TextField(null=True, blank=True)
    slug = AutoSlugField(
        populate_from=['product_display_name', 'product_id'],
        unique=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    article_type = models.ForeignKey(
        'ArticleType',
        on_delete=models.RESTRICT,
        related_name='products',
    )
    base_colour = models.ForeignKey(
        'BaseColour',
        on_delete=models.RESTRICT,
        related_name='products',
        null=True,
        blank=True
    )
    season = models.ForeignKey(
        'Season',
        on_delete=models.RESTRICT,
        related_name='products',
        null=True,
        blank=True
    )
    usage_type = models.ForeignKey(
        'UsageType',
        on_delete=models.RESTRICT,
        related_name='products',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-year', '-updated_at', '-created_at']

    def __str__(self):
        return self.product_display_name or f'Product {self.product_id}'

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})
