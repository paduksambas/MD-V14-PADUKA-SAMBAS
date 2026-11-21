# MD V14 — Trend Registry

## 1. Tujuan dan aturan dasar

Trend Registry adalah catatan induk untuk setiap tren/sinyal yang sedang dipantau MD V14. Satu tren memiliki satu ID stabil sepanjang siklus hidupnya. Perubahan bukti, skor, status, indikator, dan outlook dicatat sebagai pembaruan, bukan dibuat sebagai tren duplikat.

Prinsip:
- Pisahkan fakta terverifikasi, interpretasi, proyeksi, dan rekomendasi.
- Simpan URL sumber, penerbit, tanggal publikasi, tanggal kejadian, dan tanggal akses.
- Catat bukti yang mendukung maupun yang bertentangan.
- Jangan mengisi nilai yang tidak diketahui dengan tebakan; gunakan `Unknown` atau `Insufficient evidence`.
- Skor NIVCP wajib disertai alasan per dimensi sesuai `docs/SIGNAL_SCORING.md`.
- Registry adalah dokumentasi analitis; ia tidak otomatis mengumpulkan data atau menjalankan pemantauan.

## 2. ID dan identitas tren

Format ID: `MDV14-TR-YYYY-NNNN`, contoh `MDV14-TR-2026-0001`.

Aturan:
1. Tahun adalah tahun pertama tren dicatat.
2. Nomor urut unik dan tidak digunakan ulang.
3. Judul boleh diperbaiki, tetapi ID tidak berubah.
4. Jika dua catatan ternyata menggambarkan tren yang sama, tetapkan satu ID kanonis dan catat ID lama sebagai alias/merged.
5. Buat ID baru hanya jika mekanisme atau fenomena dasarnya berbeda secara material.

## 3. Skema catatan wajib

| Field | Isi |
|---|---|
| Trend ID | ID stabil sesuai format |
| Title | Nama ringkas dan spesifik |
| One-line thesis | Pernyataan tren yang dapat diuji |
| Description | Ringkasan fenomena dan mekanismenya |
| Primary domain | Kode domain dari taxonomy |
| Tags | Region, actor, sector, horizon, signal-type |
| First detected | Tanggal pertama teridentifikasi |
| Last reviewed | Tanggal pemeriksaan terakhir |
| Lifecycle status | Status siklus hidup |
| Signal type | weak-signal, emerging, accelerating, structural, shock, reversal |
| Time horizon | Immediate, Near-term, Mid-term, Long-term |
| Geography / actors | Wilayah dan aktor yang relevan |
| Evidence set | Sumber pendukung dan penyangkal |
| NIVCP | Nilai N, I, V, C, P; total; alasan |
| Confidence note | Batas bukti dan ketidakpastian |
| Baseline | Kondisi awal / nilai pembanding / tanggal baseline |
| Indicators | Indikator leading dan lagging |
| Trigger rules | Ambang/perubahan yang memicu review atau alert |
| Scenarios | Base, upside, downside bila relevan |
| Impact map | Dampak terhadap domain, sektor, dan pemangku kepentingan |
| Next review | Tanggal evaluasi berikutnya |
| Owner | Peran/tim penanggung jawab, bukan asumsi nama individu |
| Change log | Tanggal, field berubah, nilai lama → baru, alasan, sumber |

## 4. Siklus hidup

Gunakan satu status utama:

- `candidate` — sinyal baru, bukti awal belum cukup.
- `watch` — pola layak dipantau; bukti dan indikator sedang dikumpulkan.
- `emerging` — pola berulang dan didukung beberapa bukti.
- `accelerating` — laju atau dampak meningkat secara material.
- `structural` — perubahan mendalam dengan persistensi kuat.
- `reversing` — bukti menunjukkan tren melemah atau berbalik.
- `dormant` — tidak ada perkembangan bermakna dalam periode review yang ditetapkan.
- `closed` — tidak lagi relevan, terbukti keliru, atau telah digabung ke catatan kanonis.

Status bukan skor. Perubahan status harus memiliki alasan, tanggal, dan bukti. Status `closed` tidak menghapus riwayat.

## 5. Evidence ledger

Setiap bukti dicatat sebagai satu entri terpisah:

| Evidence ID | Trend ID | Claim supported / challenged | Publisher | Source type | Publication date | Event date | Access date | URL | Independence / reliability | Direction |
|---|---|---|---|---|---|---|---|---|---|---|

`Direction` bernilai `supports`, `challenges`, atau `context`. Hindari menghitung ulang sindikasi berita yang berasal dari satu sumber sebagai bukti independen. Prioritaskan dokumen primer dan data asli. Catat koreksi, pencabutan, atau pembaruan sumber.

