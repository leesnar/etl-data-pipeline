import pytest
import pandas as pd
import logging
from unittest.mock import Mock, patch, MagicMock
import requests
from bs4 import BeautifulSoup
from utils.extract import scrape_main, extract_data

@patch('requests.get')
def test_scrape_main_success(mock_get):
    """Test scrape_main dengan data valid."""
    # Mock response for main page
    main_response = Mock()
    main_response.text = """
    <div class="collection-card">
        <h3 class="product-title">T-Shirt</h3>
        <div class="price-container">$10</div>
        <p>Rating: 4.5 / 5</p>
        <p>Colors: 3</p>
        <p>Size: M</p>
        <p>Gender: Male</p>
    </div>
    """
    main_response.raise_for_status.return_value = None
    
    # Mock response for page 2
    page2_response = Mock()
    page2_response.text = """
    <div class="collection-card">
        <h3 class="product-title">Jeans</h3>
        <div class="price-container">$25</div>
        <p>Rating: 4.0 / 5</p>
        <p>Colors: 2</p>
        <p>Size: L</p>
        <p>Gender: Female</p>
    </div>
    """
    page2_response.raise_for_status.return_value = None
    
    # Configure mock to return different responses for different URLs
    mock_get.side_effect = lambda url, headers, timeout: (
        main_response if url == "https://fashion-studio.dicoding.dev/" else page2_response
    )

    df = scrape_main(url_base='https://fashion-studio.dicoding.dev/page{}', max_pages=2)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.iloc[0]['title'] == 'T-Shirt'
    assert df.iloc[0]['price'] == '$10'
    assert df.iloc[0]['rating'] == 'Rating: 4.5 / 5'
    assert df.iloc[0]['colors'] == 'Colors: 3'
    assert df.iloc[0]['size'] == 'Size: M'
    assert df.iloc[0]['gender'] == 'Gender: Male'
    assert df.iloc[1]['title'] == 'Jeans'
    assert df.iloc[1]['gender'] == 'Gender: Female'

@patch('requests.get')
def test_scrape_main_request_error(mock_get):
    """Test scrape_main ketika request gagal."""
    mock_get.side_effect = requests.RequestException("Connection error")
    with pytest.raises(requests.RequestException, match="All pages failed: Connection error"):
        scrape_main(url_base='https://test.com/page{}', max_pages=1)

@patch('requests.get')
def test_scrape_main_no_products(mock_get):
    """Test scrape_main ketika tidak ada produk ditemukan."""
    mock_response = Mock()
    mock_response.text = "<html><body>No products</body></html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    df = scrape_main(url_base='https://test.com/page{}', max_pages=1)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0

@patch('requests.get')
def test_scrape_main_missing_attributes(mock_get):
    """Test scrape_main ketika beberapa atribut produk tidak ada."""
    mock_response = Mock()
    mock_response.text = """
    <div class="collection-card">
        <h3 class="product-title">T-Shirt</h3>
        <div class="price-container">$10</div>
        <!-- Missing rating, colors, size, gender -->
    </div>
    """
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    df = scrape_main(url_base='https://test.com/page{}', max_pages=1)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]['title'] == 'T-Shirt'
    assert df.iloc[0]['price'] == '$10'
    assert df.iloc[0]['rating'] == 'No Rating'
    assert df.iloc[0]['colors'] == 'No Color Info'
    assert df.iloc[0]['size'] == 'No Size Info'
    assert df.iloc[0]['gender'] == 'No Gender Info'

