"""Generate a self-contained, offline HTML analytics dashboard."""
from __future__ import annotations

from collections import Counter
from html import escape
from math import isfinite
from typing import Any
from urllib.parse import urlparse
from .country_explorer import render_country_explorer_html
from .economic_intelligence import render_economic_intelligence_html
from .economic_data import render_world_bank_html
from .market_data import render_fred_html, render_public_market_html
from .market_analytics import render_market_analytics_html
from .public_assets import render_public_asset_html
from .commodity_data import render_world_bank_commodity_html
from .indonesia_intelligence import render_indonesia_economic_html
from .regional_intelligence import render_regional_intelligence_html


def _cell(value: Any) -> str:
    return escape(str(value if value is not None else ""), quote=True)


def _score(value: Any) -> float:
    """Return a safe numeric score for dashboard sorting and averages."""
    try:
        score = float(value or 0)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    return score if isfinite(score) else 0.0



def _safe_count(value: Any) -> int:
    """Normalize malformed count values to zero for dashboard rendering."""
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError, OverflowError):
        return 0


def build_dashboard_html(report: dict[str, Any]) -> str:
    """Render an accessible static dashboard from an existing MD V14 report."""
    signals = report.get("signals", [])
    brief = report.get("daily_brief", {})
    warning_counts = report.get("warning_summary", {})
    categories = Counter(str(item.get("category") or "Unclassified") for item in signals)
    history = [item.get("history") for item in signals if item.get("history")]
    reviewed = sum(1 for item in signals if not item.get("evidence", {}).get("evidence_complete", False))
    avg_score = (sum(_score(item.get("score")) for item in signals) / len(signals)) if signals else 0.0
    source_status_counts = Counter(
        (item.get("source_intelligence") or {}).get("status", "not assessed")
        for item in signals
    )
    source_rows = []
    for item in sorted(signals, key=lambda x: str(x.get("title", "")).casefold()):
        assessment = item.get("source_intelligence") or {}
        source_rows.append(
            "<tr>"
            f"<td>{_cell(item.get('title'))}</td>"
            f"<td>{_cell(item.get('source'))}</td>"
            f"<td>{_cell(assessment.get('source_domain') or 'tidak diketahui')}</td>"
            f"<td>{_cell(assessment.get('status', 'belum dinilai'))}</td>"
            f"<td class='num'>{_cell(str(assessment.get('metadata_checks_passed', '—')) + '/' + str(assessment.get('metadata_checks_total', '—')))}</td>"
            "<td>Belum dinilai</td>"
            "</tr>"
        )
    if not source_rows:
        source_rows.append("<tr><td colspan='6'>Tidak ada catatan sumber untuk dinilai.</td></tr>")

    rows = []
    for item in sorted(signals, key=lambda x: _score(x.get("score")), reverse=True):
        hist = item.get("history") or {}
        warning = item.get("warning") or {}
        advanced = item.get("advanced_intelligence") or {}
        anomaly = advanced.get("anomaly") or {}
        anomaly_label = "Perubahan tidak lazim — perlu ditinjau" if anomaly.get("detected") else anomaly.get("status", "belum dinilai")
        rows.append(
            "<tr>"
            f"<td>{_cell(item.get('title'))}</td>"
            f"<td>{_cell(item.get('category'))}</td>"
            f"<td class='num'>{_cell(item.get('score', 0))}</td>"
            f"<td>{_cell(warning.get('level', 'tidak diketahui'))}</td>"
            f"<td>{_cell(hist.get('direction', 'belum ada riwayat'))}</td>"
            f"<td class='num'>{_cell(advanced.get('momentum', '—'))}</td>"
            f"<td class='num'>{_cell(advanced.get('acceleration', '—'))}</td>"
            f"<td>{_cell(anomaly_label)}</td>"
            f"<td>{_cell(advanced.get('confidence', 'belum dinilai'))}</td>"
            f"<td>{_cell(item.get('source') or 'Perlu tinjauan sumber')}</td>"
            "</tr>"
        )
    if not rows:
        rows.append("<tr><td colspan='10'>Tidak ada sinyal tren dalam laporan ini.</td></tr>")

    category_rows = "".join(
        f"<tr><td>{_cell(name)}</td><td class='num'>{count}</td></tr>"
        for name, count in sorted(categories.items(), key=lambda pair: (-pair[1], pair[0].casefold()))
    ) or "<tr><td colspan='2'>Tidak ada data kategori.</td></tr>"

    def metric(label: str, value: Any, note: str = "") -> str:
        return (f"<article class='metric'><div class='muted'>{_cell(label)}</div>"
                f"<strong>{_cell(value)}</strong><small>{_cell(note)}</small></article>")

    intelligence = report.get("global_intelligence") or {}
    country_explorer_html = render_country_explorer_html(report.get("country_explorer") or {})
    economic_intelligence_html = render_economic_intelligence_html(report.get("economic_intelligence") or {})
    world_bank_html = render_world_bank_html(report.get("economic_data") or {})
    public_market_html = render_public_market_html(report.get("market_data") or {})
    public_asset_html = render_public_asset_html(report.get("public_asset_data") or {})
    commodity_html = render_world_bank_commodity_html(report.get("commodity_data") or {})
    indonesia_economic_html = render_indonesia_economic_html(report.get("indonesia_economic_intelligence") or {})
    regional_intelligence_html = render_regional_intelligence_html(report.get("regional_intelligence") or {})
    fred_market_html = render_fred_html(report.get("fred_market_data") or {})
    market_analytics_html = render_market_analytics_html(report.get("market_analytics") or {})

    def group_rows(items: list[dict[str, Any]]) -> str:
        rendered = []
        for item in items:
            name = _cell(item.get("name", "Unknown"))
            count = _safe_count(item.get("signal_count"))
            average = _score(item.get("average_score"))
            width = max(0.0, min(100.0, average))
            rendered.append(
                "<tr>"
                f"<td>{name}</td><td class='num'>{count}</td>"
                f"<td class='num'>{average:.1f}</td>"
                f"<td><div class='bar-track' role='img' aria-label='Skor rata-rata {average:.1f} dari 100'>"
                f"<span class='bar-fill' style='width:{width:.1f}%'></span></div></td></tr>"
            )
        return "".join(rendered) or "<tr><td colspan='4'>Data intelijen global tidak tersedia.</td></tr>"

    country_rows = group_rows(intelligence.get("country_analysis", []))
    topic_rows = group_rows(intelligence.get("topic_analysis", []))

    rising_rows = []
    for item in intelligence.get("rising_signals", []):
        rising_rows.append(
            "<tr>"
            f"<td>{_cell(item.get('title'))}</td>"
            f"<td>{_cell(item.get('country', 'tidak diketahui'))}</td>"
            f"<td>{_cell(', '.join(item.get('topics', [])))}</td>"
            f"<td class='num'>{_cell(item.get('score'))}</td>"
            f"<td class='num'>{_cell(item.get('momentum'))}</td>"
            "</tr>"
        )
    if not rising_rows:
        rising_rows.append("<tr><td colspan='5'>Tidak ada sinyal tren naik dengan riwayat memadai.</td></tr>")

    relation_rows = []
    for item in intelligence.get("related_events", []):
        basis = ", ".join(item.get("relationship_basis", []))
        relation_rows.append(
            "<tr>"
            f"<td>{_cell(item.get('left_title'))}</td>"
            f"<td>{_cell(item.get('left_country', 'tidak diketahui'))}</td>"
            f"<td>{_cell(item.get('right_title'))}</td>"
            f"<td>{_cell(item.get('right_country', 'tidak diketahui'))}</td>"
            f"<td>{_cell(basis)}</td>"
            "</tr>"
        )
    if not relation_rows:
        relation_rows.append("<tr><td colspan='5'>Tidak ada kandidat keterkaitan peristiwa yang teridentifikasi.</td></tr>")

    language_data = report.get("language_intelligence") or {}
    language_counts = language_data.get("language_counts", {})
    language_rows = "".join(
        f"<tr><td>{_cell(language)}</td><td class='num'>{_cell(count)}</td></tr>"
        for language, count in sorted(language_counts.items())
    ) or "<tr><td colspan='2'>Tidak ada metadata bahasa terdata.</td></tr>"
    language_cards = "".join([
        metric("Bahasa terdata", language_data.get("records_with_declared_language", 0), "Hanya metadata eksplisit"),
        metric("Bahasa tidak dikenal", language_data.get("records_with_unknown_language", 0), "Tidak disimpulkan otomatis"),
        metric("Ragam bahasa", len(language_counts), "Label bahasa terdata"),
    ])
    graph = report.get("knowledge_graph") or {}
    graph_nodes = graph.get("nodes", [])
    graph_edges = graph.get("edges", [])
    graph_type_labels = {
        "company": "Perusahaan",
        "country": "Negara",
        "intergovernmental_organization": "Organisasi antarpemerintah",
        "supranational": "Organisasi supranasional",
        "organization": "Organisasi",
        "person": "Orang",
        "event": "Peristiwa",
        "topic": "Topik",
        "explicit_entity": "Entitas dari metadata",
    }
    graph_evidence_labels = {
        "title_or_summary_alias": "Ditemukan dalam judul/ringkasan berita",
        "explicit_metadata": "Dicantumkan dalam metadata sumber",
        "source_record": "Berasal dari rekaman sumber",
    }
    graph_relation_labels = {
        "mentions_entity": "Menyebut entitas",
        "tagged_with_topic": "Diberi topik",
        "declared_country": "Negara yang dicantumkan",
        "shared_entity": "Entitas yang sama terdeteksi",
        "shared_topic": "Topik yang sama terdeteksi",
        "same_declared_country": "Negara yang sama dicantumkan",
    }
    graph_node_labels = {
        str(item.get("id")): f"{item.get('label', '')} ({graph_type_labels.get(str(item.get('type') or ''), str(item.get('type') or 'Entitas').replace('_', ' ').capitalize())})"
        for item in graph_nodes
        if item.get("id")
    }
    graph_node_rows = "".join(
        "<tr><td>" + _cell(item.get("label")) + "</td><td>" + _cell(graph_type_labels.get(str(item.get("type") or ""), str(item.get("type") or "Belum diklasifikasikan").replace("_", " ").capitalize())) + "</td><td>" + _cell(", ".join(graph_evidence_labels.get(str(source), str(source).replace("_", " ").capitalize()) for source in item.get("evidence_sources", []))) + "</td></tr>"
        for item in graph_nodes
    ) or "<tr><td colspan=\"3\">Belum ada entitas atau simpul yang terdeteksi.</td></tr>"
    graph_edge_rows = "".join(
        "<tr><td>" + _cell(graph_relation_labels.get(str(item.get("relation") or ""), str(item.get("relation") or "").replace("_", " ").capitalize())) + "</td><td>" + _cell(graph_node_labels.get(str(item.get("source")), str(item.get("source") or ""))) + "</td><td>" + _cell(graph_node_labels.get(str(item.get("target")), str(item.get("target") or ""))) + "</td><td>" + _cell(", ".join(str(record_id) for record_id in item.get("supporting_record_ids", []))) + "</td></tr>"
        for item in graph_edges
    ) or "<tr><td colspan=\"4\">Belum ada hubungan antarsimpul yang teridentifikasi.</td></tr>"
    graph_cards = "".join([
        metric("Jumlah simpul", graph.get("nodes_total", 0), "Entitas, peristiwa, topik, dan negara"),
        metric("Hubungan terpetakan", graph.get("edges_total", 0), "Petunjuk keterkaitan untuk ditinjau"),
        metric("Berita dengan entitas terdeteksi", graph.get("records_with_recognized_entities", 0), "Alias terkurasi atau metadata eksplisit"),
    ])
    monitoring = report.get("monitoring") or {}
    generated_at = monitoring.get("generated_at") or (report.get("command_center") or {}).get("generated_at") or ""
    source_status = []
    for key, label in (
        ("market_data", "Kurs valas"),
        ("commodity_data", "Komoditas"),
        ("economic_data", "World Bank"),
        ("regional_intelligence", "Data regional BPS"),
        ("airtable_regional_data", "Airtable BPS"),
        ("bps_regional_tables", "Konektor tabel BPS"),
        ("bps_public_export", "Impor ekspor BPS"),
        ("fred_market_data", "FRED"),
    ):
        payload = report.get(key)
        if isinstance(payload, dict):
            source_status.append((label, str(payload.get("status") or "not_reported")))
    status_labels = {
        "available": "tersedia", "partial": "tersedia sebagian",
        "not_configured": "belum dihubungkan", "not_reported": "belum dilaporkan",
        "unavailable": "tidak tersedia", "pending_validation": "menunggu pemeriksaan",
        "no_data": "belum ada data", "no_validated_records": "belum ada data tervalidasi",
    }
    source_status_html = "".join(
        f"<li><span>{_cell(label)}</span><b class='status-value'>{_cell(status_labels.get(status, status.replace('_', ' ')))}</b></li>"
        for label, status in source_status
    ) or "<li>Status sumber belum tersedia pada laporan ini.</li>"
    decision = report.get("strategic_decision") or {}
    review_rows = []
    for item in decision.get("review_queue", []):
        review_rows.append("<tr>" + f"<td>{_cell(item.get('priority_band'))}</td><td>{_cell(item.get('title'))}</td><td class='num'>{_cell(item.get('priority_score'))}</td><td>{_cell(item.get('warning_level'))}</td><td>{_cell(item.get('source'))}</td><td>{_cell(item.get('url') or 'Tidak tersedia')}</td>" + "</tr>")
    if not review_rows:
        review_rows.append("<tr><td colspan='6'>Tidak ada catatan dalam antrean tinjauan strategis.</td></tr>")
    analyst = report.get("analyst_report") or {}
    analyst_findings = []
    for item in analyst.get("key_findings", []):
        analyst_findings.append(
            "<tr><td>" + _cell(item.get("review_priority")) + "</td><td>" +
            _cell(item.get("title")) + "</td><td>" + _cell(item.get("source")) +
            "</td><td>" + _cell(item.get("country")) + "</td><td>" +
            _cell(item.get("signal_id")) + "</td></tr>"
        )
    if not analyst_findings:
        analyst_findings.append("<tr><td colspan=\"5\">Tidak ada temuan analis yang tersedia.</td></tr>")
    analyst_actions = "".join(
        "<li><span>" + _cell(item.get("priority")) + " — " + _cell(item.get("action")) + "</span></li>"
        for item in analyst.get("recommended_human_actions", [])
    ) or "<li>Tidak ada tindakan tinjauan yang tersedia.</li>"
    analyst_uncertainties = "".join("<li>" + _cell(item) + "</li>" for item in analyst.get("uncertainties_and_gaps", []))
    analyst_cards = "".join([
        metric("Temuan analis", len(analyst.get("key_findings", [])), "Kandidat prioritas yang dapat ditelusuri"),
        metric("Celah bukti", (analyst.get("metadata_coverage") or {}).get("records_with_incomplete_evidence_metadata", 0), "Hanya metadata"),
        metric("Ketidakpastian", len(analyst.get("uncertainties_and_gaps", [])), "Peringatan eksplisit"),
    ])
    command = report.get("command_center") or {}
    command_cycle = command.get("collection_cycle") or {}
    command_posture = command.get("strategic_posture") or {}
    command_coverage = command.get("coverage") or {}
    command_metrics = "".join([
        metric("Status operasional", command.get("operational_state", "belum dinilai"), "Hanya siklus umpan terkonfigurasi"),
        metric("Postur strategis", command_posture.get("status", "belum dinilai"), "Petunjuk tinjauan manusia heuristik"),
        metric("Sinyal dianalisis", command_coverage.get("signals_analyzed", len(signals)), "Laporan saat ini"),
        metric("Umpan berhasil", str(command_cycle.get("feeds_succeeded", 0)) + "/" + str(command_cycle.get("feeds_attempted", 0)), "Siklus pengumpulan terakhir"),
        metric("Prioritas tinjauan tinggi", command_posture.get("high_review_priority", 0), "Bukan tingkat keparahan ancaman"),
        metric("Celah bukti", command_posture.get("evidence_review_required", reviewed), "Hanya kelengkapan metadata"),
    ])
    command_queue_rows = "".join(
        "<tr><td>" + _cell(item.get("priority_band")) + "</td><td>" + _cell(item.get("title")) +
        "</td><td>" + _cell(item.get("country")) + "</td><td>" + _cell(item.get("source")) +
        "</td><td>" + _cell(item.get("signal_id")) + "</td></tr>"
        for item in command.get("priority_review_queue", [])
    ) or "<tr><td colspan=\"5\">Tidak ada item tinjauan prioritas.</td></tr>"
    decision_gate_rows = "".join("<li>" + _cell(item) + "</li>" for item in command.get("decision_gates", []))
    if not decision_gate_rows:
        decision_gate_rows = "<li>Diperlukan tinjauan manusia sebelum tindakan diambil.</li>"
    monitor_cards = "".join([
        metric("Siklus pemantauan", monitoring.get("cycle_status", "belum dikonfigurasi"), "Siklus pengumpulan terakhir"),
        metric("Umpan berfungsi", f"{monitoring.get('feeds_succeeded', 0)}/{monitoring.get('feeds_attempted', 0)}", "Titik akhir RSS/Atom"),
        metric("Item terkumpul", monitoring.get("signals_collected", len(signals)), "Catatan dalam siklus ini"),
        metric("Terbit dalam 24 jam", monitoring.get("signals_published_within_window", 0), "Hanya stempel waktu valid"),
        metric("Waktu terbit tidak diketahui", monitoring.get("signals_with_unknown_published_at", 0), "Stempel waktu hilang atau tidak valid"),
    ])

    global_cards = "".join([
        metric("Sinyal dianalisis", intelligence.get("signals_analyzed", 0), "Input intelijen global"),
        metric("Negara terwakili", len(intelligence.get("country_analysis", [])), "Hanya metadata eksplisit"),
        metric("Topik terwakili", len(intelligence.get("topic_analysis", [])), "Topik/kategori yang disediakan"),
        metric("Sinyal tren naik", len(intelligence.get("rising_signals", [])), "Momentum historis positif"),
        metric("Kandidat keterkaitan peristiwa", len(intelligence.get("related_events", [])), "Bukan temuan sebab-akibat"),
    ])
    title = "PADUKA Sambas — Pusat Data dan Informasi Publik"
    date_label = brief.get("date", "Tanggal tidak tersedia")
    regional_data = report.get("regional_intelligence") or {}
    region_profiles = regional_data.get("region_profiles", [])
    region_profiles = region_profiles if isinstance(region_profiles, list) else []
    sambas_profiles = [
        item for item in region_profiles
        if isinstance(item, dict) and str(item.get("region_name") or "").strip().casefold() == "kabupaten sambas"
    ]
    sambas_profiles.sort(key=lambda item: str(item.get("latest_period") or ""), reverse=True)

    def public_number(value: Any) -> str:
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return _cell(value)
        if not isfinite(number):
            return "Tidak tersedia"
        rendered = f"{number:,.2f}".replace(",", "§").replace(".", ",").replace("§", ".")
        return rendered[:-3] if rendered.endswith(",00") else rendered

    def public_source_link(value: Any) -> str:
        url = str(value or "").strip()
        try:
            parsed = urlparse(url)
        except ValueError:
            return ""
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or not (host == "go.id" or host.endswith(".go.id")):
            return ""
        return f'<a class="source-link" href="{_cell(url)}" target="_blank" rel="noopener noreferrer">Lihat sumber resmi</a>'

    public_indicator_cards = []
    for item in sambas_profiles[:6]:
        unit = str(item.get("unit") or "").strip()
        is_percent = unit.casefold() in {"persen", "percent", "%"}
        displayed_value = public_number(item.get("latest_value"))
        if is_percent:
            displayed_value += "%"
        elif unit:
            displayed_value += " " + _cell(unit)
        source_link = public_source_link(item.get("source_url"))
        source_markup = source_link or '<span class="source-unavailable">Tautan sumber belum tersedia</span>'
        public_indicator_cards.append(
            '<article class="public-indicator-card">'
            f'<div class="indicator-period">{_cell(item.get("latest_period") or "Periode tidak tersedia")}</div>'
            f'<h3>{_cell(item.get("indicator_name") or "Indikator daerah")}</h3>'
            f'<strong class="indicator-value">{displayed_value}</strong>'
            '<p>Nilai terakhir yang tercatat untuk Kabupaten Sambas. Perhatikan periode dan definisi indikator saat membandingkan data.</p>'
            f'{source_markup}'
            '</article>'
        )
    if not public_indicator_cards:
        public_indicator_cards_html = (
            '<div class="public-empty"><strong>Data indikator Sambas belum tersedia pada laporan ini.</strong>'
            '<p>Bagian ini akan menampilkan angka setelah data daerah tersedia dan sumbernya dapat ditelusuri.</p>'
            '<a href="https://sambaskab.bps.go.id/id/statistics-table" target="_blank" rel="noopener noreferrer">Jelajahi tabel resmi BPS Sambas</a></div>'
        )
    else:
        public_indicator_cards_html = "".join(public_indicator_cards)

    latest_sambas_period = max(
        (str(item.get("latest_period") or "") for item in sambas_profiles),
        default="Belum tersedia",
    )
    source_domains = set()
    for item in sambas_profiles:
        try:
            parsed_url = urlparse(str(item.get("source_url") or ""))
        except ValueError:
            continue
        host = (parsed_url.hostname or "").lower()
        if parsed_url.scheme == "https" and (host == "go.id" or host.endswith(".go.id")):
            source_domains.add(host)
    airtable_summary = regional_data.get("airtable") if isinstance(regional_data.get("airtable"), dict) else {}
    pending_public_count = _safe_count(airtable_summary.get("pending_validation_count", 0))
    public_summary_cards = "".join([
        metric("Indikator Sambas", len(sambas_profiles), "Indikator daerah yang termuat"),
        metric("Periode terbaru", latest_sambas_period, "Mengikuti periode masing-masing data"),
        metric("Sumber tercantum", len(source_domains), "Domain sumber pada indikator Sambas"),
        metric("Menunggu pemeriksaan", pending_public_count, "Belum ditampilkan sebagai angka utama"),
    ])
    cards = "".join([
        metric("Sinyal tren", len(signals), "Dalam laporan ini"),
        metric("Skor rata-rata", f"{avg_score:.1f}/100", "Skor heuristik yang diberikan"),
        metric("Perlu tinjauan sumber", reviewed, "Hanya kelengkapan metadata"),
        metric("Memiliki riwayat", len(history), "Observasi tersimpan"),
        metric("Catatan sumber dinilai", sum(source_status_counts.values()), "Hanya daftar periksa metadata"),
    ])
    warning_labels = {"critical": "Kritis", "elevated": "Perhatian tinggi", "watch": "Pantauan", "normal": "Normal"}
    warnings = "".join(
        f"<li><span>{_cell(warning_labels.get(level, level.title()))}</span><b>{_cell(count)}</b></li>"
        for level, count in (("critical", warning_counts.get("critical", 0)),
                             ("elevated", warning_counts.get("elevated", 0)),
                             ("watch", warning_counts.get("watch", 0)),
                             ("normal", warning_counts.get("normal", 0)))
    )
    source_summary = "".join(
        f"<li><span>{_cell(status.replace('_', ' '))}</span><b>{_cell(count)}</b></li>"
        for status, count in sorted(source_status_counts.items())
    ) or "<li>Tidak ada penilaian sumber</li>"
    return f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_cell(title)}</title>
