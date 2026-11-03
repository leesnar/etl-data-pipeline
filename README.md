# ETL Data Pipeline

Pipeline Python untuk mengekstrak data produk dari [Fashion Studio](https://fashion-studio.dicoding.dev/), membersihkan dan memvalidasi data, lalu menyimpannya ke CSV, Google Sheets, dan PostgreSQL.

## Fitur

- Ekstraksi halaman utama dan halaman produk sampai halaman 50 menggunakan Requests dan Beautiful Soup.
- Pembersihan nilai kosong, duplikat, dan data tidak valid menggunakan pandas.
- Konversi harga USD ke IDR dengan kurs tetap Rp16.000 per USD.
- Validasi tipe data, harga positif, rating 0–5, dan jumlah warna nonnegatif.
- Ekspor CSV dan integrasi Google Sheets API serta PostgreSQL.
- Unit test berbasis pytest dengan mock untuk layanan eksternal.
- Pembuatan berkas konfigurasi cron untuk jadwal harian pukul 06.00.

## Struktur

```text
main.py                 # Menjalankan tahap ETL dan menghasilkan konfigurasi cron
utils/extract.py        # Web scraping
utils/transform.py      # Pembersihan dan validasi
utils/load.py           # Penyimpanan CSV, Google Sheets, dan PostgreSQL
tests/                  # Unit test
requirements.txt        # Dependensi Python
submission.txt          # Perintah dasar proyek
```

## Menjalankan proyek di Windows

Siapkan Python, PostgreSQL, serta service account Google dengan akses Google Sheets API. Buat spreadsheet dengan tab bernama `Sheet1` dan bagikan akses editor kepada alamat email service account.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

$env:GOOGLE_SHEETS_ID = 'YOUR_SPREADSHEET_ID'
$env:GOOGLE_APPLICATION_CREDENTIALS = 'C:\path\to\service-account.json'
$env:DATABASE_URL = 'postgresql+psycopg2://USER:PASSWORD@localhost:5432/product_db'

python main.py
```

Database tujuan harus sudah tersedia. Ganti nilai contoh dengan konfigurasi lokal. Jika `GOOGLE_APPLICATION_CREDENTIALS` tidak diatur, program menggunakan `google-sheets-api.json` di direktori kerja. Kredensial, environment file, dan hasil proses tidak disertakan dalam Git.

Proses menghasilkan `raw_data.csv` dan `products.csv`. Pemuatan Google Sheets membersihkan tab `Sheet1` sebelum menulis ulang data; pemuatan PostgreSQL menggunakan `if_exists='replace'` untuk tabel `products`.

## Unit test

```powershell
python -m pytest tests
python -m pytest --cov=utils tests/
```

Pengujian layanan eksternal menggunakan mock; hasilnya tidak membuktikan bahwa koneksi ke Google Sheets atau PostgreSQL langsung berhasil.

## Penjadwalan

Setelah ETL berhasil, `schedule_etl()` menulis `etl_schedule.cron` dengan ekspresi `0 6 * * *`. Fungsi ini hanya menghasilkan konfigurasi dan belum mendaftarkan job pada scheduler sistem operasi. Path di fungsi tersebut masih mengacu ke mesin pengembangan awal dan perlu disesuaikan.

Untuk eksekusi otomatis di Windows, daftarkan Python dan `main.py` melalui Task Scheduler, gunakan direktori proyek sebagai direktori kerja, dan sediakan environment variable yang sama bagi proses tersebut. Berkas cron yang dihasilkan menggunakan path Windows dan perlu disesuaikan sebelum digunakan pada sistem dengan cron.
