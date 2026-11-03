import os
from utils.extract import scrape_main
from utils.transform import transform_data
from utils.load import save_to_csv, save_to_google_sheets, save_to_postgres
from crontab import CronTab
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_etl():
    """Jalankan pipeline ETL secara berurutan."""
    try:
        spreadsheet_id = os.environ['GOOGLE_SHEETS_ID']
        database_url = os.environ['DATABASE_URL']
        credentials_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'google-sheets-api.json')

        # Extract
        logging.info("Starting extraction")
        df = scrape_main(url_base="https://fashion-studio.dicoding.dev/page{}")
        
        # Transform
        logging.info("Starting transformation")
        df_transformed = transform_data(df)
        
        # Load
        logging.info("Starting loading")
        save_to_csv(df_transformed, 'products.csv')
        save_to_google_sheets(df_transformed, spreadsheet_id, credentials_file)
        save_to_postgres(df_transformed, 'products', database_url)
        
        logging.info("ETL pipeline completed successfully")
    except Exception as e:
        logging.error(f"ETL pipeline failed: {e}")
        raise

def schedule_etl():
    """Schedule the ETL pipeline to run every day at 6 AM."""
    try:
        cron_file = 'etl_schedule.cron'
        
        # Inisialisasi CronTab tanpa file atau user
        cron = CronTab(tab=None)
        
        # Tentukan perintah cron untuk Windows
        project_path = r'D:\KULIAH\STUDPEN DBS CODING 2025\submission belajar fundamental pemrosesan data'
        python_path = r'D:\KULIAH\STUDPEN DBS CODING 2025\submission belajar fundamental pemrosesan data\venv\Scripts\python.exe'
        main_path = r'D:\KULIAH\STUDPEN DBS CODING 2025\submission belajar fundamental pemrosesan data\main.py'
        command = f'cd "{project_path}" && "{python_path}" "{main_path}"'
        
        # Buat job baru
        job = cron.new(command=command)
        job.setall('0 6 * * *')  # Setiap hari jam 6 pagi
        
        # Tulis ke file cron
        with open(cron_file, 'w', encoding='utf-8') as f:
            f.write(str(cron))
        logging.info(f"ETL pipeline scheduled successfully, saved to {cron_file}")
    except Exception as e:
        logging.error(f"Failed to schedule ETL: {e}")
        raise

if __name__ == '__main__':
    run_etl()
    schedule_etl()
