# MD V14 — Early Warning System (EWS)

## 1. Tujuan dan prinsip
EWS mengubah perubahan indikator dan bukti menjadi peringatan yang dapat ditindaklanjuti. Alert adalah penilaian pada waktu penerbitan, bukan kepastian prediksi. Dokumen ini menetapkan metode dan format; pengambilan data otomatis, notifikasi, serta pemantauan real-time memerlukan implementasi teknis terpisah.

Prinsip: evidence first; pisahkan sinyal dari kejadian; severity proporsional; cari konfirmasi independen; nyatakan ketidakpastian; setiap alert harus actionable; seluruh perubahan dapat diaudit.

## 2. Klasifikasi alert

| Level | Makna | Bukti minimum dan respons |
|---|---|---|
| INFORMATIONAL | Perkembangan relevan, belum memenuhi ambang eskalasi | Satu sumber kredibel/data awal; catat dan masukkan brief |
| WATCH | Indikator menyimpang dari baseline atau weak signal berulang | Sumber dapat ditelusuri dan validasi awal; tingkatkan frekuensi review |
| WARNING | Eskalasi material masuk akal dalam horizon yang disebutkan | Idealnya dua sumber independen atau satu sumber primer kuat plus bukti pendukung; siapkan opsi mitigasi |
| CRITICAL | Dampak tinggi dan waktu respons pendek; kejadian terkonfirmasi atau indikator kuat menunjukkan risiko segera | Bukti primer/otoritatif atau konfirmasi multi-sumber; eskalasi segera melalui kanal yang disepakati |

Severity bukan probabilitas statistik. Jangan menyamakan CRITICAL dengan kepastian hasil. Jika bukti belum cukup, turunkan level atau beri status UNVERIFIED.

## 3. Jenis trigger

Trigger ditetapkan per tren di `docs/TREND_REGISTRY.md`; tidak ada ambang universal tanpa dasar.

- **Threshold:** indikator melewati ambang yang ditetapkan.
- **Rate-of-change:** kecepatan perubahan melampaui pola historis relevan.
- **Persistence:** penyimpangan bertahan selama periode konfirmasi.
- **Convergence:** beberapa indikator independen bergerak searah.
- **Event-based:** peristiwa terkonfirmasi, misalnya kebijakan resmi berlaku.
- **Contradiction/reversal:** bukti baru melemahkan tesis atau menunjukkan pembalikan.
- **Cross-domain spillover:** dampak menyebar ke domain atau aktor lain.

Setiap trigger harus mencatat definisi, kondisi, sumber, unit, baseline, ambang, periode konfirmasi, pengecualian, false-positive risk, severity maksimum awal, dan tindakan.

| Contoh trigger ilustratif | Tindakan |
|---|---|
| Threshold terlampaui | Validasi data, unit, dan baseline |
| Penyimpangan persisten | Review status dan skor |
| Konvergensi indikator independen | Analisis lintas-domain |
| Peristiwa resmi terkonfirmasi | Perbarui evidence ledger |
| Bukti berlawanan material | Re-score, turunkan severity, atau tutup alert |

Contoh ini bukan ambang faktual. Jumlah indikator/periode yang cukup bergantung pada konteks dan kualitas data.

## 4. Validasi sebelum publikasi

Checklist:
- [ ] Klaim utama spesifik dan dapat diuji.
- [ ] Tanggal kejadian dibedakan dari tanggal publikasi.
- [ ] URL, penerbit, dan waktu akses dicatat.
- [ ] Sumber primer dicari bila tersedia.
- [ ] Sindikasi tidak dihitung sebagai konfirmasi independen.
- [ ] Data dibandingkan dengan baseline, unit, cakupan, dan periode yang tepat.
- [ ] Bukti bertentangan dan alternatif penjelasan dicatat.
- [ ] Fakta, inferensi, skenario, dan rekomendasi dipisahkan.
- [ ] Confidence, keterbatasan, owner, tindakan, dan review date ditulis.
- [ ] Severity sebanding dengan bukti dan urgensi.

Status verifikasi:
- `UNVERIFIED` — belum cukup diperiksa.
- `PARTIALLY_VERIFIED` — sebagian unsur terkonfirmasi.
- `VERIFIED` — klaim inti didukung bukti memadai dan dapat ditelusuri.
- `DISPUTED` — bukti kredibel bertentangan dan belum terselesaikan.

Status dapat berbeda antar-klaim dalam satu alert. Jangan melabeli seluruh alert VERIFIED jika hanya sebagian klaim yang terkonfirmasi.

