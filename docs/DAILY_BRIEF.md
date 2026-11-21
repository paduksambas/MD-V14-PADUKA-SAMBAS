# MD V14 — Daily Intelligence Brief (DIB)

## 1. Tujuan

Daily Intelligence Brief menyajikan perubahan paling penting dalam periode 24 jam terakhir (atau periode eksplisit yang disebutkan), beserta implikasi, tingkat keyakinan, indikator, dan tindakan yang disarankan. Brief harus berorientasi pada perubahan dan keputusan, bukan sekadar kumpulan berita.

Jika tidak ada perkembangan material, nyatakan secara eksplisit: **No material change detected in the reviewed scope**. Jangan menciptakan sinyal untuk mengisi ruang.

## 2. Aturan penerbitan

- Cantumkan tanggal, waktu cut-off, dan zona waktu (default: Asia/Jakarta).
- Jelaskan cakupan domain, geografi, dan periode yang benar-benar diperiksa.
- Bedakan tanggal kejadian, tanggal publikasi, dan waktu akses.
- Prioritaskan sumber primer, data resmi, dan konfirmasi independen.
- Setiap klaim material harus memiliki sitasi/tautan yang dapat ditelusuri.
- Pisahkan fakta, analisis, skenario, dan rekomendasi.
- Tandai informasi yang belum terverifikasi dan bukti yang saling bertentangan.
- Jangan menyebut pencarian terbatas sebagai pemantauan global menyeluruh.
- Jangan menyatakan tidak ada perubahan jika cakupan sumber atau periode tidak memadai.

## 3. Template Daily Intelligence Brief

# MD V14 — DAILY INTELLIGENCE BRIEF

**Tanggal:** YYYY-MM-DD  
**Diterbitkan:** HH:MM (Asia/Jakarta)  
**Cut-off data:** YYYY-MM-DD HH:MM (zona waktu)  
**Periode tinjauan:**  
**Cakupan domain/geografi:**  
**Analis/owner:**  
**Status cakupan:** Lengkap / Parsial / Terbatas

### A. Executive Intelligence Summary

Maksimal lima butir. Urutkan menurut signifikansi, bukan urutan berita.

1. **[Judul sinyal]** — perubahan utama, mengapa penting, confidence, dan tindakan paling relevan.
2. ...
3. ...

### B. Top Signals — Perubahan 24 Jam

| Prioritas | Sinyal/perubahan | Fakta dan waktu | Domain/geografi | Implikasi | Confidence | Trend ID |
|---|---|---|---|---|---|---|

Masukkan hanya perubahan yang material. Jika tidak ada, tulis bahwa tidak ditemukan perubahan material dalam cakupan yang diperiksa.

### C. Early Warning Status

| Alert ID | Severity | Perkembangan/trigger | Verification | Confidence | Tindakan dan next review |
|---|---|---|---|---|---|

Gunakan INFORMATIONAL / WATCH / WARNING / CRITICAL sesuai `docs/EARLY_WARNING_SYSTEM.md`. Jangan menaikkan severity tanpa bukti dan alasan.

### D. Trend Registry Changes

| Trend ID | Perubahan status/skor/bukti | Nilai sebelumnya → terbaru | Alasan dan sumber |
|---|---|---|---|

Jika tidak ada perubahan registry, tulis **No registry change**. Jangan mengarang ID atau skor.

### E. Domain Watch

Ringkasan singkat domain yang ditinjau:
- GEO — geopolitik dan diplomasi:
- ECO / FIN — ekonomi dan pasar:
- TEC — teknologi:
- BUS — industri dan rantai pasok:
- ENE — energi dan mineral:
- SOC / HLT — sosial dan kesehatan:
- ENV — iklim, pangan, dan lingkungan:
- SEC — keamanan dan pertahanan:

Untuk setiap domain, tandai: **Material change / Watch / No material change / Not reviewed**. Jangan menggunakan “No material change” untuk domain yang tidak diperiksa.

### F. Impact Assessment

Untuk setiap sinyal utama, uraikan:
- mekanisme sebab-akibat;
- aktor, sektor, dan wilayah terdampak;
- dampak jangka pendek dan menengah;
- efek lintas-domain;
- peluang, risiko, dan pihak yang paling terekspos.

