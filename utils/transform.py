import pandas as pd
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def transform_data(df):
    """Transformasi data untuk menghapus invalid, null, duplikat, dan format ulang.
    
    Args:
        df (pd.DataFrame): DataFrame dari tahap extract.
    
    Returns:
        pd.DataFrame: DataFrame yang sudah dibersihkan dan diformat.
    
    Raises:
        ValueError: Jika transformasi gagal atau menghasilkan DataFrame kosong.
    """
    try:
        # Salin DataFrame untuk menghindari SettingWithCopyWarning
        df = df.copy()
        
        # Simpan data mentah untuk debugging
        df.to_csv('raw_data.csv', index=False)
        logging.info("Saved raw data to raw_data.csv")
        
        # Hapus duplikat dan null
        initial_rows = len(df)
        df = df.drop_duplicates().dropna()
        logging.info(f"Removed {initial_rows - len(df)} duplicates and nulls")
        if df.empty:
            raise ValueError("DataFrame is empty after removing duplicates and nulls")
        
        # Log nilai unik untuk debugging
        logging.info(f"Unique titles: {df['title'].unique()[:5]}")
        logging.info(f"Unique prices: {df['price'].unique()[:5]}")
        logging.info(f"Unique ratings: {df['rating'].unique()[:5]}")
        logging.info(f"Unique colors: {df['colors'].unique()[:5]}")
        
        # Hapus data invalid (kurangi penghapusan agresif)
        invalid_titles = df['title'].str.contains('Unknown Title', case=False, na=False)
        df = df[~invalid_titles]
        logging.info(f"Removed {invalid_titles.sum()} rows with invalid titles")
        
        # Konversi price ke Rupiah (1 USD = Rp16,000)
        def convert_price(price):
            try:
                # Hapus '$' atau karakter lain, asumsikan format bervariasi
                cleaned = re.sub(r'[^\d.]', '', price)
                return float(cleaned) * 16000 if cleaned else None
            except ValueError:
                return None
        df['price'] = df['price'].apply(convert_price)
        price_nulls = df['price'].isna()
        df = df[~price_nulls]
        logging.info(f"Removed {price_nulls.sum()} rows with invalid prices")
        
        # Format rating ke float
        def clean_rating(rating):
            try:
                # Hapus 'Rating: ', ' / 5', '⭐', dan teks lain
                cleaned = re.sub(r'Rating: | / 5|⭐|Invalid|[^\d.]', '', rating).strip()
                return float(cleaned) if cleaned else None
            except ValueError:
                return None
        df['rating'] = df['rating'].apply(clean_rating)
        rating_nulls = df['rating'].isna()
        df = df[~rating_nulls]
        logging.info(f"Removed {rating_nulls.sum()} rows with invalid ratings")
        
        # Format colors ke int
        def clean_colors(colors):
            try:
                cleaned = re.sub(r'Colors: |[^\d]', '', colors).strip()
                return int(cleaned) if cleaned else None
            except ValueError:
                return None
        df['colors'] = df['colors'].apply(clean_colors)
        colors_nulls = df['colors'].isna()
        df = df[~colors_nulls]
        logging.info(f"Removed {colors_nulls.sum()} rows with invalid colors")
        
        # Format size dan gender
        df['size'] = df['size'].str.replace('Size: ', '', regex=False)
        df['gender'] = df['gender'].str.replace('Gender: ', '', regex=False)
        
        # Validasi tipe data
        dtypes = {
            'title': str,
            'price': float,
            'rating': float,
            'colors': int,
            'size': str,
            'gender': str,
            'timestamp': str
        }
        df = df.astype(dtypes)
        
        # Validasi rentang (longgarkan)
        price_invalid = df['price'] <= 0
        df = df[~price_invalid]
        logging.info(f"Removed {price_invalid.sum()} rows with price <= 0")
        
        rating_invalid = ~df['rating'].between(0, 5)
        df = df[~rating_invalid]
        logging.info(f"Removed {rating_invalid.sum()} rows with rating not in 0-5")
        
        colors_invalid = df['colors'] < 0
        df = df[~colors_invalid]
        logging.info(f"Removed {colors_invalid.sum()} rows with colors < 0")
        
        if df.empty:
            raise ValueError("DataFrame is empty after validation")
        
        logging.info(f"Transformed data: {len(df)} rows")
        return df
    except Exception as e:
        logging.error(f"Transformation failed: {e}")
        raise