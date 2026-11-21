# MD V14 — Indicator & Trigger Register

## 1. Tujuan dan ruang lingkup

Register ini adalah katalog terstruktur untuk memantau indikator yang dapat mengonfirmasi, melemahkan, atau mengubah penilaian atas tren, risiko, dan peluang. Register menghubungkan Trend Registry, Early Warning System (EWS), Daily Intelligence Brief, dan Weekly Global Intelligence Report.

Register adalah spesifikasi kerja dan template pencatatan. Dokumen ini tidak mengambil data secara otomatis, menghitung ambang secara mandiri, atau mengirim peringatan. Setiap pembaruan dan keputusan tetap memerlukan analis/owner yang bertanggung jawab.

## 2. Prinsip desain

1. **Observable:** indikator harus dapat diamati atau diukur dengan sumber yang dapat diidentifikasi.
2. **Decision-relevant:** jelaskan penilaian atau keputusan apa yang dapat berubah ketika indikator bergerak.
3. **Reproducible:** definisi, unit, periode, dan metode pengukuran harus cukup jelas agar pembacaan dapat diulang.
4. **Contextual:** baseline dan trigger harus mempertimbangkan konteks wilayah, sektor, musim, dan kondisi normal.
5. **Falsifiable:** catat kondisi yang akan melemahkan hipotesis, bukan hanya bukti pendukung.
6. **Proportionate:** severity dan respons sebanding dengan kekuatan bukti serta potensi dampak.
7. **Auditable:** setiap perubahan nilai, baseline, threshold, status, atau interpretasi memiliki tanggal, sumber, dan catatan.

## 3. Hubungan ID dan konvensi penamaan

Gunakan ID stabil dan unik. Jangan mendaur ulang ID yang sudah ditutup.

| Objek | Pola ID | Contoh |
|---|---|---|
| Indikator | IND-YYYY-NNNN | IND-2026-0001 |
| Trigger | TRG-YYYY-NNNN | TRG-2026-0001 |
| Tren terkait | Ikuti Trend Registry | TR-ENERGY-001 |
| Alert terkait | Ikuti EWS | EWS-2026-0001 |
| Memo terkait | Ikuti EWM | MDV14-EWM-2026-0001 |

Satu indikator dapat memiliki beberapa trigger (misalnya WATCH dan WARNING). Satu trigger dapat merujuk pada lebih dari satu indikator bila hubungan dan logikanya dijelaskan. Hindari menggabungkan indikator yang berbeda definisi ke dalam satu entri.

## 4. Struktur data minimum

Setiap entri indikator wajib mencakup:

| Field | Keterangan |
|---|---|
| Indicator ID | ID unik dan stabil |
| Name | Nama singkat indikator |
| Definition | Definisi operasional dan apa yang diukur |
| Domain / tags | Domain dan tag taxonomy |
| Linked Trend IDs | Tren terkait |
| Geography / scope | Wilayah, pasar, aktor, atau cakupan |
| Unit / direction | Unit serta arah perubahan yang relevan |
| Baseline | Nilai/kondisi normal, periode, dan metode |
| Latest reading | Pembacaan terbaru, waktu observasi, dan sumber |
| Source & quality | Sumber, URL/referensi, kualitas, dan keterbatasan |
| Update cadence | Frekuensi pembaruan yang diharapkan |
| Owner role | Peran penanggung jawab |
| Trigger IDs | Trigger yang menggunakan indikator |
| Limitations | Bias, lag, missingness, dan risiko false positive |
| Status | ACTIVE / WATCHLIST / SUSPENDED / RETIRED |
| Last reviewed | Tanggal review terakhir |

Jika data tidak tersedia, tulis **UNKNOWN** atau **NOT AVAILABLE**; jangan mengisi nilai perkiraan seolah-olah terukur.

## 5. Template entri indikator

Salin blok berikut untuk setiap indikator baru.

### IND-YYYY-NNNN — [Nama indikator]

- **Status:** ACTIVE / WATCHLIST / SUSPENDED / RETIRED
- **Domain / tags:**
- **Linked Trend IDs:**
- **Geography / scope:**
- **Definition:** Definisi operasional yang spesifik.
- **Rationale:** Mengapa indikator ini relevan terhadap tren/risiko.
- **Unit:**
- **Directionality:** Naik / turun / perubahan volatilitas / kondisi ambang / kualitatif.
- **Baseline:** Nilai atau kondisi normal.
- **Baseline period & method:** Periode acuan, metode hitung, dan alasan pemilihan.
- **Latest reading:**
- **Observation timestamp:**
- **Source(s):** Penerbit, judul/dataset, URL, tanggal publikasi/akses.
- **Source quality:** HIGH / MODERATE / LOW / DISPUTED; jelaskan alasan.
- **Update cadence:**
- **Expected publication lag:**
- **Owner role:**
- **Related Trigger IDs:**
- **Limitations / bias:**
- **False-positive risks:**
- **Disconfirming evidence to watch:**
- **Last reviewed:**
- **Change history:**

