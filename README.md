# Bike Sharing Analytics Dashboard

Dashboard interaktif untuk menganalisis penyewaan sepeda berdasarkan waktu, musim, cuaca, dan profil pengguna selama 2011–2012. Aplikasi dibuat dengan Streamlit dan menggunakan data yang sudah disiapkan di `dashboard/main_data.csv`.

Analisis yang tersedia:

- Perbandingan rata-rata penyewaan pada pukul 08.00 dan 17.00 di hari kerja, termasuk persentase perubahan antara 2011 dan 2012.
- Hubungan suhu, kelembapan, dan kecepatan angin dengan jumlah pengguna kasual pada akhir pekan atau hari libur.
- Perbandingan pengguna kasual dan terdaftar berdasarkan klaster waktu dan jenis hari.

Filter rentang tanggal dan musim diterapkan pada seluruh metrik dan visualisasi. Untuk mereplikasi pertanyaan bisnis tentang musim gugur, pilih musim **Fall**.

## Setup Environment - Anaconda

```bash
conda create --name bike-sharing python=3.11
conda activate bike-sharing
python -m pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

Jalankan dari folder utama proyek.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run Streamlit app

Jalankan perintah berikut dari folder utama proyek:

```bash
streamlit run dashboard/dashboard.py
```

Pastikan `dashboard/main_data.csv` tetap berada di folder yang sama dengan `dashboard/dashboard.py`.