### G. Indicators to Watch

| Indikator | Baseline dan tanggal | Pembacaan terbaru | Arah | Trigger | Sumber/frekuensi |
|---|---|---|---|---|---|

Cantumkan unit dan cakupan data. Jika pembacaan terbaru tidak tersedia, tulis **Data unavailable**.

### H. Outlook — 24 Jam hingga 30 Hari

- **Base case:** perkembangan yang paling masuk akal dan asumsi kuncinya.
- **Upside:** perkembangan lebih baik dan indikator konfirmasi.
- **Downside:** perkembangan lebih buruk dan indikator konfirmasi.
- **Key uncertainties:** faktor yang dapat mengubah penilaian.

Skenario bukan prediksi pasti. Sebutkan horizon dan trigger perubahan.

### I. Recommended Actions

| Urutan | Tindakan | Alasan | Owner role | Tenggat/review |
|---|---|---|---|---|

Bedakan tindakan yang perlu segera dilakukan dari hal yang hanya perlu dipantau. Jangan memberikan rekomendasi tanpa alasan.

### J. Confidence, Gaps, and Limitations

- **Overall confidence:** Low / Moderate / High, dengan alasan.
- **Unverified claims:**
- **Conflicting evidence:**
- **Data gaps / domains not reviewed:**
- **Methodological limitations:**

### K. Sources

Daftar sumber dengan penerbit, judul/jenis dokumen, tanggal publikasi/kejadian, URL, dan klaim yang didukung. Letakkan sitasi dekat klaim terkait di versi yang diterbitkan.

---

## 4. Aturan prioritas sinyal

Gunakan penilaian kualitatif berdasarkan:
1. Dampak potensial dan luasnya pihak terdampak.
2. Urgensi serta kecepatan perubahan.
3. Kebaruan dibanding baseline.
4. Kekuatan dan independensi bukti.
5. Persistensi atau potensi perubahan struktural.
6. Relevansi terhadap keputusan pengguna laporan.

NIVCP dapat digunakan untuk karakteristik tren, tetapi tidak menggantikan severity alert. Jangan menghitung skor komposit baru tanpa metodologi yang disetujui.

## 5. Prosedur produksi harian

1. Tetapkan periode cut-off, cakupan, dan pertanyaan intelijen.
2. Kumpulkan perkembangan dari sumber relevan dan catat cakupan pencarian.
3. Validasi klaim penting, tanggal, sumber primer, dan bukti berlawanan.
4. Bandingkan perkembangan dengan baseline dan Trend Registry.
5. Periksa trigger EWS dan status alert aktif.
6. Perbarui catatan tren hanya jika ada bukti/perubahan yang layak; simpan change log.
7. Susun executive summary dan urutkan sinyal menurut materialitas.
8. Tinjau konsistensi fakta, confidence, severity, dan rekomendasi.
9. Terbitkan brief dengan keterbatasan yang transparan.
10. Tetapkan indikator dan tanggal review untuk siklus berikutnya.

## 6. Quality gate sebelum terbit

- [ ] Periode, cut-off, zona waktu, dan cakupan dinyatakan.
- [ ] Klaim utama memiliki sumber dan tanggal.
- [ ] Fakta dipisahkan dari interpretasi dan skenario.
- [ ] Bukti yang bertentangan serta ketidakpastian dicatat.
- [ ] Severity EWS konsisten dengan bukti.
- [ ] Perubahan Trend Registry dapat ditelusuri.
- [ ] Domain yang tidak ditinjau ditandai Not reviewed.
- [ ] Rekomendasi memiliki alasan dan owner role.
- [ ] Tidak ada klaim pemantauan otomatis yang belum diimplementasikan.

## 7. Batas operasional

Template ini tidak otomatis mengumpulkan berita, membaca semua feed, mengubah Trend Registry, atau mengirim brief terjadwal. Otomatisasi memerlukan sumber data terintegrasi, prosedur scheduler, penyimpanan, pengujian, dan kanal distribusi. Setiap brief harus menyebutkan cakupan kerja yang benar-benar dilakukan.