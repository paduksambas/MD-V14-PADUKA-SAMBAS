# PADUKA — Integrasi Data Regional BPS dengan Airtable

## Tujuan

Airtable menjadi penyimpanan terpusat untuk observasi statistik regional BPS Sambas. GitHub Actions mengambil data dari BPS WebAPI, lalu menyinkronkannya ke Airtable. Dashboard publik mengambil baris Airtable melalui PAT khusus. Baris **Valid** masuk ke analisis regional; baris **Belum ditinjau** ditampilkan pada antrean tinjauan terpisah dan tidak masuk ke ranking atau perhitungan disparitas.

## Base dan tabel

Base: **PADUKA — Data Regional BPS Sambas**

- **Master Wilayah** — domain BPS dan identitas wilayah.
- **Master Indikator BPS** — kode variabel, definisi, satuan, dan status pemetaan.
- **Observasi Regional** — satu baris per kombinasi domain|indikator|periode.
- **Log Sinkronisasi** — jumlah data dibaca, ditambah, diperbarui, dan ditolak.

## Konfigurasi GitHub

Koneksi Airtable di ChatGPT tidak otomatis dibagikan ke runner GitHub Actions. Simpan PAT Airtable dengan scope data.records:read dan data.records:write, batasi ke base PADUKA, dan simpan sebagai Actions secret AIRTABLE_API_TOKEN. Jangan letakkan token di file, commit, log, atau percakapan.

Base ID dan table IDs sudah diatur dalam skrip integrasi.

## Cara kerja sinkronisasi

Workflow **Scheduled global intelligence monitoring** berjalan setiap enam jam, dan juga saat dijalankan manual atau ada perubahan terkait.

1. Mengambil observasi dari BPS WebAPI menggunakan konfigurasi domain, variabel, dan periode yang eksplisit.
2. Menulis hasil yang lolos pemeriksaan ke Airtable berdasarkan Kunci Observasi: domain|indikator|periode.
3. Jika nilai tetap sama, status validasi yang sudah ada dipertahankan. Jika nilai berubah, status dikembalikan ke Belum ditinjau.
4. Mencatat ringkasan sinkronisasi di Log Sinkronisasi.

Data ambigu atau kosong ditolak; sistem tidak mengisi nilai nol atau menebak.

## Status validasi Sambas per 23 November 2026

Periode yang dikonfirmasi melalui metadata BPS: **2024**, ID periode **124**. Domain API Kabupaten Sambas: **6101**.

Dua observasi di Airtable berstatus **Valid**:

- Tingkat Pengangguran Terbuka (TPT): **4,99 persen**.
- Employment-to-Population Ratio (EPR): **69,15 persen**.

Validasi angka direproduksi dari Laporan Kinerja Instansi Pemerintah Kabupaten Sambas Tahun 2024: TPT = 17,69/354,58 x 100 = 4,9890% -> 4,99%; EPR = 336,89/487,18 x 100 = 69,1510% -> 69,15%. Angka dasar laporan disajikan dalam ribuan dengan dua desimal, sehingga hasil hitung cocok setelah pembulatan. Laporan resmi: https://sambas.go.id/uploads/transparansi_anggaran/transparansi-124.pdf. Konteks Sakernas Agustus 2024 representatif hingga kabupaten/kota: https://sambaskab.bps.go.id/id/news/2024/07/24/66/pelatihan-petugas-survei-angkatan-kerja-nasional--sakernas--agustus-2024.html.

Catatan audit di tiap record menjelaskan bahwa verifikasi menggunakan perhitungan ulang angka dasar pemerintah daerah, bukan ekstraksi baris mentah dari tabel dinamis BPS. Halaman tabel EPR BPS yang teridentifikasi: https://sambaskab.bps.go.id/en/statistics-table/2/MTY4IzI=/rasio-penduduk-umur-15-tahun-ke-atas-yang-bekerja-terhadap-jumlah-penduduk--epr-.html.

Tiga kandidat lain (variabel 105, 107, dan 108) belum dapat dipetakan menjadi satu sel numerik karena respons tabel berisi lebih dari satu kandidat nilai. Tidak ada angka yang dimasukkan untuk ketiganya.

## Batasan dan keamanan

- PAT Airtable hanya berada di GitHub Actions Secrets dan digunakan pada langkah sinkronisasi/ekspor.
- Build publik mengunggah satu file HTML; report JSON, ekspor sementara, dan database lokal dibersihkan setelah build.
- Hanya baris berstatus Valid yang masuk perhitungan regional; observasi yang menunggu tinjauan tidak memengaruhi ranking.
