# PADUKA — Integrasi Data Regional BPS dengan Airtable

## Tujuan

Airtable menjadi penyimpanan terpusat untuk observasi statistik regional BPS Sambas. GitHub Actions mengambil data dari BPS WebAPI, lalu menyinkronkannya ke Airtable. Dashboard publik hanya membaca baris yang sudah disetujui dengan status **Valid**.

## Base dan tabel

Base: **PADUKA — Data Regional BPS Sambas**

- **Master Wilayah** — domain BPS dan identitas wilayah.
- **Master Indikator BPS** — kode variabel, definisi, satuan, dan status pemetaan.
- **Observasi Regional** — satu baris per kombinasi domain|indikator|periode.
- **Log Sinkronisasi** — jumlah data dibaca, ditambah, diperbarui, dan ditolak.

## Satu kali konfigurasi GitHub

Koneksi Airtable yang terpasang di ChatGPT dapat mengelola base melalui percakapan, tetapi kredensial OAuth tersebut tidak dibagikan otomatis ke runner GitHub Actions. Untuk sinkronisasi terjadwal, buat Personal Access Token (PAT) Airtable khusus:

1. Buat PAT Airtable dengan scope **data.records:read** dan **data.records:write**.
2. Batasi akses token hanya ke base **PADUKA — Data Regional BPS Sambas**.
3. Simpan token di GitHub repository sebagai Actions secret bernama **AIRTABLE_API_TOKEN**.
4. Jangan letakkan token di file, commit, issue, workflow log, atau percakapan.

GitHub Secret settings:
https://github.com/paduksambas/MD-V14-PADUKA-SAMBAS/settings/secrets/actions

Base ID dan table IDs sudah diatur dalam skrip integrasi. Jangan mengubahnya kecuali base/tabel diganti.

## Cara kerja sinkronisasi

Workflow **Scheduled global intelligence monitoring** berjalan setiap enam jam, dan juga saat dijalankan manual atau ada perubahan terkait.

1. Mengambil observasi dari BPS WebAPI menggunakan konfigurasi domain, variabel, dan periode yang eksplisit.
2. Menulis hasil yang lolos pemeriksaan ke Airtable berdasarkan **Kunci Observasi**: domain|indikator|periode. Pengulangan run memperbarui baris yang sama, bukan membuat duplikat.
3. Jika nilai tetap sama, status validasi yang sudah ada dipertahankan. Jika nilai berubah, status otomatis dikembalikan ke **Belum ditinjau**.
4. Mencatat ringkasan sinkronisasi di **Log Sinkronisasi**.

Data yang tidak memiliki satu nilai numerik yang tidak ambigu ditolak. Nilai kosong tidak diisi nol dan tidak ditebak.

## Gerbang publikasi dashboard

Build GitHub Pages membaca Airtable dan mengekspor **hanya** observasi dengan status **Valid**. Baris **Belum ditinjau** atau **Ditolak** tidak ikut ke dashboard publik.

Sebelum mengubah status menjadi **Valid**, cocokkan nilai, definisi, satuan, periode, dan cakupan wilayah dengan tabel/publikasi BPS asli. Jika BPS merevisi angka pada sinkronisasi berikutnya, status kembali ke **Belum ditinjau** dan nilai baru tidak langsung dipublikasikan.

## Status pemetaan awal Sambas

Periode yang dikonfirmasi melalui metadata BPS: **2024**, ID periode **124**. Domain API Kabupaten Sambas: **6101**.

Dua nilai yang telah dikembalikan sebagai satu sel numerik oleh BPS WebAPI dan dimasukkan ke Airtable:

- Tingkat Pengangguran Terbuka (TPT): 4,99 persen.
- Employment-to-Population Ratio (EPR): 69,15 persen.

Kedua observasi tetap berstatus **Belum ditinjau** sampai diperiksa terhadap tabel BPS asli.

Tiga kandidat lain (variabel 105, 107, dan 108) belum dapat dipetakan menjadi satu sel numerik karena respons tabel berisi lebih dari satu kandidat nilai. Tidak ada angka yang dimasukkan untuk ketiganya.

## Batasan dan keamanan

- PAT Airtable hanya berada di GitHub Actions Secrets dan hanya digunakan pada langkah sinkronisasi/ekspor.
- Build publik mengunggah satu file HTML; report JSON, ekspor sementara, dan database lokal dibersihkan setelah build.
- Dashboard publik hanya menerima baris Airtable yang sudah ditandai **Valid**.
- Hasil BPS yang ambigu, kosong, atau gagal ditolak; sistem tidak mengisi nilai perkiraan.
