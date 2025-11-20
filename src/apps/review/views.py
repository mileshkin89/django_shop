from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DeleteView, UpdateView
from django.contrib import messages

from apps.catalog.models import Product
from apps.order.models import Order
from apps.review.forms import ReviewForm, ReplyForm
from apps.review.models import Review


class AuthorOrAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.get_object().author or self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to perform this action.")
        return redirect(self.get_object().product.get_absolute_url())


class AddCommentView(LoginRequiredMixin, CreateView):
    form_class = ReviewForm
    model = Review
    template_name = 'pages/catalog/product_detail.html'

    def is_author_product_buyer(self) -> bool:
        return Order.objects.filter(
            user=self.request.user,
            status__in=['Pending', 'Paid', 'Shipped', 'Delivered', 'Completed'],
            order_items__product=self.get_product(),
        ).exists()

    def is_first_authors_comment(self, product) -> bool:
        return not Review.objects.filter(
            author=self.request.user,
            product=product,
            parent__isnull=True,
        ).exists()

    def get_product(self):
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_product()

        comments = Review.objects.filter(
            product=product,
            parent__isnull=True,
            is_active=True
        ).order_by('-created_at')

        # use the current form (may contain errors) or create new
        form = context.get('form', self.get_form())

        context.update({
            'product': product,
            'comments': comments,
            'review_form': form,
            'reply_form': ReplyForm(),
        })
        return context

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        product = self.get_product()

        if not self.is_first_authors_comment(product):
            form.add_error(None, "You have already left a review for this product.")
            return self.form_invalid(form)

        if not self.is_author_product_buyer():
            form.add_error(None, "Only customers who purchased the product can leave a comment.")
            return self.form_invalid(form)

        form.instance.product = product
        form.instance.author = self.request.user
        form.instance.parent = None

        try:
            self.object = form.save()
            messages.success(self.request, 'Your comment has been added successfully!')
            return redirect(self.get_success_url())
        except Exception as e:
            form.add_error(None, f"Error saving comment: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        self.object = None
        messages.error(self.request, 'There was an error with your comment. Please try again.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        product = self.get_product()
        return f"{product.get_absolute_url()}#comment-{self.object.id}"


class AddReplyView(LoginRequiredMixin, CreateView):
    form_class = ReplyForm
    model = Review
    template_name = 'pages/catalog/product_detail.html'

    def get_product(self):
        return get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug'],
        )

    def get_parent_comment(self):
        product = self.get_product()
        return get_object_or_404(
            Review,
            id=self.kwargs['pk'],
            product=product,
            is_active=True,
            parent=None
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_product()

        comments = Review.objects.filter(
            product=product,
            parent__isnull=True,
            is_active=True
        ).order_by('-created_at')

        # use the current form (may contain errors) or create new
        form = context.get('form', self.get_form())

        context.update({
            'product': product,
            'comments': comments,
            'review_form': ReviewForm(),
            'reply_form': form,
        })
        return context

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)
        product = self.get_product()
        parent_comment = self.get_parent_comment()

        form.instance.product = product
        form.instance.author = self.request.user
        form.instance.parent = parent_comment
        form.instance.rating = None

        try:
            self.object = form.save()
            messages.success(self.request, 'Your comment has been added successfully!')
            return redirect(self.get_success_url())
        except Exception as e:
            form.add_error(None, f"Error saving comment: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        self.object = None
        messages.error(self.request, 'There was an error with your reply. Please try again.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        product = self.get_product()
        return f"{product.get_absolute_url()}#comment-{self.object.parent.id}"


class EditCommentView(LoginRequiredMixin, AuthorOrAdminRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'pages/catalog/product_detail.html'

    def get_object(self, queryset=None):
        product = get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug']
        )
        return get_object_or_404(
            Review,
            id=self.kwargs['pk'],
            product=product,
            parent__isnull=True,
            is_active=True
        )

    def form_valid(self, form):
        messages.success(self.request, "Your comment has been updated.")
        self.object = form.save()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object().product

        comments = Review.objects.filter(
            product=product,
            parent__isnull=True,
            is_active=True
        ).order_by('-created_at')

        context.update({
            'product': product,
            'comments': comments,
            'review_form': context.get('form'),
            'reply_form': ReplyForm(),
        })
        return context

    def get_success_url(self):
        return f"{self.object.product.get_absolute_url()}#comment-{self.object.id}"


class EditReplyView(LoginRequiredMixin, AuthorOrAdminRequiredMixin, UpdateView):
    model = Review
    form_class = ReplyForm
    template_name = 'pages/catalog/product_detail.html'

    def get_object(self, queryset=None):
        product = get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug']
        )
        return get_object_or_404(
            Review,
            id=self.kwargs['pk'],
            product=product,
            parent__isnull=False,
            is_active=True
        )

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Your reply has been updated.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object().product

        comments = Review.objects.filter(
            product=product,
            parent__isnull=True,
            is_active=True
        ).order_by('-created_at')

        context.update({
            'product': product,
            'comments': comments,
            'review_form': ReviewForm(),
            'reply_form': context.get('form')
        })
        return context

    def get_success_url(self):
        return f"{self.object.product.get_absolute_url()}#comment-{self.object.parent.id}"


class DeleteCommentView(LoginRequiredMixin, AuthorOrAdminRequiredMixin, DeleteView):
    model = Review
    template_name = 'pages/catalog/confirm_delete.html'

    def get_object(self, queryset=None):
        product = get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug']
        )
        return get_object_or_404(
            Review,
            id=self.kwargs['pk'],
            product=product,
            parent__isnull=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "object_name": "comment",
            "object_text": self.object.comment,
            "cancel_url": self.object.product.get_absolute_url(),
        })
        return context

    def get_success_url(self):
        return self.object.product.get_absolute_url()


class DeleteReplyView(LoginRequiredMixin, AuthorOrAdminRequiredMixin, DeleteView):
    model = Review
    template_name = 'pages/catalog/confirm_delete.html'

    def get_object(self, queryset=None):
        product = get_object_or_404(
            Product,
            is_active=True,
            slug=self.kwargs['slug']
        )
        return get_object_or_404(
            Review,
            id=self.kwargs['pk'],
            product=product,
            parent__isnull=False
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "object_name": "reply",
            "object_text": self.object.comment,
            "cancel_url": self.object.product.get_absolute_url(),
        })
        return context

    def get_success_url(self):
        return f"{self.object.product.get_absolute_url()}#comment-{self.object.parent.id}"
