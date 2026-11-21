# MD V14 — Early Warning Memo (EWM)

## 1. Tujuan

Early Warning Memo adalah memo ringkas untuk menyampaikan satu risiko atau perkembangan yang memerlukan perhatian dan keputusan. Memo berfokus pada satu isu utama, konsekuensi jika tidak bertindak, opsi respons, dan trigger untuk meninjau kembali penilaian.

Gunakan memo ini untuk eskalasi terarah kepada pimpinan atau pemangku keputusan. Untuk pencatatan alert operasional dan validasi teknis, tetap ikuti `docs/EARLY_WARNING_SYSTEM.md`.

## 2. Prinsip penyusunan

- Satu memo membahas satu isu utama; isu terkait dapat ditautkan.
- Letakkan kesimpulan dan kebutuhan keputusan di bagian awal.
- Pisahkan fakta, penilaian, asumsi, dan rekomendasi.
- Nyatakan tingkat verifikasi, confidence, horizon, dan keterbatasan.
- Tampilkan bukti pendukung dan bukti tandingan.
- Hindari bahasa sensasional dan kepastian yang tidak didukung.
- Sesuaikan detail dengan audiens; lampiran teknis dapat memuat evidence ledger.
- Memo bukan pengganti prosedur tanggap darurat atau nasihat profesional khusus.

## 3. Template memo

# MD V14 — EARLY WARNING MEMO

**Memo ID:** MDV14-EWM-YYYY-NNNN  
**Versi:** 1.0  
**Tanggal/waktu:** YYYY-MM-DD HH:MM (Asia/Jakarta)  
**Kepada:** Peran/jabatan atau kelompok penerima  
**Dari:** Tim/peran analis  
**Subjek:** Ringkasan isu dan urgensi  
**Klasifikasi distribusi:** Sesuai kebijakan organisasi  
**Severity:** INFORMATIONAL / WATCH / WARNING / CRITICAL  
**Verification:** UNVERIFIED / PARTIALLY_VERIFIED / VERIFIED / DISPUTED  
**Confidence:** LOW / MODERATE / HIGH  
**Horizon:**  
**Related Alert ID:**  
**Related Trend ID:**  
**Keputusan diminta paling lambat:**  
**Next review:**  

### A. Key Judgment

Maksimal tiga kalimat:
1. Apa yang sedang terjadi atau berubah?
2. Mengapa hal ini penting bagi penerima?
3. Apa tindakan/keputusan yang diperlukan dan kapan?

### B. Decision Required

- **Keputusan atau tindakan yang diminta:**
- **Batas waktu keputusan:**
- **Konsekuensi jika ditunda:**
- **Pihak yang berwenang memutuskan:**

Jika belum ada keputusan yang diminta, jelaskan bahwa memo bersifat awareness-only.

### C. Situation and Verified Facts

| Fakta/klaim | Waktu kejadian | Sumber | Status verifikasi |
|---|---|---|---|

Pisahkan fakta yang telah dikonfirmasi dari laporan awal, klaim pihak berkepentingan, dan informasi yang belum diverifikasi.

### D. Why It Matters

- Mekanisme risiko atau peluang:
- Aktor, wilayah, dan sektor terdampak:
- Dampak langsung:
- Dampak lanjutan/lintas-domain:
- Jendela waktu dan tingkat urgensi:

### E. Warning Indicators and Triggers

| Indikator | Baseline | Pembacaan terbaru | Trigger | Status / implikasi |
|---|---|---|---|---|

Jika data tidak tersedia, tulis **Data unavailable**. Jangan membuat angka baseline atau ambang tanpa sumber.

### F. Assessment

- **Severity dan alasan:**
- **Confidence dan alasan:**
- **NIVCP (bila relevan):** nilai dan alasan per dimensi; atau Insufficient evidence.
- **Asumsi kunci:**
- **Penjelasan alternatif:**
- **Bukti yang bertentangan:**
- **Hal yang belum diketahui:**

### G. Outlook and Scenarios

| Skenario | Kondisi pemicu | Indikator konfirmasi | Dampak yang mungkin |
|---|---|---|---|
| Base case | | | |
| Escalation / downside | | | |
| De-escalation / upside | | | |

Nyatakan horizon setiap skenario. Jangan memberikan probabilitas numerik tanpa metode dan dasar estimasi yang dapat dijelaskan.

### H. Response Options

| Opsi | Manfaat | Biaya/risiko/trade-off | Prasyarat | Waktu |
|---|---|---|---|---|

Sajikan opsi secara berimbang. Bedakan tindakan tanpa penyesalan (no-regret), tindakan bersyarat, dan tindakan yang memerlukan otorisasi khusus.

### I. Recommended Course of Action

- **Rekomendasi utama:**
- **Alasan:**
- **Langkah 1 / owner role / tenggat:**
- **Langkah 2 / owner role / tenggat:**
- **Indikator keberhasilan:**
- **Kondisi untuk mengubah atau menghentikan tindakan:**

### J. Escalation and Review Plan

- Penerima eskalasi:
- Kondisi eskalasi lebih lanjut:
- Frekuensi pembaruan:
- Next review date/time:
- Kondisi untuk menurunkan severity atau menutup memo:

### K. Sources and Annexes

Daftar sumber dengan penerbit, judul, tanggal kejadian/publikasi, URL, dan klaim yang didukung. Lampirkan tabel bukti, kronologi, data indikator, atau peta dampak bila dibutuhkan.

---

## 4. Panduan panjang dan format

- **Flash memo:** satu halaman untuk perkembangan mendesak; isi A, B, C, D, F, I, J, K.
- **Standard memo:** sekitar 2–4 halaman; gunakan seluruh bagian yang relevan.
- **Technical annex:** lampiran terpisah untuk metodologi, data, evidence ledger, dan analisis skenario.

Panjang bukan ukuran kualitas. Memo harus cukup ringkas untuk mendukung keputusan tanpa menghilangkan ketidakpastian yang material.

## 5. Review dan persetujuan

Sebelum distribusi, reviewer memeriksa:
- ketepatan fakta, tanggal, dan sumber;
- pemisahan fakta dan penilaian;
- konsistensi severity dengan EWS;
- kewajaran confidence dan asumsi;
- keseimbangan opsi dan trade-off;
- kejelasan keputusan, otorisasi, dan tenggat;
- kesesuaian klasifikasi distribusi dengan kebijakan organisasi.

Untuk CRITICAL, lakukan eskalasi segera melalui kanal yang disepakati; proses editorial memo tidak boleh menunda respons keselamatan atau prosedur darurat.

## 6. Riwayat versi

| Versi | Waktu | Perubahan | Alasan | Penyusun/reviewer |
|---|---|---|---|---|
| 1.0 | YYYY-MM-DD | Memo awal | | |

Jangan menimpa versi terdahulu. Catat perubahan material pada severity, confidence, fakta inti, atau rekomendasi.

## 7. Batas penggunaan

Template ini tidak mengirim memo secara otomatis, tidak mengesahkan keputusan, dan tidak menjamin prediksi. Distribusi, klasifikasi keamanan, otorisasi, serta tindakan respons tetap mengikuti tata kelola organisasi dan penanggung jawab manusia.