## 6. Spesifikasi trigger

Trigger mengubah pembacaan indikator menjadi kondisi yang perlu ditinjau atau dieskalasikan. Trigger bukan prediksi otomatis dan tidak boleh diaktifkan hanya karena satu angka tampak mencolok tanpa konteks.

Setiap trigger wajib menjelaskan:

- ID dan nama trigger;
- indikator dan tren yang terkait;
- kondisi/logika yang dapat diuji;
- ambang dan satuan atau kriteria kualitatif;
- jangka waktu dan confirmation window;
- sumber data yang diterima;
- pengecualian dan konteks;
- level EWS yang diusulkan;
- langkah validasi sebelum eskalasi;
- tindakan/review yang diharapkan;
- kondisi pembatalan, de-escalation, atau expiry;
- owner dan tanggal review.

### Template trigger

#### TRG-YYYY-NNNN — [Nama kondisi]

- **Status:** PROPOSED / ACTIVE / PAUSED / RETIRED
- **Indicator ID(s):**
- **Linked Trend ID(s):**
- **Trigger logic:** Jika [indikator/kondisi] memenuhi [ambang/kriteria] selama [periode], dengan [konfirmasi].
- **Threshold:** Nilai/kondisi dan unit; cantumkan dasar penetapan.
- **Comparison:** Baseline, perubahan absolut/relatif, peer comparison, atau kombinasi.
- **Confirmation window:** Durasi/jumlah observasi yang diperlukan.
- **Accepted source(s):**
- **Context / exclusions:** Musiman, revisi data, kejadian satu kali, perubahan metodologi, dan faktor pengganggu.
- **Proposed EWS severity:** INFORMATIONAL / WATCH / WARNING / CRITICAL.
- **Validation steps:** Pemeriksaan sumber, independen corroboration, timestamp, dan konteks.
- **False-positive risk:**
- **False-negative risk:**
- **Expected action:** Pantau, verifikasi, analisis dampak, atau eskalasi.
- **De-escalation / reset condition:**
- **Expiry / review date:**
- **Owner role:**
- **Approval / activation note:**

## 7. Penetapan baseline dan threshold

- Pilih baseline yang relevan dengan objek dan konteks; nyatakan periode, unit, metode, dan alasan.
- Pertimbangkan pola musiman, tren struktural, perubahan rezim, revisi data, serta keterbandingan antarwilayah.
- Gunakan ambang absolut, relatif, deviasi dari baseline, laju perubahan, atau kombinasi sesuai karakter indikator.
- Untuk indikator kualitatif, definisikan bukti minimum dan kriteria kategorisasi secara eksplisit.
- Jangan mengarang threshold numerik. Jika belum ada dasar empiris, tandai **PROVISIONAL** dan jelaskan metode validasi.
- Gunakan confirmation window untuk mengurangi noise; jangan menunda eskalasi yang diwajibkan prosedur keselamatan.
- Review threshold ketika metodologi sumber berubah atau indikator kehilangan daya prediksi.

## 8. Validasi, severity, dan confidence

Ikuti `docs/EARLY_WARNING_SYSTEM.md` untuk definisi severity dan alur eskalasi.

Sebelum trigger diaktifkan:
1. Periksa apakah sumber asli dan timestamp tersedia.
2. Pastikan definisi, unit, cakupan, dan periode sebanding dengan baseline.
3. Cari konfirmasi independen jika dampaknya material.
4. Periksa revisi data, duplikasi berita, anomali sementara, dan faktor musiman.
5. Cari bukti tandingan dan penjelasan alternatif.
6. Nilai confidence secara terpisah dari severity.
7. Catat alasan aktivasi, penundaan, atau penolakan trigger.

**Severity** mencerminkan urgensi dan potensi dampak; **confidence** mencerminkan kekuatan bukti. Severity tinggi tidak otomatis berarti confidence tinggi.

## 9. Risiko false positive dan false negative

| Risiko | Contoh | Pengendalian |
|---|---|---|
| False positive | Lonjakan sementara disalahartikan sebagai perubahan struktural | Confirmation window, sumber kedua, pemeriksaan musiman |
| False negative | Data terlambat membuat eskalasi tertunda | Catat publication lag, gunakan indikator pendahulu yang tervalidasi |
| Measurement drift | Metode atau definisi sumber berubah | Versi metodologi dan peninjauan ulang baseline |
| Coverage bias | Data hanya mewakili sebagian wilayah/aktor | Nyatakan cakupan dan tambahkan sumber pembanding |
| Correlated sources | Banyak laporan mengulang satu sumber primer | Telusuri sumber asal dan hindari menghitung ulang sebagai corroboration |
| Threshold gaming | Ambang disesuaikan agar cocok dengan narasi | Catat alasan, persetujuan, dan histori perubahan |

