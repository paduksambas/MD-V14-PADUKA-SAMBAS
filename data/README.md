# Data publik BPS untuk PADUKA

Tempatkan satu file ekspor tabel BPS yang telah dipilih dan diunduh secara resmi di folder ini dengan salah satu nama berikut:

- `bps-public-export.csv`
- `bps-public-export.xlsx`
- `bps-public-export.json`

Lalu salin `examples/bps-public-export.sample.json` menjadi `examples/bps-public-export.json` dan sesuaikan pemetaan header, kode indikator, wilayah, periode, satuan, serta URL tabel BPS yang tepat. Jangan mengisi atau menebak nilai secara manual ke file ini.

GitHub Pages otomatis memproses file tersebut ketika perubahan di-push ke `main`. File dan konfigurasi tidak boleh berisi kredensial atau informasi pribadi. Sebelum dipakai dalam ranking, periksa definisi indikator, satuan, periode, revisi, cakupan wilayah, dan baris yang ditolak.

Saat folder ini hanya berisi README, status impor publik BPS tetap `not_configured` secara sengaja.
