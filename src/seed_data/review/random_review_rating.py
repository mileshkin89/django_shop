import random

REVIEWS = [
    {"text": "Great quality and exactly as described. I’m very happy with this purchase.", "rating": 5},
    {"text": "The product exceeded my expectations. Fast delivery and excellent packaging.", "rating": 5},
    {"text": "Works perfectly so far. I would definitely recommend it to others.", "rating": 5},
    {"text": "Good value for the price. Not perfect, but overall I’m satisfied.", "rating": 4},
    {"text": "The item is decent and does what it should. A few minor issues, but nothing serious.", "rating": 4},
    {"text": "Pretty good overall. The design could be better, but it’s functional.", "rating": 4},
    {"text": "It's okay, nothing special. Does the job but feels a bit overpriced.", "rating": 3},
    {"text": "Average quality. I expected a bit more considering the reviews.", "rating": 3},
    {"text": "The product is fine, but it arrived later than promised. Mixed feelings.", "rating": 3},
    {"text": "Not very impressed. It works, but the build quality feels cheap.", "rating": 2},
    {"text": "The item doesn’t match the description fully. I wouldn’t buy it again.", "rating": 2},
    {"text": "The product arrived damaged, and customer support was slow to respond.", "rating": 2},
    {"text": "Very disappointing. The item stopped working after a few days.", "rating": 1},
    {"text": "Terrible experience. Completely not as described and very poor quality.", "rating": 1},
    {"text": "I regret buying this product. It’s unusable and a waste of money.", "rating": 1},
    {"text": "Surprisingly good for the price. I wasn’t expecting much, but it performs well.", "rating": 4},
    {"text": "The item is lightweight and easy to use. Exactly what I needed.", "rating": 5},
    {"text": "Mediocre performance. It works but has several annoying flaws.", "rating": 3},
    {"text": "Poor packaging and the product feels fragile. Not recommended.", "rating": 2},
    {"text": "Absolutely fantastic! I will definitely purchase from this store again.", "rating": 5},
    {"text": "The product arrived on time and was packaged very well. It feels sturdy and performs smoothly in daily use. I wouldn’t call it amazing, but it definitely gets the job done without issues.", "rating": 4},
    {"text": "I’ve been using this item for about a week now and it works as advertised. The build quality is decent, though I noticed a few small imperfections. Overall, it's a solid choice for the price.", "rating": 4},
    {"text": "This item is good, but not exceptional. I expected a bit more based on the reviews. Still, it performs reliably and should be fine for most people.", "rating": 3},
    {"text": "Really impressed with how smooth and efficient this product is. It fits perfectly into my daily routine and makes tasks easier. Definitely worth the money, and I’d consider buying it again.", "rating": 5},
    {"text": "The product is well-made and feels premium. I’ve tested it in several scenarios and it consistently delivers good results. Minor improvements could make it even better, but I'm satisfied overall.", "rating": 4},
    {"text": "At first I wasn’t sure about the purchase, but after using it for several days, I’m pleasantly surprised. It functions reliably and looks nice too. Not perfect, but a strong performer for its category.", "rating": 4},
    {"text": "The overall experience with this product has been positive. It’s simple to use, and the instructions were clear. While it’s not groundbreaking, it does exactly what it promises.", "rating": 4},
    {"text": "A very helpful product that exceeded a few of my expectations. The build quality is solid and it feels durable. I’m confident it will last a long time, and I would recommend it to friends.", "rating": 5},
    {"text": "Decent item with reasonable performance. It works fine for everyday tasks, although it lacks some advanced features. Good for those who need something simple and functional.", "rating": 3},
    {"text": "I’m quite happy with this purchase. The product performs well and has a clean, modern design. It could be slightly more efficient, but overall it's a very good option for the price.", "rating": 4},
]

def get_random_review_rating() -> tuple[str, int]:
    """Return random 'text' and 'rating' for review."""
    review = random.choice(REVIEWS)
    return review["text"], review["rating"]
