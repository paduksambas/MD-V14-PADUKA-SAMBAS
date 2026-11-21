# MD V14 — Paduka Sambas Global Trend Intelligence

Repositori pengembangan plugin/agent untuk riset tren global, intelijen strategis, analisis dampak, dan briefing yang dapat ditindaklanjuti.

## Status
- Build 1.2 — integrated deterministic intelligence pipeline + JSON CLI
- Bahasa utama: Indonesia; sumber global dapat dianalisis dalam bahasa apa pun
- Python: 3.11+
- Pengujian: unittest + GitHub Actions

## Struktur utama
- `plugin/INSTRUCTIONS.md` — instruksi inti plugin
- `mdv14/trend_registry.py` — normalisasi dan deduplikasi sinyal
- `mdv14/fact_check.py` — pemeriksaan kelengkapan metadata dan URL
- `mdv14/early_warning.py` — klasifikasi tingkat peringatan
- `mdv14/daily_brief.py` — pembentuk laporan harian
- `mdv14/pipeline.py` — orkestrasi seluruh tahap
- `mdv14/storage.py` — input/output JSON atomik
- `mdv14/__main__.py` — antarmuka command line
- `examples/signals.sample.json` — contoh input
- `tests/` — pengujian otomatis
- `.github/workflows/tests.yml` — CI GitHub Actions

## Menjalankan pengujian
```bash
python -m unittest discover -s tests -v
```

## Menjalankan pipeline
```bash
python -m mdv14 examples/signals.sample.json --output build/report.json
```

Untuk integrasi Python:
```python
from mdv14 import run_pipeline
report = run_pipeline([{
    "title": "Contoh tren",
    "source": "Nama sumber",
    "url": "https://example.com/report",
    "summary": "Ringkasan dari sumber",
    "category": "Technology",
    "score": 72,
}])
```

## Prinsip integritas
Pisahkan fakta, interpretasi, prediksi, dan rekomendasi. Cantumkan tanggal, sumber, tingkat keyakinan, serta ketidakpastian. Jangan mengarang data atau menganggap tren sebagai kepastian.

Pemeriksaan metadata dan format URL bukan verifikasi kebenaran. Skor peringatan adalah heuristik dari input, bukan probabilitas atau prediksi terverifikasi. Pengumpulan tren langsung, pemeriksaan silang sumber, dan notifikasi produksi memerlukan integrasi lanjutan.
