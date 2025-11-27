import random

REPLIES = [
    {"text": "Thank you for your feedback! We’re glad to hear the product met your expectations."},
    {"text": "We appreciate your review and are happy you had a positive experience."},
    {"text": "Thanks for sharing your thoughts! We're always working to improve."},
    {"text": "We're glad the product is working well for you. Thank you for choosing our store."},
    {"text": "Thank you for taking the time to leave a review! Your feedback helps us improve."},
    {"text": "We're pleased to hear you're satisfied with your purchase. Thanks for the support!"},
    {"text": "Thank you for your honest feedback. We hope the product continues to serve you well."},
    {"text": "We appreciate your input! It’s great to know the product is meeting your needs."},
    {"text": "Thanks for your review! If you have any suggestions, feel free to share."},
    {"text": "We’re happy that the product works well for you. Thank you for your trust."},
    {"text": "Your feedback means a lot to us. Thanks for choosing our product!"},
    {"text": "Thank you for the detailed review! We’re glad you’re enjoying your purchase."},
    {"text": "We appreciate your comments. Our team is always striving to improve."},
    {"text": "Thanks for your positive feedback! We’re happy to have you as a customer."},
    {"text": "We appreciate your honest review. Your satisfaction is our priority."},
    {"text": "Thanks for taking the time to share your experience! We're glad it was positive."},
    {"text": "Thank you! We're happy the product performs well for you."},
    {"text": "We appreciate your support. Let us know if you need anything else!"},
    {"text": "Thank you for your kind words. We're glad you're enjoying the product."},
    {"text": "We’re grateful for your feedback. Your experience helps us grow."},
    {"text": "Thanks for choosing our store! We're happy the product suits your needs."},
    {"text": "We appreciate your review and hope the product continues to perform well."},
    {"text": "Thank you for your feedback! We’re glad everything is working as expected."},
    {"text": "Your review is appreciated. Please reach out if you ever need assistance."},
    {"text": "We’re happy to hear you’re enjoying your purchase. Thanks for letting us know!"},
    {"text": "Thank you for taking the time to share your thoughts. We value your feedback."},
    {"text": "We appreciate your review and are glad to hear the product is useful to you."},
    {"text": "Thanks for your feedback! We're pleased the product met your expectations."},
    {"text": "Your satisfaction matters to us. Thank you for your review!"},
    {"text": "Thank you! We're always here if you have any questions or concerns."},
    {"text": "We’re happy you're satisfied with your purchase. Thanks for sharing!"},
    {"text": "Thanks for letting us know how the product works for you. We appreciate it!"},
    {"text": "We're glad to hear everything is working well. Thank you for your review."},
    {"text": "We appreciate your feedback and are happy you had a good experience."},
    {"text": "Thank you for your kind review! We're glad you like the product."},
    {"text": "Thanks for choosing our product. We’re happy it meets your expectations!"},
    {"text": "Your feedback is valuable to us. Thank you for taking the time to share it."},
    {"text": "We're pleased to hear you're enjoying the product. Thanks for the positive review!"},
    {"text": "Thank you for your review! Your support means a lot to our team."},
    {"text": "We appreciate your thoughtful feedback. Glad to hear you're satisfied!"},
]

def get_random_replies() -> str:
    """Return random "text" for reply to review."""
    reply = random.choice(REPLIES)
    return reply["text"]