<meta name="description" content="PADUKA Sambas — informasi publik daerah, ekonomi Indonesia, dan tren global. MD V14 Trend Intelligence Dashboard.">
<style>
:root{{color-scheme:light;--bg:#f3f7f5;--panel:#ffffff;--line:#dbe5e0;--muted:#52665e;--text:#172b24;--accent:#08765b;--accent-soft:#e6f2ed;--navy:#12372e}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth;scroll-padding-top:18px}}body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:1240px;margin:auto;padding:24px 24px 64px}}header{{margin-bottom:18px}}h1{{font-size:clamp(2rem,4vw,3.25rem);line-height:1.12;letter-spacing:-.035em;margin:0 0 14px;max-width:760px}}h2{{font-size:1.2rem;line-height:1.3;margin:0 0 14px;letter-spacing:-.01em}}h3{{font-size:1rem;line-height:1.35}}p{{margin:0 0 12px}}a{{color:#075d49}}a:focus-visible,button:focus-visible,select:focus-visible{{outline:3px solid #f0b94f;outline-offset:3px}}.muted,small{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:12px;margin:18px 0}}
.metric,.panel{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 2px 10px rgba(20,55,42,.035)}}.metric strong{{display:block;font-size:1.8rem;line-height:1.2;margin:6px 0}}.metric small{{display:block;line-height:1.45}}
.columns{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0}}@media(max-width:700px){{.columns{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;width:100%;font-size:.92rem}}th,td{{text-align:left;padding:11px 9px;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:#40574e;font-weight:700;background:#f7faf8}}.num{{font-variant-numeric:tabular-nums;text-align:right}}.table-wrap{{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;overscroll-behavior-x:contain}}ul{{list-style:none;padding:0;margin:0}}li{{display:flex;justify-content:space-between;gap:14px;padding:8px 0;border-bottom:1px solid var(--line)}}.bar-track{{height:9px;min-width:100px;background:#e3ece7;border-radius:99px;overflow:hidden}}.bar-fill{{display:block;height:100%;background:var(--accent);border-radius:99px}}.map-wrap{{background:#f7faf8;border:1px solid var(--line);border-radius:12px;overflow:hidden}}.world-plot{{display:block;width:100%;height:auto;max-height:480px}}.map-bg{{fill:#edf4f0}}.map-gridline{{stroke:#c8d9d0;stroke-width:1;stroke-dasharray:3 5}}.country-marker{{cursor:pointer;outline:none}}.country-marker circle,.legend-dot{{stroke:#fff;stroke-width:1.5;fill:#08765b}}.country-marker.priority-high circle,.legend-dot.priority-high{{fill:#bd4444}}.country-marker.priority-medium circle,.legend-dot.priority-medium{{fill:#b7791f}}.country-marker.priority-routine circle,.legend-dot.priority-routine{{fill:#08765b}}.country-marker:focus circle,.country-marker:hover circle{{stroke:#172b24;stroke-width:3}}.map-legend,.country-picker{{display:flex;flex-wrap:wrap;gap:9px;margin:12px 0}}.map-legend span{{display:flex;align-items:center;gap:6px;color:var(--muted);font-size:.85rem}}.legend-dot{{display:inline-block;width:11px;height:11px;border-radius:50%}}.country-select{{background:#fff;border:1px solid var(--line);border-radius:8px;color:var(--text);padding:8px 10px;cursor:pointer}}.country-select[aria-pressed=true]{{border-color:var(--accent);outline:1px solid var(--accent)}}.country-detail{{padding:14px;border:1px solid var(--line);border-radius:10px;background:#fff}}.country-detail[hidden]{{display:none}}.notice{{border-left:3px solid var(--accent);padding:12px 15px;background:var(--accent-soft);border-radius:7px;color:#35564a;margin-top:18px}}footer{{margin-top:22px;color:var(--muted);font-size:.88rem;border-top:1px solid var(--line);padding-top:18px}}.control-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:16px 0}}.control-card{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px}}.control-card h3{{margin:0 0 8px;font-size:1rem}}.control-card p{{margin:0;color:var(--muted)}}.control-status{{display:inline-block;padding:4px 9px;border:1px solid var(--line);border-radius:999px;font-size:.8rem;margin-bottom:8px}}.notification-list{{display:grid;gap:8px}}.notification-item{{padding:10px 12px;border-left:3px solid var(--accent);background:var(--accent-soft);border-radius:5px}}.notification-item strong{{display:block}}.notification-item span{{color:var(--muted);font-size:.9rem}}.quick-nav{{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 24px;padding:8px 0}}.quick-nav a{{display:inline-block;border:1px solid var(--line);background:#fff;border-radius:999px;padding:8px 14px;color:#24473b;text-decoration:none;font-size:.9rem;font-weight:650}}.quick-nav a:hover,.quick-nav a:focus{{border-color:var(--accent);outline:1px solid var(--accent);background:var(--accent-soft)}}.live-clock{{font-size:clamp(2rem,6vw,3.2rem);font-weight:750;font-variant-numeric:tabular-nums;letter-spacing:.03em;color:var(--navy)}}.status-value{{text-transform:capitalize;color:var(--accent)}}
.quick-nav{{display:flex;flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;position:sticky;top:8px;z-index:8;background:rgba(243,247,245,.94);backdrop-filter:blur(10px);border:1px solid var(--line);border-radius:999px;padding:7px;margin:12px 0 20px;scrollbar-width:none}}
.quick-nav::-webkit-scrollbar{{display:none}}
.accordion-intro{{margin:18px 0 10px;color:var(--muted);font-size:.92rem}}
.content-accordion{{margin:12px 0;background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:0 2px 10px rgba(20,55,42,.035)}}
.content-accordion>summary{{display:flex;align-items:center;gap:13px;cursor:pointer;list-style:none;padding:17px 19px;min-height:76px;background:linear-gradient(110deg,#fff 0%,#f7fbf8 100%);}}
.content-accordion>summary::-webkit-details-marker{{display:none}}
.content-accordion>summary:hover{{background:var(--accent-soft)}}
.accordion-symbol{{display:grid;place-items:center;flex:0 0 40px;width:40px;height:40px;border-radius:12px;background:var(--accent-soft);color:#145b45;font-size:1.25rem;font-weight:800}}
.accordion-copy{{display:grid;gap:3px;min-width:0}}
.accordion-copy strong{{font-size:1rem;color:var(--text);line-height:1.3}}
.accordion-copy small{{font-size:.84rem;color:var(--muted);font-weight:450;line-height:1.35}}
.accordion-toggle{{margin-left:auto;flex:0 0 28px;width:28px;height:28px;border-radius:50%;border:1px solid var(--line);position:relative;background:#fff}}
.accordion-toggle:before,.accordion-toggle:after{{content:"";position:absolute;left:8px;right:8px;top:13px;height:2px;background:var(--accent);border-radius:2px}}
.accordion-toggle:after{{transform:rotate(90deg);transition:transform .18s ease}}
.content-accordion[open]>summary{{border-bottom:1px solid var(--line);background:#f7fbf8}}
.content-accordion[open] .accordion-toggle:after{{transform:rotate(0)}}
.accordion-body{{padding:2px 14px 14px}}
.accordion-body>.panel,.accordion-body>.columns,.accordion-body>.grid{{margin-top:14px}}
.accordion-body>.panel:last-child{{margin-bottom:0}}
@media(max-width:520px){{.content-accordion>summary{{padding:14px 13px;gap:10px;min-height:70px}}.accordion-symbol{{flex-basis:36px;width:36px;height:36px}}.accordion-copy small{{font-size:.78rem}}.accordion-body{{padding:1px 9px 10px}}.quick-nav{{margin-left:-2px;margin-right:-2px}}}}
.site-hero{{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(230px,.65fr);gap:30px;align-items:center;background:#e8f2ed;border:1px solid #d4e5dc;border-radius:24px;padding:clamp(24px,5vw,54px);margin:0 0 18px;position:relative;overflow:hidden}}.site-topline{{display:flex;align-items:center;gap:12px;margin-bottom:28px;color:#1e4e3e;font-weight:800;letter-spacing:.04em}}.brand-mark{{display:grid;place-items:center;width:42px;height:42px;border-radius:13px;background:#0f6049;color:#fff;font-size:1.2rem;letter-spacing:0}}.brand-name{{font-size:1rem;line-height:1.2}}.brand-subtitle{{display:block;color:#526d61;font-size:.78rem;font-weight:550;letter-spacing:0;margin-top:3px}}.hero-eyebrow{{font-size:.8rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:#17664e;margin-bottom:12px}}.hero-copy{{font-size:1.08rem;max-width:680px;color:#3d5d50;margin:0 0 22px}}.hero-actions{{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0}}.hero-actions a{{display:inline-block;text-decoration:none;padding:11px 17px;border-radius:999px;font-weight:750;background:#0b684f;color:#fff}}.hero-actions a.secondary{{background:#fff;color:#174c3c;border:1px solid #c9ddd2}}.hero-meta{{display:flex;flex-wrap:wrap;gap:9px 18px;color:#4b6759;font-size:.88rem}}.hero-aside{{background:#fff;border:1px solid #d3e2d9;border-radius:18px;padding:23px;box-shadow:0 10px 26px rgba(23,73,54,.06)}}.hero-aside-label{{font-size:.76rem;color:#527466;letter-spacing:.1em;text-transform:uppercase;font-weight:800}}.hero-aside strong{{display:block;color:#12372e;font-size:1.5rem;line-height:1.25;margin:12px 0}}.hero-aside p{{color:#4b6759;font-size:.92rem}}.legacy-title{{font-size:.78rem;color:#6d8177}}.public-section{{margin:22px 0}}.public-section-lead{{max-width:780px;color:var(--muted);margin:-6px 0 16px}}.public-indicator-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:16px 0}}.public-indicator-card{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:19px;box-shadow:0 2px 10px rgba(20,55,42,.035)}}.indicator-period{{display:inline-block;padding:4px 9px;border-radius:999px;background:var(--accent-soft);color:#145b45;font-size:.78rem;font-weight:750}}.public-indicator-card h3{{margin:12px 0 6px;min-height:2.5em;font-size:1rem}}.indicator-value{{display:block;font-size:2.15rem;line-height:1.2;color:#0d5e48;font-variant-numeric:tabular-nums;margin:8px 0}}.public-indicator-card p{{font-size:.9rem;color:var(--muted);min-height:4.2em}}.source-link{{font-weight:750;text-decoration:none;border-bottom:1px solid #9cc9b5;padding-bottom:2px}}.source-unavailable{{font-size:.85rem;color:var(--muted)}}.public-empty{{padding:22px;border:1px dashed #a9c7b8;border-radius:16px;background:#fbfdfb}}.public-empty p{{color:var(--muted);margin:8px 0}}.explore-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:14px 0}}.explore-card{{display:block;padding:17px;background:#fff;border:1px solid var(--line);border-radius:14px;color:var(--text);text-decoration:none}}.explore-card:hover{{border-color:var(--accent);background:var(--accent-soft)}}.explore-card strong{{display:block;color:#125840;margin-bottom:5px}}.explore-card span{{display:block;color:var(--muted);font-size:.9rem}}.section-note{{font-size:.9rem;color:var(--muted)}}.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}
@media(max-width:800px){{.site-hero{{grid-template-columns:1fr}}.hero-aside{{max-width:none}}}}
@media(max-width:520px){{main{{padding:14px 12px 36px}}.metric,.panel{{padding:14px;border-radius:12px}}.grid{{grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:9px}}.metric strong{{font-size:1.45rem}}.quick-nav{{gap:6px}}.quick-nav a{{padding:7px 10px;font-size:.82rem}}table{{font-size:.84rem}}th,td{{padding:8px 7px}}.live-clock{{font-size:clamp(1.8rem,10vw,2.6rem)}}.site-hero{{padding:22px 18px;border-radius:18px;gap:18px}}.site-topline{{margin-bottom:20px}}.hero-actions a{{width:100%;text-align:center}}.public-indicator-grid{{grid-template-columns:1fr}}.indicator-value{{font-size:1.9rem}}}}</style></head><body><main>
<header class="site-hero" id="home">
<div class="hero-main">
<div class="site-topline"><span class="brand-mark" aria-hidden="true">P</span><span class="brand-name">PADUKA SAMBAS<span class="brand-subtitle">Pusat Data dan Informasi Publik</span></span></div>
<div class="hero-eyebrow">Portal informasi publik Kabupaten Sambas</div>
<h1>Kenali kondisi Kabupaten Sambas melalui data.</h1>
<p class="hero-copy">PADUKA merangkum informasi daerah, ekonomi Indonesia, pasar, komoditas, dan perkembangan global dalam satu tempat. Setiap angka dilengkapi periode dan jejak sumber agar mudah dibaca serta ditelusuri.</p>
<div class="hero-actions"><a href="#data-sambas">Lihat data Sambas</a><a class="secondary" href="#jelajahi">Jelajahi informasi</a><a class="secondary" href="https://padukasambas.blogspot.com" target="_blank" rel="noopener noreferrer" style="background:#e11d48;color:#fff;border-color:#e11d48;font-weight:700;">📰 Portal Berita Resmi</a></div>
<div class="hero-meta"><span class="sr-only">PUBLIC DASHBOARD</span><span>Laporan diperbarui: <strong>{_cell(generated_at or "Belum tersedia")}</strong></span><span>Zona waktu: Indonesia Barat (WIB)</span></div>
</div>
<aside class="hero-aside"><div class="hero-aside-label">Tentang PADUKA</div><strong>Data lebih jelas. Informasi lebih mudah dijangkau.</strong><p>Ringkasan untuk masyarakat, pelaku usaha, peneliti, dan pengambil kebijakan. Gunakan tautan sumber untuk memeriksa konteks setiap data.</p><span class="legacy-title">MD V14 · Trend Intelligence Dashboard</span></aside>
</header>
<nav class="quick-nav" aria-label="Navigasi utama"><a href="#home">Beranda</a><a href="https://padukasambas.blogspot.com" target="_blank" rel="noopener noreferrer" style="background:#fff1f2;border-color:#fda4af;color:#e11d48;font-weight:700;">📰 Blog Berita</a><a href="#data-sambas">Data Sambas</a><a href="#regional">Data Indonesia</a><a href="#economy">Ekonomi &amp; pasar</a><a href="#global-overview">Tren global</a><a href="#live-status">Pembaruan &amp; sumber</a><a href="#technical-detail">Catatan teknis</a></nav>
<section class="public-section" id="public-overview"><h2>Ringkasan untuk publik</h2>
<p class="public-section-lead">Lihat cakupan data daerah yang tersedia, periode terakhir, sumber yang dicantumkan, dan data yang masih menunggu pemeriksaan.</p>
<div class="grid">{public_summary_cards}</div></section>
<section class="public-section" id="data-sambas"><h2>Sorotan data Kabupaten Sambas</h2>
<p class="public-section-lead">Angka di bawah menampilkan observasi terbaru yang tersedia untuk Kabupaten Sambas. Perhatikan tahun/periode dan satuan sebelum membandingkan atau mengutipnya.</p>
<div class="public-indicator-grid">{public_indicator_cards_html}</div>
<p class="section-note">Sumber dicantumkan pada setiap kartu. Data yang belum selesai diperiksa tidak ditampilkan sebagai indikator utama.</p></section>
<section class="panel public-section" id="jelajahi"><h2>Jelajahi informasi</h2>
<p class="public-section-lead">Pilih topik untuk melihat ringkasan dan rincian yang tersedia.</p>
<div class="explore-grid">
<a class="explore-card" href="#regional"><strong>Data daerah Indonesia</strong><span>Indikator kabupaten/provinsi dan gambaran ekonomi regional.</span></a>
<a class="explore-card" href="#economy"><strong>Ekonomi Indonesia</strong><span>Indikator makroekonomi dan konteks sektor ekonomi.</span></a>
<a class="explore-card" href="#economy"><strong>Kurs, pasar, dan komoditas</strong><span>Referensi kurs serta harga acuan komoditas global.</span></a>
<a class="explore-card" href="#global-overview"><strong>Tren dan isu global</strong><span>Perkembangan lintas negara, topik, dan sumber berita.</span></a>
<a class="explore-card" href="#metodologi"><strong>Sumber dan cara membaca</strong><span>Asal informasi, keterbatasan, dan penjelasan indikator.</span></a>
</div></section>
<p class="accordion-intro">Pilih topik di bawah untuk membuka rincian. Bagian yang belum dibuka tetap ringkas agar informasi utama mudah ditemukan.</p>
<details class="content-accordion" id="pembaruan-section">
<summary><span class="accordion-symbol" aria-hidden="true">↻</span><span class="accordion-copy"><strong>Pembaruan &amp; kualitas data</strong><small>Waktu laporan, status sumber, cakupan bahasa, dan pengenalan entitas</small></span><span class="accordion-toggle" aria-hidden="true"></span></summary>
<div class="accordion-body">
<section class="panel" id="live-status">
<h2>Pembaruan data dan status sumber</h2>
<p class="public-section-lead">Jam WIB berjalan langsung. Angka dan ringkasan pada halaman ini mengikuti waktu pembuatan laporan terakhir, bukan data streaming.</p>
<div class="columns">
<article><div class="muted">JAM INDONESIA BARAT (WIB)</div><div id="wib-clock" class="live-clock" aria-live="off">Memuat waktu…</div><div id="wib-date" class="muted"></div></article>
<article><div class="muted">WAKTU PEMBUATAN LAPORAN <span class="sr-only">PEMBARUAN DATA TERAKHIR</span></div><strong>{_cell(generated_at or "Belum tersedia")}</strong><div class="muted">Data analisis berubah saat laporan berikutnya diterbitkan</div></article>
</div>
<div class="columns">
<article><h2>Status siklus pengumpulan</h2><p><strong>{_cell(monitoring.get("cycle_status", "belum dilaporkan"))}</strong></p><p class="muted">Umpan berhasil: {_cell(monitoring.get("feeds_succeeded", 0))}/{_cell(monitoring.get("feeds_attempted", 0))}. Siklus terjadwal, bukan streaming kontinu.</p></article>
<article><h2>Status sumber data</h2><ul>{source_status_html}</ul></article>
</div>
<p class="notice">Informasi publik: dashboard ini dapat diakses siapa saja melalui internet. Jangan masukkan data pribadi, kredensial, atau laporan internal ke sumber yang dipublikasikan. Jam WIB berjalan langsung; isi analisis merupakan snapshot dari siklus pengumpulan terakhir dan berubah setelah dashboard dibangun ulang.</p>
</section>
<section class="grid" id="overview">{cards}</section>
<section class="panel" id="monitoring"><h2>Pemantauan langsung · siklus pengumpulan terakhir</h2><div class="grid">{monitor_cards}</div><p class="muted">Stempel waktu siklus: {_cell(monitoring.get("generated_at", "Tidak tersedia"))}. Status kelancaran umpan menunjukkan keberhasilan pengumpulan teknis, bukan verifikasi isi konten. Eksekusi terjadwal hanya aktif saat alur kerja repositori berjalan.</p></section>
<section class="panel"><h2>Cakupan sumber multibahasa</h2><div class="grid">{language_cards}</div><div class="table-wrap"><table><thead><tr><th>Bahasa terdata</th><th class="num">Jumlah rekaman</th></tr></thead><tbody>{language_rows}</tbody></table></div><p class="muted">Label bahasa merupakan metadata yang tersedia dari sumber. Pencocok riset dwibahasa adalah alat bantu leksikal terbatas, bukan penerjemahan atau deteksi bahasa otomatis.</p></section>
<section class="panel"><h2>Graf pengetahuan lintas bahasa</h2><div class="grid">{graph_cards}</div>
<h3>Entitas dan istilah yang terdeteksi</h3><div class="table-wrap"><table><thead><tr><th>Entitas</th><th>Jenis</th><th>Dasar pengenalan</th></tr></thead><tbody>{graph_node_rows}</tbody></table></div>
<h3>Hubungan untuk ditinjau</h3><div class="table-wrap"><table><thead><tr><th>Jenis hubungan</th><th>Simpul pertama</th><th>Simpul kedua</th><th>ID rekaman pendukung</th></tr></thead><tbody>{graph_edge_rows}</tbody></table></div>
<p class="muted">Pengenalan entitas dilakukan otomatis melalui pencocokan nama dan metadata. Nama yang terdeteksi hanya menunjukkan bahwa istilah tersebut muncul pada sumber; hal ini bukan verifikasi kebenaran isi berita. Hubungan dalam grafik juga tidak membuktikan sebab-akibat, pengaruh, atau independensi sumber. Setiap temuan tetap memerlukan pemeriksaan manusia.</p></section>

</div>
</details>

<details class="content-accordion" id="analisis-section">
<summary><span class="accordion-symbol" aria-hidden="true">▤</span><span class="accordion-copy"><strong>Analisis &amp; tinjauan</strong><small>Ringkasan analisis, antrean pemeriksaan, dan peringatan</small></span><span class="accordion-toggle" aria-hidden="true"></span></summary>
<div class="accordion-body">
<section class="panel"><h2>Laporan strategis analis</h2><div class="grid">{analyst_cards}</div>
<p>{_cell(analyst.get("executive_summary") or "Laporan analis tidak tersedia.")}</p>
<h3>Temuan utama untuk ditinjau</h3><div class="table-wrap"><table><thead><tr><th>Prioritas</th><th>Temuan</th><th>Sumber</th><th>Negara</th><th>ID Sinyal</th></tr></thead><tbody>{''.join(analyst_findings)}</tbody></table></div>
<h3>Ketidakpastian dan celah bukti</h3><ul>{analyst_uncertainties}</ul>
<h3>Rekomendasi tindakan tinjauan manusia</h3><ul>{analyst_actions}</ul>
<p class="muted">Sintesis deterministik dari penilaian yang disediakan, bukan AI generatif atau verifikasi fakta independen. Persetujuan manusia tetap diperlukan.</p></section>
<section class="panel" id="signals"><h2>Antrean tinjauan keputusan strategis</h2><div class="table-wrap"><table><thead><tr><th>Prioritas</th><th>Sinyal</th><th class="num">Skor</th><th>Peringatan</th><th>Sumber</th><th>Tautan artikel</th></tr></thead><tbody>{''.join(review_rows)}</tbody></table></div><p class="muted">Prioritas adalah petunjuk urutan peninjauan manusia, bukan tingkat keparahan atau probabilitas peristiwa.</p></section>
<section class="columns">
<article class="panel"><h2>Distribusi tingkat peringatan</h2><ul>{warnings}</ul></article>
<article class="panel"><h2>Status metadata sumber</h2><ul>{source_summary}</ul></article>
</section>
</div>
</details>

<details class="content-accordion" id="data-section">
<summary><span class="accordion-symbol" aria-hidden="true">◉</span><span class="accordion-copy"><strong>Data wilayah, ekonomi &amp; pasar</strong><small>Peta wilayah, indikator Indonesia, kurs, komoditas, dan pasar</small></span><span class="accordion-toggle" aria-hidden="true"></span></summary>
<div class="accordion-body">
{country_explorer_html}
<section id="economy">{economic_intelligence_html}
{world_bank_html}
{public_market_html}
{public_asset_html}
{commodity_html}
{fred_market_html}
{market_analytics_html}</section>
<section id="regional">{indonesia_economic_html}
{regional_intelligence_html}</section>


</div>
</details>

<details class="content-accordion" id="tren-section">
<summary><span class="accordion-symbol" aria-hidden="true">◎</span><span class="accordion-copy"><strong>Tren dan perkembangan global</strong><small>Aktivitas negara, topik, tren meningkat, dan jejak sumber</small></span><span class="accordion-toggle" aria-hidden="true"></span></summary>
<div class="accordion-body">
<section class="panel" id="global-overview"><h2>Gambaran tren global <span class="sr-only">Global intelligence overview</span></h2><div class="grid">{global_cards}</div></section>
<section class="columns">
<article class="panel"><h2>Aktivitas negara</h2><div class="table-wrap"><table><thead><tr><th>Negara</th><th class="num">Sinyal</th><th class="num">Skor rata-rata</th><th>Profil skor</th></tr></thead><tbody>{country_rows}</tbody></table></div></article>
<article class="panel"><h2>Aktivitas topik</h2><div class="table-wrap"><table><thead><tr><th>Topik</th><th class="num">Sinyal</th><th class="num">Skor rata-rata</th><th>Profil skor</th></tr></thead><tbody>{topic_rows}</tbody></table></div></article>
</section>
<section class="panel"><h2>Sinyal tren naik</h2><div class="table-wrap"><table><thead><tr><th>Tren</th><th>Negara</th><th>Topik</th><th class="num">Skor</th><th class="num">Momentum</th></tr></thead><tbody>{''.join(rising_rows)}</tbody></table></div></section>
<section class="panel"><h2>Kandidat keterkaitan peristiwa</h2><div class="table-wrap"><table><thead><tr><th>Peristiwa A</th><th>Negara</th><th>Peristiwa B</th><th>Negara</th><th>Dasar hubungan</th></tr></thead><tbody>{''.join(relation_rows)}</tbody></table></div><p class="muted">Kandidat keterkaitan didasarkan pada metadata atau kata kunci bersama, bukan bukti hubungan sebab-akibat atau konfirmasi independen.</p></section>
<section class="panel" id="metodologi"><h2>Sumber informasi dan jejak data <span class="sr-only">Source intelligence &amp; provenance</span></h2><div class="table-wrap"><table><thead><tr><th>Tren</th><th>Sumber</th><th>Domain</th><th>Status metadata</th><th class="num">Pemeriksaan</th><th>Status keandalan <span class="sr-only">Reliability verdict</span></th></tr></thead><tbody>{''.join(source_rows)}</tbody></table></div></section>
<section class="panel"><h2>Distribusi kategori</h2><div class="table-wrap"><table><thead><tr><th>Kategori</th><th class="num">Sinyal</th></tr></thead><tbody>{category_rows}</tbody></table></div></section>
<section class="panel"><h2>Analisis lanjutan tren <span class="sr-only">Advanced trend intelligence</span></h2><div class="table-wrap"><table><thead><tr><th>Tren</th><th>Kategori</th><th class="num">Skor</th><th>Peringatan</th><th>Riwayat</th><th class="num">Momentum</th><th class="num">Akselerasi</th><th>Tinjauan anomali</th><th>Tingkat keyakinan</th><th>Sumber</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>

</div>
</details>

<details class="content-accordion" id="teknis-section">
<summary><span class="accordion-symbol" aria-hidden="true">⚙</span><span class="accordion-copy"><strong>Catatan teknis &amp; sistem</strong><small>Metodologi, kontrol operasional, dan batasan analisis</small></span><span class="accordion-toggle" aria-hidden="true"></span></summary>
<div class="accordion-body">
<section class="panel" id="technical-detail"><h2>Informasi teknis dan analisis lanjutan</h2><p class="public-section-lead">Bagian ini memuat status operasional, antrean peninjauan, dan ringkasan analitis. Istilah prioritas dan peringatan merupakan alat bantu peninjauan, bukan penilaian risiko otomatis.</p></section>
<section class="panel" id="control-center"><h2>PADUKA Control Center</h2><p class="muted">Pusat kontrol laporan dan status build berdasarkan data report saat ini. Notifikasi di bawah adalah aturan pemantauan; belum terhubung ke push alert.</p><div class="control-grid"><article class="control-card"><h3>Build 1.9 · Integrasi FRED &amp; BPS</h3><span class="control-status">Validasi berjalan</span><p>Target bukti: observasi FRED, tabel BPS Sambas live, metadata/period/unit, dan tes lulus.</p></article><article class="control-card"><h3>Monitoring sumber</h3><span class="control-status">{_cell(monitoring.get("cycle_status", "belum dilaporkan"))}</span><p>Feed sukses: {_cell(monitoring.get("feeds_succeeded", 0))}/{_cell(monitoring.get("feeds_attempted", 0))}. Status berdasarkan laporan yang dibuat.</p></article><article class="control-card"><h3>Riwayat &amp; tindakan</h3><span class="control-status">Laporan lokal</span><p>Gunakan timestamp laporan, status sumber, dan hasil tes workflow untuk menilai perubahan. Dashboard tidak mengubah repository.</p></article></div><h3>Daftar pemberitahuan / aturan</h3><div class="notification-list"><div class="notification-item"><strong>Gangguan sumber data</strong><span>Periksa jika FRED/BPS gagal, observasi kosong, atau status stale pada laporan berikutnya.</span></div><div class="notification-item"><strong>Build siap ditinjau</strong><span>Periksa jika semua bukti integrasi dan tes Build 1.9 sudah valid.</span></div><div class="notification-item"><strong>Perubahan repository</strong><span>Gunakan GitHub commit dan workflow sebagai bukti perubahan, bukan indikator visual dashboard semata.</span></div></div></section><section class="panel" id="command-center"><h2>Pusat Komando Intelijen Strategis Global · Build 3.0 <span class="sr-only">Global Strategic Intelligence Command Center</span></h2>
<div class="grid">{command_metrics}</div>
<p><strong>{_cell(command_posture.get("status", "belum dinilai"))}</strong> — {_cell(command_posture.get("note", "Penilaian pusat komando tidak tersedia."))}</p>
<p class="muted">Pengumpulan: {_cell(command_cycle.get("status", "belum dikonfigurasi"))}; waktu dibuat: {_cell(command.get("generated_at", "tidak tersedia"))}. Ini adalah tampilan laporan terkonsolidasi, bukan pemantauan terus-menerus atau pemeringkatan risiko otonom.</p>
<h3>Antrean tinjauan prioritas</h3><div class="table-wrap"><table><thead><tr><th>Prioritas</th><th>Sinyal</th><th>Negara</th><th>Sumber</th><th>ID Sinyal</th></tr></thead><tbody>{command_queue_rows}</tbody></table></div>
<h3>Gerbang keputusan</h3><ul>{decision_gate_rows}</ul></section>
<p class="notice">Pemeriksaan sumber hanya mendeskripsikan kolom metadata dan rekam jejak yang disediakan. Pemeriksaan ini tidak menilai reputasi sumber atau memverifikasi klaim kebenaran berita. Keandalan dan independensi redaksional tidak dinilai secara otomatis. Momentum dan akselerasi bersifat deskriptif; indikator anomali memerlukan tinjauan manusia. Tidak ada indikator yang merupakan probabilitas atau ramalan pasti.</p>

</div>
</details>
<footer>
<div style="margin-bottom:14px;display:flex;flex-wrap:wrap;gap:12px;align-items:center;">
  <strong>Jejaring Media Resmi Paduka Sambas:</strong>
  <a href="https://padukasambas.blogspot.com" target="_blank" rel="noopener noreferrer" style="font-weight:700;color:#e11d48;">🌐 Blog Resmi</a> ·
  <a href="https://www.facebook.com/paduka.sambas" target="_blank" rel="noopener noreferrer">Facebook</a> ·
  <a href="https://www.instagram.com/paduka_sambas" target="_blank" rel="noopener noreferrer">Instagram</a> ·
  <a href="https://www.youtube.com/@PadukaSambas" target="_blank" rel="noopener noreferrer">YouTube</a>
</div>
PADUKA Sambas menyajikan ringkasan informasi berbasis sumber yang tercantum. Data diperbarui ketika laporan baru diterbitkan; periksa periode, satuan, metode, dan sumber asli sebelum mengutip atau mengambil keputusan. <span class="sr-only">Dipublikasikan sebagai dashboard statis MD V14 Trend Intelligence Dashboard.</span>
</footer>
</main><script>
(function () {{
  const clock = document.getElementById("wib-clock");
  const date = document.getElementById("wib-date");
  const timeOptions = {{ timeZone: "Asia/Jakarta", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }};
  const dateOptions = {{ timeZone: "Asia/Jakarta", weekday: "long", year: "numeric", month: "long", day: "numeric" }};
  function updateWibClock() {{
    const now = new Date();
    clock.textContent = new Intl.DateTimeFormat("id-ID", timeOptions).format(now) + " WIB";
    date.textContent = new Intl.DateTimeFormat("id-ID", dateOptions).format(now);
  }}
  updateWibClock();
  window.setInterval(updateWibClock, 1000);
  document.querySelectorAll('.quick-nav a[href^="#"], .explore-card[href^="#"], .hero-actions a[href^="#"]').forEach((link) => {{
    link.addEventListener("click", () => {{
      const targetId = link.getAttribute("href").slice(1);
      const target = document.getElementById(targetId);
      const accordion = target ? target.closest("details.content-accordion") : null;
      if (accordion) accordion.open = true;
    }});
  }});
  if (window.location.hash) {{
    const initialTarget = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    const initialAccordion = initialTarget ? initialTarget.closest("details.content-accordion") : null;
    if (initialAccordion) initialAccordion.open = true;
  }}
  const reportUpdated = document.querySelector(".hero-meta strong");
  if (reportUpdated) {{
    const parsed = Date.parse(reportUpdated.textContent.trim());
    if (Number.isFinite(parsed)) {{
      reportUpdated.textContent = new Intl.DateTimeFormat("id-ID", {{ dateStyle: "medium", timeStyle: "medium", timeZone: "Asia/Jakarta" }}).format(new Date(parsed)) + " WIB";
    }}
  }}
}})();
</script></body></html>
"""