@patch('utils.extract.scrape_main')
def test_extract_data(mock_scrape_main):
    """Test extract_data fungsi."""
    # Mock data yang akan dikembalikan oleh scrape_main
    mock_data = pd.DataFrame({
        'title': ['T-Shirt', 'Jeans'],
        'price': ['$10', '$25'],
        'rating': ['Rating: 4.5 / 5', 'Rating: 4.0 / 5'],
        'colors': ['Colors: 3', 'Colors: 2'],
        'size': ['Size: M', 'Size: L'],
        'gender': ['Gender: Male', 'Gender: Female'],
        'timestamp': ['2025-05-19 10:00:00', '2025-05-19 10:00:00']
    })
    mock_scrape_main.return_value = mock_data
    
    # Panggil fungsi extract_data
    result = extract_data()
    
    # Verifikasi bahwa scrape_main dipanggil
    mock_scrape_main.assert_called_once()
    
    # Verifikasi hasil
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result['title']) == ['T-Shirt', 'Jeans']

@patch('requests.get')
def test_scrape_main_page_error(mock_get):
    """Test scrape_main ketika halaman tertentu gagal tetapi keseluruhan proses berhasil."""
    # Mock untuk halaman utama berhasil
    main_response = Mock()
    main_response.text = """
    <div class="collection-card">
        <h3 class="product-title">T-Shirt</h3>
        <div class="price-container">$10</div>
        <p>Rating: 4.5 / 5</p>
        <p>Colors: 3</p>
        <p>Size: M</p>
        <p>Gender: Male</p>
    </div>
    """
    main_response.raise_for_status.return_value = None
    
    # Definisikan side effect untuk mock_get
    def side_effect(url, headers, timeout):
        if url == "https://fashion-studio.dicoding.dev/":
            return main_response
        elif url == "https://fashion-studio.dicoding.dev/page2":
            raise requests.RequestException("Error on page 2")
        else:
            page3_response = Mock()
            page3_response.text = """
            <div class="collection-card">
                <h3 class="product-title">Hat</h3>
                <div class="price-container">$15</div>
                <p>Rating: 5.0 / 5</p>
                <p>Colors: 1</p>
                <p>Size: One Size</p>
                <p>Gender: Unisex</p>
            </div>
            """
            page3_response.raise_for_status.return_value = None
            return page3_response
    
    mock_get.side_effect = side_effect
    
    # Uji dengan max_pages=3
    df = scrape_main(url_base='https://fashion-studio.dicoding.dev/page{}', max_pages=3)
    
    # Verifikasi hasil
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2  # Should have products from main page and page 3 (page 2 failed)
    assert 'Hat' in df['title'].values

@patch('requests.get')
def test_scrape_main_empty_products(mock_get):
    """Test scrape_main ketika halaman berisi produk kosong."""
    # Mock response untuk halaman utama
    mock_response = Mock()
    mock_response.text = "<html><body><div class='collection-card'></div></body></html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    df = scrape_main(url_base='https://test.com/page{}', max_pages=1)
    assert isinstance(df, pd.DataFrame)
    # Masih ada satu produk tapi dengan nilai default
    assert len(df) == 1
    assert df.iloc[0]['title'] == 'Unknown Title'
    assert df.iloc[0]['price'] == 'Price Not Available'

@patch('logging.info')
@patch('utils.extract.scrape_main')
def test_extract_data_logging(mock_scrape_main, mock_logging):
    """Test log messages pada extract_data."""
    # Setup mock data
    mock_data = pd.DataFrame({
        'title': ['T-Shirt', 'Jeans'],
        'price': ['$10', '$25'],
        'rating': ['Rating: 4.5 / 5', 'Rating: 4.0 / 5'],
        'colors': ['Colors: 3', 'Colors: 2'],
        'size': ['Size: M', 'Size: L'],
        'gender': ['Gender: Male', 'Gender: Female'],
        'timestamp': ['2025-05-19 10:00:00', '2025-05-19 10:00:00']
    })
    mock_scrape_main.return_value = mock_data
    
    # Call extract_data
    result = extract_data()
    
    # Verify logging calls
    assert mock_logging.call_count >= 2
    mock_logging.assert_any_call("Starting extraction")
    mock_logging.assert_any_call(f"Total scraped data: {len(result)} rows")