## 10. Workflow operasional

1. **Propose:** analis mengusulkan indikator/trigger dengan ID dan definisi lengkap.
2. **Review:** reviewer memeriksa relevansi, kualitas sumber, baseline, dan potensi bias.
3. **Approve:** owner yang berwenang menyetujui status ACTIVE dan threshold.
4. **Observe:** owner mencatat pembacaan terbaru beserta waktu dan sumber.
5. **Validate:** analis menguji trigger, konteks, bukti tandingan, dan confidence.
6. **Escalate:** jika memenuhi kriteria, ikuti EWS; buat Alert ID dan/atau EWM bila diperlukan.
7. **Report:** perubahan material masuk ke Daily Brief; tren lintas waktu dan implikasi masuk ke Weekly Report.
8. **Review:** evaluasi kinerja indikator dan trigger sesuai cadence serta setelah kejadian material.
9. **Retire:** hentikan indikator yang tidak relevan/tidak andal, simpan histori dan alasan.

## 11. Log pembacaan indikator

| Indicator ID | Observation time | Reading | Unit | Source | Validation status | Analyst note |
|---|---|---|---|---|---|---|

Satu baris mewakili satu observasi. Jangan menimpa observasi lama; koreksi harus menjadi entri baru yang merujuk pada catatan yang dikoreksi.

## 12. Trigger event log

| Event ID | Trigger ID | Time detected | Observed condition | Validation | EWS action / Alert ID | Decision / owner |
|---|---|---|---|---|---|---|

Catat trigger yang terpenuhi maupun yang ditolak setelah validasi. Log penolakan membantu mengukur false positive dan memperbaiki definisi.

## 13. Review cadence

Cadence ditetapkan berdasarkan volatilitas dan ketersediaan data, bukan satu jadwal seragam untuk semua indikator.

| Kategori indikator | Panduan review |
|---|---|
| Sangat cepat / event-driven | Saat data atau kejadian baru tersedia; validasi segera sesuai urgensi |
| Mingguan | Minimal setiap minggu dan setelah perubahan material |
| Bulanan / struktural | Minimal setiap bulan atau sesuai siklus publikasi |
| Kuartalan / lambat | Setiap kuartal dan ketika ada sinyal luar biasa |

Jika data belum terbit sesuai jadwal, catat keterlambatan; jangan menganggap tidak ada perubahan sebagai pembacaan nol.

## 14. Quality gate

Entri tidak boleh berstatus ACTIVE sebelum:
- definisi dan cakupan dapat dipahami secara konsisten;
- sumber dapat ditelusuri dan kualitasnya dinilai;
- baseline dan metode dinyatakan atau keterbatasannya dijelaskan;
- threshold memiliki dasar atau ditandai PROVISIONAL dengan rencana validasi;
- false-positive/false-negative risks dinilai;
- owner dan review cadence ditetapkan;
- keterkaitan dengan Trend Registry dan EWS jelas;
- reviewer dan tanggal persetujuan dicatat.

## 15. Change log dan versioning

| Tanggal | ID | Field yang berubah | Nilai lama → baru | Alasan dan bukti | Diubah oleh | Disetujui oleh |
|---|---|---|---|---|---|---|

Perubahan definisi, baseline, threshold, severity mapping, atau status harus dicatat. Simpan versi sebelumnya agar analisis historis dapat direkonstruksi.

## 16. Integrasi dengan artefak MD V14

- **Trend Registry:** simpan Indicator ID dan Trigger ID pada entri tren yang relevan.
- **Early Warning System:** gunakan trigger sebagai masukan validasi; severity akhir mengikuti prosedur EWS.
- **Early Warning Memo:** cantumkan indikator, pembacaan, trigger, dan bukti utama yang mendasari memo.
- **Daily Intelligence Brief:** laporkan trigger baru, perubahan pembacaan material, status validasi, dan tindakan.
- **Weekly Global Intelligence Report:** evaluasi arah indikator, tren lintas minggu, perubahan baseline, serta performa trigger.
- **NIVCP:** gunakan pembacaan indikator sebagai bukti untuk dimensi yang relevan; jangan menyamakan satu indikator dengan skor keseluruhan.

## 17. Batas penggunaan

Register ini merupakan kerangka tata kelola dan pencatatan. Ia belum menjadi database, feed data, dashboard, atau mesin trigger otomatis. Data aktual, koneksi sumber, perhitungan, persetujuan, dan notifikasi memerlukan implementasi teknis serta pengawasan manusia.