## 5. Confidence dan NIVCP
Confidence menilai kekuatan bukti, bukan dampak atau urgensi:
- **LOW:** sumber terbatas/tidak langsung atau gap penting.
- **MODERATE:** beberapa bukti sejalan, tetapi ketidakpastian material tersisa.
- **HIGH:** bukti kuat, relevan, mutakhir, dan terkonfirmasi secara independen atau oleh sumber primer otoritatif.

NIVCP tetap menilai karakteristik tren sesuai rubrik. Severity alert dinilai terpisah. Skor NIVCP tinggi tidak otomatis menghasilkan WARNING/CRITICAL; kejadian berisiko tinggi dapat memerlukan alert meski skor tren belum lengkap.

## 6. Alur kerja
1. **Detect:** trigger atau perkembangan teridentifikasi.
2. **Triage:** periksa relevansi, potensi dampak, horizon, dan duplikasi.
3. **Validate:** periksa klaim, sumber, baseline, independensi, dan kontradiksi.
4. **Assess:** tetapkan severity, confidence, domain terdampak, dan skenario.
5. **Approve:** WARNING/CRITICAL mendapat pemeriksaan kedua bila waktu memungkinkan. Dalam keadaan mendesak, alert awal boleh provisional dan harus ditinjau susulan.
6. **Disseminate:** kirim kepada audiens melalui kanal yang telah disepakati.
7. **Monitor:** pantau trigger, bukti baru, dan tenggat update.
8. **Resolve:** tutup, turunkan, atau eskalasi; catat alasan.

INFORMATIONAL masuk brief; WATCH masuk watchlist dengan owner; WARNING dieskalasikan kepada penanggung jawab analisis/pengambil keputusan; CRITICAL dieskalasikan segera melalui kanal operasional. Repository bukan kanal notifikasi darurat.

## 7. Format Early Warning Alert

```markdown
# MD V14 — EARLY WARNING ALERT
- Alert ID: MDV14-EW-YYYY-NNNN
- Version:
- Issued (timezone):
- Last updated:
- Severity: INFORMATIONAL / WATCH / WARNING / CRITICAL
- Verification: UNVERIFIED / PARTIALLY_VERIFIED / VERIFIED / DISPUTED
- Confidence: LOW / MODERATE / HIGH
- Related Trend ID:
- Domain / geography:
- Time horizon:
- Owner:
- Next review:

## 1. Alert headline
Satu kalimat tentang perubahan dan implikasi.

## 2. What happened / what changed
Pisahkan kejadian terkonfirmasi, indikator, dan interpretasi.

## 3. Why this matters
Mekanisme dampak, pihak terpapar, skala, dan urgensi.

## 4. Evidence
| Claim | Publisher | Event date | Publication date | URL | Verification |
|---|---|---|---|---|---|

## 5. Indicators and triggers
| Indicator | Baseline | Latest reading | Trigger | Status |
|---|---|---|---|---|

## 6. Assessment
- NIVCP (jika relevan):
- Severity rationale:
- Confidence rationale:
- Alternative explanations:
- Contradictory evidence:
- Key unknowns:

## 7. Outlook
- Base case:
- Upside:
- Downside:
- Escalation / de-escalation conditions:

## 8. Recommended actions
| Priority | Action | Owner role | Deadline / review |
|---|---|---|---|

## 9. Update log
| Time | Change | Reason | Evidence |
|---|---|---|---|

## Sources
Daftar tautan.
```

## 8. Cadence dan penutupan
Default cadence, sesuaikan dengan volatilitas:
- INFORMATIONAL: siklus brief berikutnya atau saat ada perubahan material.
- WATCH: review sekurang-kurangnya setiap 7 hari.
- WARNING: review sekurang-kurangnya setiap 24 jam selama aktif.
- CRITICAL: interval ditetapkan eksplisit sesuai laju kejadian dan kebutuhan respons.

Tutup/turunkan alert bila trigger tidak aktif, bukti inti dibatalkan, risiko mereda, atau horizon relevansi berakhir. Catat alasan, bukti, hasil, dan status Trend Registry terkait.

## 9. Audit dan kontrol mutu
Setiap alert memakai ID unik `MDV14-EW-YYYY-NNNN`; versi bertambah pada perubahan material. Simpan peran penyusun/peninjau, waktu deteksi-validasi-persetujuan-publikasi-update, sumber dan snapshot indikator, perubahan severity/confidence, keputusan eskalasi, serta alasan penutupan. Jangan menghapus versi lama.

## 10. Batas kemampuan
Dokumen ini tidak dengan sendirinya menarik data, memonitor indikator kontinu, mengirim SMS/email/push, menjamin deteksi dini, atau menggantikan penilaian manusia dan prosedur darurat. Klaim kemampuan tersebut hanya boleh dibuat setelah integrasi, scheduler, kanal notifikasi, dan pengujian teknis tersedia.
