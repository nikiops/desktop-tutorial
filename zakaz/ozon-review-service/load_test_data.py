#!/usr/bin/env python3
"""Load test data into the database"""
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.review import Review

# Test reviews
test_reviews = [
    {
        "ozon_review_id": "test-001",
        "product_id": "123456",
        "product_name": "Тестовый товар 1",
        "rating": 5,
        "text": "Отличный товар! Рекомендую всем.",
        "customer_name": "Иван",
        "sentiment": "positive",
        "answered": False,
    },
    {
        "ozon_review_id": "test-002",
        "product_id": "123456",
        "product_name": "Тестовый товар 1",
        "rating": 3,
        "text": "Нормально, но можно лучше. Цена высокая.",
        "customer_name": "Мария",
        "sentiment": "neutral",
        "answered": False,
    },
    {
        "ozon_review_id": "test-003",
        "product_id": "789012",
        "product_name": "Тестовый товар 2",
        "rating": 1,
        "text": "Не соответствует описанию! Полный разочаровтель.",
        "customer_name": "Петр",
        "sentiment": "negative",
        "answered": False,
    },
    {
        "ozon_review_id": "test-004",
        "product_id": "789012",
        "product_name": "Тестовый товар 2",
        "rating": 5,
        "text": "Спасибо за отличный товар и быструю доставку!",
        "customer_name": "Анна",
        "sentiment": "positive",
        "answered": True,
    },
    {
        "ozon_review_id": "test-005",
        "product_id": "456789",
        "product_name": "Тестовый товар 3",
        "rating": 4,
        "text": "Хороший товар, доставка долгая.",
        "customer_name": "Ольга",
        "sentiment": "positive",
        "answered": False,
    }
]

def load_test_data():
    """Load test data into database"""
    db = SessionLocal()
    try:
        # Clear existing test data
        db.query(Review).filter(Review.ozon_review_id.like("test-%")).delete()
        db.commit()
        
        # Add test reviews
        for review_data in test_reviews:
            review = Review(**review_data)
            db.add(review)
        
        db.commit()
        print(f"✅ Loaded {len(test_reviews)} test reviews")
        
        # Show stats
        total = db.query(Review).count()
        positive = db.query(Review).filter_by(sentiment="positive").count()
        neutral = db.query(Review).filter_by(sentiment="neutral").count()
        negative = db.query(Review).filter_by(sentiment="negative").count()
        
        print(f"📊 Total reviews: {total}")
        print(f"   👍 Positive: {positive}")
        print(f"   ➡️  Neutral: {neutral}")
        print(f"   👎 Negative: {negative}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_test_data()
