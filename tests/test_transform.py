import pytest
import pandas as pd
from utils.transform import transform_data

def test_transform_data_success():
    """Test transform_data dengan data valid."""
    data = pd.DataFrame({
        'title': ['T-Shirt', 'Jeans'],
        'price': ['$10', '$20'],
        'rating': ['Rating: 4.5 / 5', 'Rating: 3.0 / 5'],
        'colors': ['Colors: 3', 'Colors: 2'],
        'size': ['Size: M', 'Size: L'],
        'gender': ['Gender: Male', 'Gender: Female'],
        'timestamp': ['2025-05-19 12:00:00', '2025-05-19 12:00:00']
    })
    df = transform_data(data)
    assert len(df) == 2
    assert df['price'].iloc[0] == 160000.0
    assert df['rating'].iloc[0] == 4.5
    assert df['colors'].iloc[0] == 3
    assert df['size'].iloc[0] == 'M'
    assert df['gender'].iloc[0] == 'Male'

def test_transform_data_invalid_rating():
    """Test transform_data dengan rating invalid."""
    data = pd.DataFrame({
        'title': ['T-Shirt', 'Jeans'],
        'price': ['$10', '$20'],
        'rating': ['⭐ Invalid Rating', 'Rating: 3.0 / 5'],
        'colors': ['Colors: 3', 'Colors: 2'],
        'size': ['Size: M', 'Size: L'],
        'gender': ['Gender: Male', 'Gender: Female'],
        'timestamp': ['2025-05-19 12:00:00', '2025-05-19 12:00:00']
    })
    df = transform_data(data)
    assert len(df) == 1
    assert df['rating'].iloc[0] == 3.0

def test_transform_data_empty():
    """Test transform_data dengan data kosong setelah validasi."""
    data = pd.DataFrame({
        'title': ['Unknown Title'],
        'price': ['Price Not Available'],
        'rating': ['No Rating'],
        'colors': ['No Color Info'],
        'size': ['No Size Info'],
        'gender': ['No Gender Info'],
        'timestamp': ['2025-05-19 12:00:00']
    })
    with pytest.raises(ValueError, match="DataFrame is empty after validation"):
        transform_data(data)