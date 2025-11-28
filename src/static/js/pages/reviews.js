class ReviewsManager {
    constructor() {
        this.productSlug = PRODUCT_SLUG;
        this.currentUserId = CURRENT_USER_ID;
        this.isAuthenticated = IS_AUTHENTICATED;
        
        console.log('ReviewsManager initialized:', {
            productSlug: this.productSlug,
            currentUserId: this.currentUserId,
            isAuthenticated: this.isAuthenticated
        });

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadReviews();
    }

    bindEvents() {
        // Review form submission
        const reviewForm = document.getElementById('review-form');
        if (reviewForm) {
            reviewForm.addEventListener('submit', (e) => this.handleReviewSubmit(e));
        }

        // Delegated events for dynamic elements
        document.addEventListener('click', (e) => {
            // Reply form toggle
            if (e.target.closest('.show-reply-form')) {
                this.toggleReplyForm(e.target.closest('.show-reply-form').dataset.reviewId);
            }

            // Reply form submission
            if (e.target.closest('.reply-form')) {
                const form = e.target.closest('.reply-form');
                if (e.target.type === 'submit' || e.target.closest('button[type="submit"]')) {
                    e.preventDefault();
                    this.handleReplySubmit(form);
                }
            }

            // Edit review
            if (e.target.closest('.edit-review')) {
                const button = e.target.closest('.edit-review');
                this.showEditReviewForm(button.dataset.reviewId);
            }

            // Delete review
            if (e.target.closest('.delete-review')) {
                const button = e.target.closest('.delete-review');
                this.deleteReview(button.dataset.reviewId);
            }

            // Edit reply
            if (e.target.closest('.edit-reply')) {
                const button = e.target.closest('.edit-reply');
                this.showEditReplyForm(button.dataset.reviewId, button.dataset.replyId);
            }

            // Delete reply
            if (e.target.closest('.delete-reply')) {
                const button = e.target.closest('.delete-reply');
                this.deleteReply(button.dataset.reviewId, button.dataset.replyId);
            }

            // Cancel edit forms
            if (e.target.closest('.cancel-edit')) {
                this.cancelEditForm(e.target);
            }

            // Cancel reply form
            if (e.target.closest('.cancel-reply-form')) {
                const form = e.target.closest('.reply-form');
                form.classList.add('is-hidden');
            }

            // Save edited review
            if (e.target.closest('.save-edit')) {
                const button = e.target.closest('.save-edit');
                this.saveEditReview(button.dataset.reviewId);
            }

            // Save edited reply
            if (e.target.closest('.save-edit-reply')) {
                const button = e.target.closest('.save-edit-reply');
                this.saveEditReply(button.dataset.reviewId, button.dataset.replyId);
            }
        });
    }

    async loadReviews() {
        try {
            console.log('Loading reviews from:', this.getApiUrl('comments_list_add'));
            const response = await fetch(this.getApiUrl('comments_list_add'));
            if (!response.ok) throw new Error('Failed to load reviews');

            const reviews = await response.json();
            console.log('Loaded reviews:', reviews);
            this.renderReviews(reviews);
        } catch (error) {
            console.error('Error loading reviews:', error);
            this.showError('Failed to load reviews');
        }
    }

    renderReviews(reviews) {
        const container = document.getElementById('reviews-list');
        if (!container) return;

        if (reviews.length === 0) {
            container.innerHTML = '<p class="text-gray">No reviews yet. Be the first to review this product!</p>';
            return;
        }

        container.innerHTML = reviews.map(review => this.renderReview(review)).join('');
    }

    renderReview(review) {
        const authorId = typeof review.author === 'object' ? review.author.id : review.author;
        const isAuthor = this.currentUserId === authorId;
        const isStaff = typeof review.author === 'object' ? review.author.is_staff : false;
        const canEdit = this.isAuthenticated && (isAuthor || isStaff);

        const authorName = typeof review.author === 'object'
            ? review.author.username
            : `User ${authorId}`;

        const formattedDate = new Date(review.created_at).toLocaleDateString();

        const replies = review.review_replies || review.replies || [];

        console.log(`Review ${review.id} debug:`, {
            review_replies: review.review_replies,
            replies: review.replies,
            repliesCount: replies.length
        });

        return `
            <div class="review-item" id="review-${review.id}">
                <div class="review-header">
                    <div>
                        <span class="review-author">${this.escapeHtml(authorName)}</span>
                        <span class="review-rating">★ ${review.rating}/5</span>
                    </div>
                    <span class="review-date">${formattedDate}</span>
                </div>
                
                <div class="review-text">${this.escapeHtml(review.text)}</div>
                
                ${canEdit ? `
                    <div class="review-actions">
                        <button class="edit-review" data-review-id="${review.id}">Edit</button>
                        <button class="delete-review" data-review-id="${review.id}">Delete</button>
                    </div>
                ` : ''}
                
                ${this.isAuthenticated ? `
                    <button class="show-reply-form text-sm" data-review-id="${review.id}">
                        Reply
                    </button>
                ` : ''}
                
                <div id="reply-form-${review.id}" class="reply-form is-hidden">
                    <textarea placeholder="Write your reply..." required></textarea>
                    <div class="reply-form-actions">
                        <button type="submit" class="button button--primary">Submit Reply</button>
                        <button type="button" class="cancel-reply-form">Cancel</button>
                    </div>
                </div>
                
                ${replies.length > 0 ? this.renderReplies(replies, review.id) : ''}
            </div>
        `;
    }

    renderReplies(replies, reviewId) {
        console.log(`Rendering ${replies.length} replies for review ${reviewId}:`, replies);

        return `
            <div class="replies-list" id="replies-${reviewId}">
                ${replies.map(reply => this.renderReply(reply, reviewId)).join('')}
            </div>
        `;
    }

    renderReply(reply, reviewId) {
        const authorId = typeof reply.author === 'object' ? reply.author.id : reply.author;
        const isAuthor = this.currentUserId === authorId;
        const isStaff = typeof reply.author === 'object' ? reply.author.is_staff : false;
        const canEdit = this.isAuthenticated && (isAuthor || isStaff);

        const authorName = typeof reply.author === 'object'
            ? reply.author.username
            : `User ${authorId}`;

        const formattedDate = new Date(reply.created_at).toLocaleDateString();

        return `
            <div class="reply-item" id="reply-${reply.id}">
                <div class="reply-header">
                    <span class="reply-author">${this.escapeHtml(authorName)}</span>
                    <span class="reply-date">${formattedDate}</span>
                </div>
                <div class="reply-text">${this.escapeHtml(reply.text)}</div>
                ${canEdit ? `
                    <div class="reply-actions">
                        <button class="edit-reply" data-review-id="${reviewId}" data-reply-id="${reply.id}">Edit</button>
                        <button class="delete-reply" data-review-id="${reviewId}" data-reply-id="${reply.id}">Delete</button>
                    </div>
                ` : ''}
            </div>
        `;
    }

    async handleReviewSubmit(e) {
        e.preventDefault();

        if (!this.isAuthenticated) {
            this.showError('Please login to submit a review');
            return;
        }

        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;

        form.classList.add('loading');
        submitButton.disabled = true;
        submitButton.textContent = 'Submitting...';

        try {
            const formData = new FormData(form);

            const reviewData = {
                rating: parseInt(formData.get('rating')),
                text: formData.get('text')
            };

            const response = await fetch(this.getApiUrl('comments_list_add'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(reviewData)
            });

            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(
                    responseData.detail ||
                    responseData.message ||
                    Object.values(responseData).flat().join(', ') ||
                    'Failed to submit review'
                );
            }

            form.reset();
            this.showSuccess('Review submitted successfully!');
            this.loadReviews();

        } catch (error) {
            console.error('Error submitting review:', error);
            this.showError(error.message);
        } finally {
            form.classList.remove('loading');
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    }

    toggleReplyForm(reviewId) {
        const form = document.getElementById(`reply-form-${reviewId}`);
        form.classList.toggle('is-hidden');
    }

    async handleReplySubmit(formElement) {
        const reviewId = formElement.id.split('-')[2];
        const textarea = formElement.querySelector('textarea');
        const submitButton = formElement.querySelector('button[type="submit"]');
        const text = textarea.value.trim();

        if (!text) {
            this.showError('Please enter a reply');
            return;
        }

        const originalText = submitButton.textContent;
        formElement.classList.add('loading');
        submitButton.disabled = true;
        submitButton.textContent = 'Submitting...';

        try {
            const response = await fetch(this.getApiUrl('replies_list_add', reviewId), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ text })
            });

            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(
                    responseData.detail ||
                    responseData.message ||
                    Object.values(responseData).flat().join(', ') ||
                    'Failed to submit reply'
                );
            }

            textarea.value = '';
            formElement.classList.add('is-hidden');
            this.showSuccess('Reply submitted successfully!');
            this.loadReviews();

        } catch (error) {
            console.error('Error submitting reply:', error);
            this.showError(error.message);
        } finally {
            formElement.classList.remove('loading');
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    }

    showEditReviewForm(reviewId) {
        const reviewElement = document.getElementById(`review-${reviewId}`);
        const reviewText = reviewElement.querySelector('.review-text').textContent;
        const reviewRating = reviewElement.querySelector('.review-rating').textContent.match(/\d+/)[0];

        reviewElement.querySelector('.review-text').style.display = 'none';
        if (reviewElement.querySelector('.review-actions')) {
            reviewElement.querySelector('.review-actions').style.display = 'none';
        }
        if (reviewElement.querySelector('.show-reply-form')) {
            reviewElement.querySelector('.show-reply-form').style.display = 'none';
        }

        const editForm = `
            <div class="edit-review-form" id="edit-review-${reviewId}">
                <div class="form-group">
                    <label>Rating:</label>
                    <select class="edit-rating">
                        <option value="1" ${reviewRating === '1' ? 'selected' : ''}>1 - Poor</option>
                        <option value="2" ${reviewRating === '2' ? 'selected' : ''}>2 - Fair</option>
                        <option value="3" ${reviewRating === '3' ? 'selected' : ''}>3 - Good</option>
                        <option value="4" ${reviewRating === '4' ? 'selected' : ''}>4 - Very Good</option>
                        <option value="5" ${reviewRating === '5' ? 'selected' : ''}>5 - Excellent</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Review:</label>
                    <textarea class="edit-text">${this.escapeHtml(reviewText)}</textarea>
                </div>
                <div class="edit-form-actions">
                    <button class="save-edit" data-review-id="${reviewId}">Save</button>
                    <button class="cancel-edit">Cancel</button>
                </div>
            </div>
        `;

        reviewElement.insertAdjacentHTML('beforeend', editForm);
    }

    async saveEditReview(reviewId) {
        const editForm = document.getElementById(`edit-review-${reviewId}`);
        const saveButton = editForm.querySelector('.save-edit');
        const rating = editForm.querySelector('.edit-rating').value;
        const text = editForm.querySelector('.edit-text').value.trim();

        if (!text) {
            this.showError('Please enter review text');
            return;
        }

        const originalText = saveButton.textContent;
        editForm.classList.add('loading');
        saveButton.disabled = true;
        saveButton.textContent = 'Saving...';

        try {
            const response = await fetch(this.getApiUrl('comment_retrieve_edit_delete', reviewId), {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ rating: parseInt(rating), text })
            });

            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(
                    responseData.detail ||
                    responseData.message ||
                    Object.values(responseData).flat().join(', ') ||
                    'Failed to update review'
                );
            }

            this.showSuccess('Review updated successfully!');
            this.loadReviews();

        } catch (error) {
            console.error('Error updating review:', error);
            this.showError(error.message);
        } finally {
            editForm.classList.remove('loading');
            saveButton.disabled = false;
            saveButton.textContent = originalText;
        }
    }

    showEditReplyForm(reviewId, replyId) {
        const replyElement = document.getElementById(`reply-${replyId}`);
        const replyText = replyElement.querySelector('.reply-text').textContent;

        replyElement.querySelector('.reply-text').style.display = 'none';
        if (replyElement.querySelector('.reply-actions')) {
            replyElement.querySelector('.reply-actions').style.display = 'none';
        }

        const editForm = `
            <div class="edit-reply-form" id="edit-reply-${replyId}">
                <div class="form-group">
                    <label>Reply:</label>
                    <textarea class="edit-text">${this.escapeHtml(replyText)}</textarea>
                </div>
                <div class="edit-form-actions">
                    <button class="save-edit-reply" data-review-id="${reviewId}" data-reply-id="${replyId}">Save</button>
                    <button class="cancel-edit">Cancel</button>
                </div>
            </div>
        `;

        replyElement.insertAdjacentHTML('beforeend', editForm);
    }

    async saveEditReply(reviewId, replyId) {
        const editForm = document.getElementById(`edit-reply-${replyId}`);
        const saveButton = editForm.querySelector('.save-edit-reply');
        const text = editForm.querySelector('.edit-text').value.trim();

        if (!text) {
            this.showError('Please enter reply text');
            return;
        }

        const originalText = saveButton.textContent;
        editForm.classList.add('loading');
        saveButton.disabled = true;
        saveButton.textContent = 'Saving...';

        try {
            const response = await fetch(this.getApiUrl('reply_retrieve_edit_delete', reviewId, replyId), {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ text })
            });

            const responseData = await response.json();

            if (!response.ok) {
                throw new Error(
                    responseData.detail ||
                    responseData.message ||
                    Object.values(responseData).flat().join(', ') ||
                    'Failed to update reply'
                );
            }

            this.showSuccess('Reply updated successfully!');
            this.loadReviews();

        } catch (error) {
            console.error('Error updating reply:', error);
            this.showError(error.message);
        } finally {
            editForm.classList.remove('loading');
            saveButton.disabled = false;
            saveButton.textContent = originalText;
        }
    }

    async deleteReview(reviewId) {
        if (!confirm('Are you sure you want to delete this review?')) {
            return;
        }

        try {
            const response = await fetch(this.getApiUrl('comment_retrieve_edit_delete', reviewId), {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(
                    errorData.detail ||
                    errorData.message ||
                    'Failed to delete review'
                );
            }

            this.showSuccess('Review deleted successfully!');
            this.loadReviews();

        } catch (error) {
            console.error('Error deleting review:', error);
            this.showError(error.message);
        }
    }

    async deleteReply(reviewId, replyId) {
        if (!confirm('Are you sure you want to delete this reply?')) {
            return;
        }

        try {
            const response = await fetch(this.getApiUrl('reply_retrieve_edit_delete', reviewId, replyId), {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(
                    errorData.detail ||
                    errorData.message ||
                    'Failed to delete reply'
                );
            }

            this.showSuccess('Reply deleted successfully!');
            this.loadReviews();

        } catch (error) {
            console.error('Error deleting reply:', error);
            this.showError(error.message);
        }
    }

    cancelEditForm(button) {
        const form = button.closest('.edit-review-form, .edit-reply-form');
        const parentElement = form.closest('.review-item, .reply-item');

        if (form.classList.contains('edit-review-form')) {
            parentElement.querySelector('.review-text').style.display = 'block';
            if (parentElement.querySelector('.review-actions')) {
                parentElement.querySelector('.review-actions').style.display = 'flex';
            }
            if (parentElement.querySelector('.show-reply-form')) {
                parentElement.querySelector('.show-reply-form').style.display = 'block';
            }
        } else {
            parentElement.querySelector('.reply-text').style.display = 'block';
            if (parentElement.querySelector('.reply-actions')) {
                parentElement.querySelector('.reply-actions').style.display = 'flex';
            }
        }

        form.remove();
    }

    // Utility methods
    getApiUrl(viewName, reviewId = null, replyId = null) {
        const urls = {
            comments_list_add: `/api/products/${this.productSlug}/comments/`,
            comment_retrieve_edit_delete: `/api/products/${this.productSlug}/comments/${reviewId}/`,
            replies_list_add: `/api/products/${this.productSlug}/comments/${reviewId}/replies/`,
            reply_retrieve_edit_delete: `/api/products/${this.productSlug}/comments/${reviewId}/replies/${replyId}/`
        };
        return urls[viewName];
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showMessage(message, type) {
        const existingMessages = document.querySelectorAll('.error-message, .success-message');
        existingMessages.forEach(msg => msg.remove());

        const messageDiv = document.createElement('div');
        messageDiv.className = type === 'error' ? 'error-message' : 'success-message';
        messageDiv.textContent = message;

        const reviewsSection = document.querySelector('.reviews-section');
        reviewsSection.insertBefore(messageDiv, reviewsSection.firstChild);

        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.reviewsManager = new ReviewsManager();
});