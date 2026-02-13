import pytest
import os
import sys
from unittest.mock import Mock, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_gemini_client():
    """Mock Gemini API client."""
    mock = MagicMock()
    mock.generate_content.return_value = MagicMock(text="Test response")
    return mock

@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        'name': 'Samsung Galaxy A54',
        'price': 45000,
        'seller': 'Test Seller',
        'platform': 'Jumia',
        'rating': 4.5
    }

@pytest.fixture
def sample_recommendation():
    """Sample recommendation for testing."""
    return {
        'product_name': 'Test Product',
        'best_option': {
            'price_kes': 50000,
            'seller': 'Test Seller',
            'platform': 'Jumia'
        },
        'confidence_score': 0.85,
        'human_approval_required': False
    }
