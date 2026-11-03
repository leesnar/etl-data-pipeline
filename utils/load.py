import os
import pandas as pd
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import sqlalchemy

def save_to_csv(df, file_path):
    """
    Menyimpan DataFrame ke file CSV.
    
    Args:
        df (pandas.DataFrame): DataFrame yang akan disimpan
        file_path (str): Path untuk menyimpan file CSV
    
    Raises:
        ValueError: Jika DataFrame kosong
    """
    if df.empty:
        raise ValueError("DataFrame is empty, cannot save to CSV")
    
    try:
        df.to_csv(file_path, index=False)
        logging.info(f"Successfully saved data to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save to CSV: {str(e)}")
        raise Exception(f"Failed to save to CSV: {str(e)}")

def save_to_google_sheets(df, spreadsheet_id, credentials_file):
    """
    Menyimpan DataFrame ke Google Sheets.
    
    Args:
        df (pandas.DataFrame): DataFrame yang akan disimpan
        spreadsheet_id (str): ID dari Google Spreadsheet
        credentials_file (str): Path ke file kredensial Google API
    
    Raises:
        ValueError: Jika DataFrame kosong atau file kredensial tidak ditemukan
    """
    if df.empty:
        raise ValueError("DataFrame is empty, cannot save to Google Sheets")
    
    if not os.path.exists(credentials_file):
        raise ValueError(f"Credentials file {credentials_file} not found")
    
    try:
        # Persiapkan data untuk Google Sheets
        # Tambahkan header dataframe sebagai baris pertama
        values = [df.columns.tolist()]
        values.extend(df.values.tolist())
        
        # Autentikasi dengan Google Sheets API
        creds = Credentials.from_service_account_file(
            credentials_file, 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)
        
        # Bersihkan sheet dahulu (jika ada data sebelumnya)
        sheet_range = "Sheet1"
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=sheet_range
        ).execute()
        
        # Update sheet dengan data baru
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption="RAW",
            body={"values": values}
        ).execute()
        
        logging.info(f"Successfully saved data to Google Sheets with ID {spreadsheet_id}")
    except Exception as e:
        logging.error(f"Failed to save to Google Sheets: {str(e)}")
        raise Exception(f"Failed to save to Google Sheets: {str(e)}")

def save_to_postgres(df, table_name, connection_string):
    """
    Menyimpan DataFrame ke database PostgreSQL.
    
    Args:
        df (pandas.DataFrame): DataFrame yang akan disimpan
        table_name (str): Nama tabel di database
        connection_string (str): Connection string untuk PostgreSQL
    
    Raises:
        ValueError: Jika DataFrame kosong
    """
    if df.empty:
        raise ValueError("DataFrame is empty, cannot save to PostgreSQL")
    
    try:
        engine = sqlalchemy.create_engine(connection_string)
        with engine.connect() as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
        logging.info(f"Successfully saved data to PostgreSQL table {table_name}")
    except Exception as e:
        logging.error(f"Failed to save to PostgreSQL: {str(e)}")
        raise Exception(f"Failed to save to PostgreSQL: {str(e)}")