## 6. Indikator dan trigger

Setiap indikator harus memiliki:
- nama dan definisi operasional;
- unit, cakupan, frekuensi, dan sumber data;
- baseline beserta tanggal dan metode;
- arah yang mengindikasikan penguatan atau pelemahan;
- ambang trigger dan periode konfirmasi;
- keterbatasan data dan kemungkinan false positive;
- tindakan setelah trigger (review, re-score, validasi, atau usulan alert).

Jangan membuat ambang numerik tanpa dasar data atau alasan analitis. Jika ambang masih kualitatif, nyatakan secara eksplisit.

## 7. Aturan NIVCP dan review

- Gunakan skala 1–5 untuk Novelty, Impact, Velocity, Confidence, Persistence.
- Simpan alasan satu kalimat untuk setiap dimensi serta total 5–25.
- Jika bukti tidak memadai, tulis `Insufficient evidence`; jangan memaksakan skor.
- Re-score saat trigger muncul, baseline berubah, bukti penting berlawanan ditemukan, atau jadwal review tiba.
- Skor tinggi tidak otomatis berarti probabilitas kejadian tinggi.
- Catat skor sebelumnya agar perubahan dapat diaudit.

## 8. Template catatan tren

```yaml
trend_id: MDV14-TR-2026-0001
title: "Judul tren"
one_line_thesis: "Pernyataan tren yang dapat diuji."
description: "Ringkasan fenomena, mekanisme, dan konteks."
primary_domain: TEC
tags:
  region: []
  actor: []
  sector: []
  horizon: Near-term
  signal_type: emerging
first_detected: YYYY-MM-DD
last_reviewed: YYYY-MM-DD
lifecycle_status: candidate
geography: []
actors: []
evidence:
  - evidence_id: EV-0001
    claim: "Klaim yang didukung atau ditantang."
    publisher: "Nama penerbit"
    source_type: primary
    publication_date: YYYY-MM-DD
    event_date: YYYY-MM-DD
    access_date: YYYY-MM-DD
    url: "https://example.com/source"
    direction: supports
nivcp:
  novelty: null
  impact: null
  velocity: null
  confidence: null
  persistence: null
  total: null
  rationale:
    novelty: ""
    impact: ""
    velocity: ""
    confidence: ""
    persistence: ""
confidence_note: "Batas bukti dan ketidakpastian."
baseline:
  description: ""
  value: null
  unit: ""
  as_of: YYYY-MM-DD
indicators:
  - name: "Nama indikator"
    definition: ""
    unit: ""
    source: ""
    frequency: ""
    baseline: ""
    direction: ""
    trigger: ""
    confirmation_period: ""
    limitations: ""
trigger_rules:
  - trigger: ""
    action: review
scenarios:
  base: ""
  upside: ""
  downside: ""
impact_map: []
next_review: YYYY-MM-DD
owner: "Peran penanggung jawab"
change_log:
  - date: YYYY-MM-DD
    change: "Catatan awal dibuat"
    rationale: ""
    evidence_ids: []
```

## 9. Prosedur operasi

1. Cari ID yang sudah ada sebelum membuat catatan baru.
2. Tetapkan thesis, domain, horizon, dan status awal.
3. Tambahkan bukti dengan tanggal dan URL; verifikasi sumber serta independensinya.
4. Isi baseline dan indikator yang dapat diamati.
5. Beri skor NIVCP hanya jika bukti cukup.
6. Tetapkan trigger, tindakan, dan tanggal review berikutnya.
7. Saat review, bandingkan bukti dan indikator terhadap baseline; catat perubahan dan alasan.
8. Periksa apakah status perlu berubah, skor perlu dihitung ulang, atau alert perlu disiapkan.
9. Pertahankan jejak audit; jangan menimpa riwayat.

## 10. Quality gate

Catatan belum boleh dipromosikan dari `candidate` ke `watch` atau lebih tinggi jika:
- thesis tidak jelas atau tidak dapat diuji;
- sumber utama tidak dapat ditelusuri;
- tanggal kejadian dan publikasi tercampur;
- bukti yang bertentangan diabaikan;
- indikator tidak memiliki definisi/baseline;
- skor NIVCP tidak memiliki alasan per dimensi.

Jika persyaratan belum terpenuhi, pertahankan status dan tandai gap secara eksplisit.

## 11. Batas implementasi

Dokumen ini menetapkan skema dan prosedur. Penyimpanan otomatis, integrasi feed, dashboard, notifikasi, dan scheduler memerlukan implementasi teknis terpisah. Jangan menyatakan tren sedang dipantau otomatis hanya karena catatan registry tersedia.
