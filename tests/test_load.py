import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, ANY
import os
from utils.load import save_to_csv, save_to_google_sheets, save_to_postgres

@pytest.fixture
def sample_df():
    """Fixture untuk DataFrame contoh."""
    return pd.DataFrame({
        'title': ['T-Shirt', 'Jeans'],
        'price': [160000.0, 320000.0],
        'rating': [4.5, 3.0],
        'colors': [3, 2],
        'size': ['M', 'L'],
        'gender': ['Male', 'Female'],
        'timestamp': ['2025-05-19 17:00:00', '2025-05-19 17:00:00']
    })

def test_save_to_csv_success(sample_df, tmp_path):
    """Test save_to_csv dengan data valid."""
    file_path = tmp_path / 'test.csv'
    save_to_csv(sample_df, file_path)
    assert file_path.exists()
    df = pd.read_csv(file_path)
    assert len(df) == 2
    assert df.iloc[0]['title'] == 'T-Shirt'

def test_save_to_csv_empty():
    """Test save_to_csv dengan DataFrame kosong."""
    df = pd.DataFrame()
    with pytest.raises(ValueError, match="DataFrame is empty, cannot save to CSV"):
        save_to_csv(df, 'test.csv')

@patch('os.path.exists', return_value=True)
@patch('utils.load.build')
@patch('utils.load.Credentials.from_service_account_file')
def test_save_to_google_sheets_success(mock_credentials, mock_build, mock_exists, sample_df):
    """Test save_to_google_sheets dengan data valid."""
    # Setup mock objects
    mock_credentials_instance = MagicMock()
    mock_credentials.return_value = mock_credentials_instance
    
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    
    mock_spreadsheets = MagicMock()
    mock_service.spreadsheets.return_value = mock_spreadsheets
    
    mock_values = MagicMock()
    mock_spreadsheets.values.return_value = mock_values
    
    mock_clear = MagicMock()
    mock_values.clear.return_value = mock_clear
    mock_clear.execute.return_value = {}
    
    mock_update = MagicMock()
    mock_values.update.return_value = mock_update
    mock_update.execute.return_value = {}

    # Call the function
    save_to_google_sheets(sample_df, 'test_spreadsheet_id', 'test_credentials.json')
    
    # Assertions
    mock_exists.assert_called_once_with('test_credentials.json')
    mock_credentials.assert_called_once_with(
        'test_credentials.json', 
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    mock_build.assert_called_once_with('sheets', 'v4', credentials=mock_credentials_instance)
    mock_values.clear.assert_called_once()
    mock_values.update.assert_called_once()

@patch('os.path.exists', return_value=True)
@patch('utils.load.build')
@patch('utils.load.Credentials.from_service_account_file')
def test_save_to_google_sheets_error(mock_credentials, mock_build, mock_exists, sample_df):
    """Test save_to_google_sheets dengan error API."""
    mock_credentials.return_value = MagicMock()
    mock_build.side_effect = Exception("Google Sheets API error")
    
    # Use the exact error message that matches the implementation
    with pytest.raises(Exception, match="Failed to save to Google Sheets: Google Sheets API error"):
        save_to_google_sheets(sample_df, 'test_spreadsheet_id', 'test_credentials.json')
    
    mock_exists.assert_called_once_with('test_credentials.json')
    mock_credentials.assert_called_once_with(
        'test_credentials.json', 
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    mock_build.assert_called_once()

@patch('sqlalchemy.create_engine')
def test_save_to_postgres_success(mock_create_engine, sample_df):
    """Test save_to_postgres dengan data valid."""
    # Setup mock objects
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    
    # Create a mock for the to_sql method
    with patch.object(pd.DataFrame, 'to_sql', return_value=None) as mock_to_sql:
        # Call the function
        save_to_postgres(sample_df, 'products', 'postgresql+psycopg2://test:test@localhost/test')
        
        # Assertions
        mock_create_engine.assert_called_once_with('postgresql+psycopg2://test:test@localhost/test')
        mock_to_sql.assert_called_once_with('products', mock_conn, if_exists='replace', index=False)
        mock_engine.connect.assert_called_once()

@patch('sqlalchemy.create_engine')
def test_save_to_postgres_error(mock_create_engine, sample_df):
    """Test save_to_postgres dengan error koneksi."""
    # Make create_engine raise an exception
    mock_create_engine.side_effect = Exception("Database connection error")
    
    # Use the exact error message that matches the implementation
    with pytest.raises(Exception, match="Failed to save to PostgreSQL: Database connection error"):
        save_to_postgres(sample_df, 'products', 'postgresql+psycopg2://test:test@localhost/test')
    
    mock_create_engine.assert_called_once_with('postgresql+psycopg2://test:test@localhost/test')