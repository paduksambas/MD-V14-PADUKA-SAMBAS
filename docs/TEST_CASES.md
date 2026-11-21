# MD V14 — Test Cases & Acceptance Checks

Gunakan test ini untuk memastikan instruksi plugin konsisten sebelum build berikutnya.

## Test 01 — Daily brief
**Prompt:** Buat Global Trend Brief untuk 24 jam terakhir. Prioritaskan geopolitik, ekonomi, AI, energi. 5 sinyal maksimum.
**Lulus jika:** menyertakan tanggal/horizon, fakta dengan sumber dan tanggal, dampak, indikator, outlook, rekomendasi; tidak mengarang.

## Test 02 — Deep dive
**Prompt:** Analisis mendalam dampak pembatasan ekspor chip terhadap rantai pasok dan persaingan AI global. Horizon 12–24 bulan.
**Lulus jika:** aktor, mekanisme, bukti, alternatif penjelasan, skenario, ketidakpastian, dan sumber jelas.

## Test 03 — Early warning
**Prompt:** Buat early-warning monitor untuk risiko eskalasi konflik yang dapat mengganggu perdagangan dan energi.
**Lulus jika:** indikator terukur/observabel, trigger, kemungkinan dampak, dan tindakan respons; tidak mengklaim monitor aktif jika belum dijadwalkan.

## Test 04 — Contradictory evidence
**Prompt:** Evaluasi klaim bahwa AI akan menggantikan mayoritas pekerjaan dalam dua tahun. Cari bukti yang mendukung dan menentang.
**Lulus jika:** bukti pro/kontra dipisahkan, asumsi dijelaskan, confidence dikalibrasi, tidak mengunci pada satu narasi.

## Test 05 — Decision memo
**Prompt:** Saya harus menentukan prioritas investasi teknologi tahun depan. Buat decision memo berbasis tren.
**Lulus jika:** keputusan dan konteks jelas; opsi, trade-off, risiko, kebutuhan validasi, dan rekomendasi prioritas dibedakan.

## Acceptance criteria
- Klaim faktual terkini memiliki sumber dan tanggal.
- Fakta, analisis, prediksi, dan rekomendasi tidak tercampur.
- Ketidakpastian dan counter-signal terlihat.
- Format output ringkas, bisa dibaca, dan dapat ditindaklanjuti.
- Tidak menyatakan monitoring otomatis berjalan kecuali automation benar-benar dibuat.
