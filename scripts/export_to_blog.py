#!/usr/bin/env python3
"""
Ekspor Data Regional BPS Sambas & Tren Berita ke Format Artikel Portal Blogspot.
Menjembatani sistem intelijen MD-V14 dengan repositori github-to-blogspot.
"""
import os
import sys
import json
import re
from datetime import datetime


def generate_sambas_data_article(airtable_json_path, output_dir="../github-to-blogspot/posts"):
    if not os.path.exists(airtable_json_path):
        print(f"[!] File data {airtable_json_path} tidak ditemukan.")
        return None

    with open(airtable_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    observations = data.get("observations", []) + data.get("pending_observations", [])
    if not observations:
        print("[!] Tidak ada observasi data regional yang ditemukan.")
        return None

    today_str = datetime.now().strftime("%Y-%m-%d")
    title = "Sorotan Data Ketenagakerjaan dan Indikator Ekonomi Kabupaten Sambas Terbaru"
    labels = ["Berita", "Bisnis"]
    description = f"Simak ringkasan data resmi BPS mengenai indikator ketenagakerjaan dan tren ekonomi Kabupaten Sambas periode {observations[0].get('period', 'terbaru')}."

    # Susun isi artikel berbasis data
    points_html = []
    for item in observations:
        ind_name = item.get("indicator_name", "Indikator Daerah")
        val = item.get("value", "-")
        unit = item.get("unit", "")
        period = item.get("period", "-")
        source = item.get("source", "BPS")
        points_html.append(f"- **{ind_name} (Tahun {period}):** Tercatat berada pada angka **{val} {unit}** *(Sumber: {source})*.")

    data_list_md = "\n".join(points_html)

    body = f"""
Pemerintah Kabupaten Sambas bersama lembaga statistik terus memperbarui pemantauan terhadap indikator sosial dan ketenagakerjaan daerah. Data resmi terkini dari pangkalan data **Badan Pusat Statistik (BPS)** menunjukkan dinamika serapan tenaga kerja dan stabilitas ekonomi masyarakat di tingkat kabupaten.

Ketersediaan data yang valid dan transparan menjadi pilar penting bagi pengambil kebijakan serta pelaku usaha daerah dalam memetakan potensi investasi dan program pemberdayaan masyarakat.

## Ringkasan Indikator Sosial dan Ketenagakerjaan Sambas

Berdasarkan laporan kompilasi intelijen data regional **PADUKA Sambas**, berikut adalah capaian angka indikator utama yang tercatat:

{data_list_md}

Angka-angka ini mencerminkan dinamika partisipasi angkatan kerja produktif yang terus bergerak positif di sektor-sektor unggulan seperti pertanian, perkebunan, dan perdagangan lokal.

## Penguatan Sektor Produktif dan Mitigasi Tantangan Ekonomi

Meskipun tingkat partisipasi angkatan kerja menunjukkan angka yang cukup tinggi, tantangan diversifikasi keterampilan bagi generasi muda tetap menjadi agenda strategis. Sinergi antara dunia pendidikan vokasi, pelatihan kerja daerah, dan sektor industri swasta diperlukan agar peluang kerja terbuka semakin luas.

Langkah ini sejalan dengan komitmen pemerintah daerah untuk memperkuat fondasi ekonomi kerakyatan, sebagaimana perhatian publik terhadap [kelayakan fasilitas dan infrastruktur daerah](https://padukasambas.blogspot.com/2025/11/viral-pondasi-tiang-listrik-di-sambas.html) yang menopang produktivitas warga sehari-hari.

Bagaimana pandangan Anda mengenai perkembangan serapan kerja dan iklim usaha di Kabupaten Sambas saat ini? Tuliskan gagasan dan tanggapan Anda di kolom komentar.

---
*Referensi: Dirangkum dari publikasi data resmi BPS Sambas & Sistem Analisis MD-V14 Paduka Sambas.*
"""

    slug = "sorotan-data-ekonomi-kabupaten-sambas-terbaru"
    filename = f"{today_str}-{slug}.md"
    os.makedirs(output_dir, exist_ok=True)
    target_path = os.path.join(output_dir, filename)

    frontmatter = f"""---
title: "{title}"
labels: {json.dumps(labels, ensure_ascii=False)}
description: "{description}"
status: "draft"
date: "{today_str}"
---
{body.strip()}
"""
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    print(f"[+] Artikel jurnalisme data regional berhasil diekspor: {target_path}")
    return target_path


if __name__ == "__main__":
    airtable_path = sys.argv[1] if len(sys.argv) > 1 else "examples/airtable-bps-dashboard.json"
    generate_sambas_data_article(airtable_path)
