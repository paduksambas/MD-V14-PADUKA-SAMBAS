"""Generate a self-contained, offline HTML analytics dashboard."""
from __future__ import annotations

from collections import Counter
from html import escape
from math import isfinite
from typing import Any
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
            f"<td>{_cell(assessment.get('source_domain') or 'unknown')}</td>"
            f"<td>{_cell(assessment.get('status', 'not assessed'))}</td>"
            f"<td class='num'>{_cell(str(assessment.get('metadata_checks_passed', '—')) + '/' + str(assessment.get('metadata_checks_total', '—')))}</td>"
            "<td>Not assessed</td>"
            "</tr>"
        )
    if not source_rows:
        source_rows.append("<tr><td colspan='6'>No source records to assess.</td></tr>")

    rows = []
    for item in sorted(signals, key=lambda x: _score(x.get("score")), reverse=True):
        hist = item.get("history") or {}
        warning = item.get("warning") or {}
        advanced = item.get("advanced_intelligence") or {}
        anomaly = advanced.get("anomaly") or {}
        anomaly_label = "Unusual change — review" if anomaly.get("detected") else anomaly.get("status", "not assessed")
        rows.append(
            "<tr>"
            f"<td>{_cell(item.get('title'))}</td>"
            f"<td>{_cell(item.get('category'))}</td>"
            f"<td class='num'>{_cell(item.get('score', 0))}</td>"
            f"<td>{_cell(warning.get('level', 'unknown'))}</td>"
            f"<td>{_cell(hist.get('direction', 'no history'))}</td>"
            f"<td class='num'>{_cell(advanced.get('momentum', '—'))}</td>"
            f"<td class='num'>{_cell(advanced.get('acceleration', '—'))}</td>"
            f"<td>{_cell(anomaly_label)}</td>"
            f"<td>{_cell(advanced.get('confidence', 'not assessed'))}</td>"
            f"<td>{_cell(item.get('source') or 'Source review needed')}</td>"
            "</tr>"
        )
    if not rows:
        rows.append("<tr><td colspan='10'>No trend signals in this report.</td></tr>")

    category_rows = "".join(
        f"<tr><td>{_cell(name)}</td><td class='num'>{count}</td></tr>"
        for name, count in sorted(categories.items(), key=lambda pair: (-pair[1], pair[0].casefold()))
    ) or "<tr><td colspan='2'>No category data.</td></tr>"

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
                f"<td><div class='bar-track' role='img' aria-label='Average score {average:.1f} out of 100'>"
                f"<span class='bar-fill' style='width:{width:.1f}%'></span></div></td></tr>"
            )
        return "".join(rendered) or "<tr><td colspan='4'>No global intelligence data available.</td></tr>"

    country_rows = group_rows(intelligence.get("country_analysis", []))
    topic_rows = group_rows(intelligence.get("topic_analysis", []))

    rising_rows = []
    for item in intelligence.get("rising_signals", []):
        rising_rows.append(
            "<tr>"
            f"<td>{_cell(item.get('title'))}</td>"
            f"<td>{_cell(item.get('country', 'unknown'))}</td>"
            f"<td>{_cell(', '.join(item.get('topics', [])))}</td>"
            f"<td class='num'>{_cell(item.get('score'))}</td>"
            f"<td class='num'>{_cell(item.get('momentum'))}</td>"
            "</tr>"
        )
    if not rising_rows:
        rising_rows.append("<tr><td colspan='5'>No rising signals with sufficient history.</td></tr>")

    relation_rows = []
    for item in intelligence.get("related_events", []):
        basis = ", ".join(item.get("relationship_basis", []))
        relation_rows.append(
            "<tr>"
            f"<td>{_cell(item.get('left_title'))}</td>"
            f"<td>{_cell(item.get('left_country', 'unknown'))}</td>"
            f"<td>{_cell(item.get('right_title'))}</td>"
            f"<td>{_cell(item.get('right_country', 'unknown'))}</td>"
            f"<td>{_cell(basis)}</td>"
            "</tr>"
        )
    if not relation_rows:
        relation_rows.append("<tr><td colspan='5'>No related-event candidates identified.</td></tr>")

    language_data = report.get("language_intelligence") or {}
    language_counts = language_data.get("language_counts", {})
    language_rows = "".join(
        f"<tr><td>{_cell(language)}</td><td class='num'>{_cell(count)}</td></tr>"
        for language, count in sorted(language_counts.items())
    ) or "<tr><td colspan='2'>No declared language metadata.</td></tr>"
    language_cards = "".join([
        metric("Declared language", language_data.get("records_with_declared_language", 0), "Explicit metadata only"),
        metric("Unknown language", language_data.get("records_with_unknown_language", 0), "Not inferred"),
        metric("Languages represented", len(language_counts), "Declared labels"),
    ])
    graph = report.get("knowledge_graph") or {}
    graph_nodes = graph.get("nodes", [])
    graph_edges = graph.get("edges", [])
    graph_node_rows = "".join(
        "<tr><td>" + _cell(item.get("label")) + "</td><td>" + _cell(item.get("type")) + "</td><td>" + _cell(", ".join(item.get("evidence_sources", []))) + "</td></tr>"
        for item in graph_nodes
    ) or "<tr><td colspan=\"3\">No recognized entities or graph nodes.</td></tr>"
    graph_edge_rows = "".join(
        "<tr><td>" + _cell(item.get("relation")) + "</td><td>" + _cell(item.get("source")) + "</td><td>" + _cell(item.get("target")) + "</td><td>" + _cell(", ".join(item.get("supporting_record_ids", []))) + "</td></tr>"
        for item in graph_edges
    ) or "<tr><td colspan=\"4\">No graph relationships identified.</td></tr>"
    graph_cards = "".join([
        metric("Graph nodes", graph.get("nodes_total", 0), "Entity, event, topic and country nodes"),
        metric("Graph edges", graph.get("edges_total", 0), "Discovery relationships"),
        metric("Records with entities", graph.get("records_with_recognized_entities", 0), "Curated aliases or explicit metadata"),
    ])
    monitoring = report.get("monitoring") or {}
    generated_at = monitoring.get("generated_at") or (report.get("command_center") or {}).get("generated_at") or ""
    source_status = []
    for key, label in (
        ("market_data", "Kurs valas"),
        ("commodity_data", "Komoditas"),
        ("economic_data", "World Bank"),
        ("regional_intelligence", "Data regional BPS"),
        ("bps_regional_tables", "Konektor tabel BPS"),
        ("bps_public_export", "Impor ekspor BPS"),
        ("fred_market_data", "FRED"),
    ):
        payload = report.get(key)
        if isinstance(payload, dict):
            source_status.append((label, str(payload.get("status") or "not_reported")))
    source_status_html = "".join(
        f"<li><span>{_cell(label)}</span><b class='status-value'>{_cell(status.replace('_', ' '))}</b></li>"
        for label, status in source_status
    ) or "<li>No source status supplied in this report.</li>"
    decision = report.get("strategic_decision") or {}
    review_rows = []
    for item in decision.get("review_queue", []):
        review_rows.append("<tr>" + f"<td>{_cell(item.get('priority_band'))}</td><td>{_cell(item.get('title'))}</td><td class='num'>{_cell(item.get('priority_score'))}</td><td>{_cell(item.get('warning_level'))}</td><td>{_cell(item.get('source'))}</td><td>{_cell(item.get('url') or 'Unavailable')}</td>" + "</tr>")
    if not review_rows:
        review_rows.append("<tr><td colspan='6'>No records in the strategic review queue.</td></tr>")
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
        analyst_findings.append("<tr><td colspan=\"5\">No analyst findings available.</td></tr>")
    analyst_actions = "".join(
        "<li><span>" + _cell(item.get("priority")) + " — " + _cell(item.get("action")) + "</span></li>"
        for item in analyst.get("recommended_human_actions", [])
    ) or "<li>No review actions available.</li>"
    analyst_uncertainties = "".join("<li>" + _cell(item) + "</li>" for item in analyst.get("uncertainties_and_gaps", []))
    analyst_cards = "".join([
        metric("Analyst findings", len(analyst.get("key_findings", [])), "Traceable priority candidates"),
        metric("Evidence gaps", (analyst.get("metadata_coverage") or {}).get("records_with_incomplete_evidence_metadata", 0), "Metadata only"),
        metric("Uncertainties", len(analyst.get("uncertainties_and_gaps", [])), "Explicit caveats"),
    ])
    command = report.get("command_center") or {}
    command_cycle = command.get("collection_cycle") or {}
    command_posture = command.get("strategic_posture") or {}
    command_coverage = command.get("coverage") or {}
    command_metrics = "".join([
        metric("Operational state", command.get("operational_state", "not assessed"), "Configured feed cycle only"),
        metric("Strategic posture", command_posture.get("status", "not assessed"), "Heuristic human-review cue"),
        metric("Signals analyzed", command_coverage.get("signals_analyzed", len(signals)), "Current report"),
        metric("Feeds succeeded", str(command_cycle.get("feeds_succeeded", 0)) + "/" + str(command_cycle.get("feeds_attempted", 0)), "Latest collection cycle"),
        metric("High review priority", command_posture.get("high_review_priority", 0), "Not threat severity"),
        metric("Evidence gaps", command_posture.get("evidence_review_required", reviewed), "Metadata completeness only"),
    ])
    command_queue_rows = "".join(
        "<tr><td>" + _cell(item.get("priority_band")) + "</td><td>" + _cell(item.get("title")) +
        "</td><td>" + _cell(item.get("country")) + "</td><td>" + _cell(item.get("source")) +
        "</td><td>" + _cell(item.get("signal_id")) + "</td></tr>"
        for item in command.get("priority_review_queue", [])
    ) or "<tr><td colspan=\"5\">No priority review items.</td></tr>"
    decision_gate_rows = "".join("<li>" + _cell(item) + "</li>" for item in command.get("decision_gates", []))
    if not decision_gate_rows:
        decision_gate_rows = "<li>Human review required before action.</li>"
    monitor_cards = "".join([
        metric("Monitoring cycle", monitoring.get("cycle_status", "not configured"), "Latest collection cycle"),
        metric("Feeds healthy", f"{monitoring.get('feeds_succeeded', 0)}/{monitoring.get('feeds_attempted', 0)}", "RSS/Atom endpoints"),
        metric("Items collected", monitoring.get("signals_collected", len(signals)), "Records in this cycle"),
        metric("Published in 24h", monitoring.get("signals_published_within_window", 0), "Parseable timestamps only"),
        metric("Unknown publish time", monitoring.get("signals_with_unknown_published_at", 0), "Missing or invalid timestamp"),
    ])

    global_cards = "".join([
        metric("Signals analyzed", intelligence.get("signals_analyzed", 0), "Global intelligence input"),
        metric("Countries represented", len(intelligence.get("country_analysis", [])), "Explicit metadata only"),
        metric("Topics represented", len(intelligence.get("topic_analysis", [])), "Supplied topics/categories"),
        metric("Rising signals", len(intelligence.get("rising_signals", [])), "Positive historical momentum"),
        metric("Related-event candidates", len(intelligence.get("related_events", [])), "Not causal findings"),
    ])
    title = "MD V14 — Trend Intelligence Dashboard"
    date_label = brief.get("date", "Date unavailable")
    cards = "".join([
        metric("Signals", len(signals), "In this report"),
        metric("Average score", f"{avg_score:.1f}/100", "Supplied heuristic scores"),
        metric("Needs source review", reviewed, "Metadata completeness only"),
        metric("With history", len(history), "Persisted observations"),
        metric("Source records assessed", sum(source_status_counts.values()), "Metadata checklist only"),
    ])
    warnings = "".join(
        f"<li><span>{_cell(level.title())}</span><b>{_cell(count)}</b></li>"
        for level, count in (("critical", warning_counts.get("critical", 0)),
                             ("elevated", warning_counts.get("elevated", 0)),
                             ("watch", warning_counts.get("watch", 0)),
                             ("normal", warning_counts.get("normal", 0)))
    )
    source_summary = "".join(
        f"<li><span>{_cell(status.replace('_', ' '))}</span><b>{_cell(count)}</b></li>"
        for status, count in sorted(source_status_counts.items())
    ) or "<li>No source assessments</li>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_cell(title)}</title>
<meta name="description" content="MD V14 Global Strategic Intelligence Command Center">
<style>
:root{{color-scheme:light dark;--bg:#101827;--panel:#182438;--line:#314158;--muted:#a9b8cc;--text:#f2f6fc;--accent:#83b7ff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,sans-serif}}
main{{max-width:1180px;margin:auto;padding:28px 20px 56px}}header{{margin-bottom:24px}}h1{{font-size:clamp(1.6rem,4vw,2.35rem);margin:0 0 6px}}h2{{font-size:1.1rem;margin:0 0 14px}}.muted,small{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:12px;margin:20px 0}}
.metric,.panel{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:17px}}.metric strong{{display:block;font-size:1.9rem;margin:5px 0}}.metric small{{display:block}}
.columns{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0}}@media(max-width:700px){{.columns{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{text-align:left;padding:10px 8px;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:var(--muted);font-weight:600}}.num{{font-variant-numeric:tabular-nums;text-align:right}}.table-wrap{{overflow-x:auto}}ul{{list-style:none;padding:0;margin:0}}li{{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--line)}}.bar-track{{height:9px;min-width:100px;background:var(--line);border-radius:99px;overflow:hidden}}.bar-fill{{display:block;height:100%;background:var(--accent);border-radius:99px}}.map-wrap{{background:#0b1422;border:1px solid var(--line);border-radius:12px;overflow:hidden}}.world-plot{{display:block;width:100%;height:auto;max-height:480px}}.map-bg{{fill:#0b1422}}.map-gridline{{stroke:#34445b;stroke-width:1;stroke-dasharray:3 5}}.country-marker{{cursor:pointer;outline:none}}.country-marker circle,.legend-dot{{stroke:#f2f6fc;stroke-width:1.5;fill:#83b7ff}}.country-marker.priority-high circle,.legend-dot.priority-high{{fill:#f07878}}.country-marker.priority-medium circle,.legend-dot.priority-medium{{fill:#e7b75d}}.country-marker.priority-routine circle,.legend-dot.priority-routine{{fill:#83b7ff}}.country-marker:focus circle,.country-marker:hover circle{{stroke:#fff;stroke-width:3}}.map-legend,.country-picker{{display:flex;flex-wrap:wrap;gap:9px;margin:12px 0}}.map-legend span{{display:flex;align-items:center;gap:6px;color:var(--muted);font-size:.85rem}}.legend-dot{{display:inline-block;width:11px;height:11px;border-radius:50%}}.country-select{{background:var(--panel);border:1px solid var(--line);border-radius:8px;color:var(--text);padding:7px 10px;cursor:pointer}}.country-select[aria-pressed=true]{{border-color:var(--accent);outline:1px solid var(--accent)}}.country-detail{{padding:14px;border:1px solid var(--line);border-radius:10px}}.country-detail[hidden]{{display:none}}.notice{{border-left:3px solid var(--accent);padding:10px 14px;background:var(--panel);border-radius:5px;color:var(--muted);margin-top:18px}}footer{{margin-top:22px;color:var(--muted);font-size:.85rem}}.control-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:16px 0}}.control-card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px}}.control-card h3{{margin:0 0 8px;font-size:1rem}}.control-card p{{margin:0;color:var(--muted)}}.control-status{{display:inline-block;padding:4px 9px;border:1px solid var(--line);border-radius:999px;font-size:.8rem;margin-bottom:8px}}.notification-list{{display:grid;gap:8px}}.notification-item{{padding:10px 12px;border-left:3px solid var(--accent);background:var(--panel);border-radius:5px}}.notification-item strong{{display:block}}.notification-item span{{color:var(--muted);font-size:.9rem}}.quick-nav{{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 20px}}.quick-nav a{{display:inline-block;border:1px solid var(--line);background:var(--panel);border-radius:999px;padding:7px 12px;color:var(--text);text-decoration:none;font-size:.86rem}}.quick-nav a:hover,.quick-nav a:focus{{border-color:var(--accent);outline:1px solid var(--accent)}}.live-clock{{font-size:clamp(2rem,6vw,3.2rem);font-weight:750;font-variant-numeric:tabular-nums;letter-spacing:.03em}}.status-value{{text-transform:capitalize;color:var(--accent)}}
</style></head><body><main>
<header><div class="muted">PADUKA SAMBAS · PRIVATE LOCAL DASHBOARD · CONTROL CENTER · LOCAL REPORT</div>
<h1>{_cell(title)}</h1><div class="muted">Report date: {_cell(date_label)}</div></header>
<nav class="quick-nav" aria-label="Navigasi dashboard"><a href="#control-center">Control Center</a><a href="#live-status">Status &amp; WIB</a><a href="#command-center">Command Center</a><a href="#overview">Ringkasan</a><a href="#monitoring">Monitoring</a><a href="#signals">Tren</a><a href="#economy">Ekonomi &amp; pasar</a><a href="#regional">Indonesia &amp; regional</a></nav>
<section class="panel" id="control-center"><h2>PADUKA Control Center</h2><p class="muted">Pusat kontrol laporan dan status build berdasarkan data report saat ini. Notifikasi di bawah adalah aturan pemantauan; belum terhubung ke push alert.</p><div class="control-grid"><article class="control-card"><h3>Build 1.9 · Integrasi FRED &amp; BPS</h3><span class="control-status">Validasi berjalan</span><p>Target bukti: observasi FRED, tabel BPS Sambas live, metadata/period/unit, dan tes lulus.</p></article><article class="control-card"><h3>Monitoring sumber</h3><span class="control-status">{_cell(monitoring.get("cycle_status", "not reported"))}</span><p>Feed sukses: {_cell(monitoring.get("feeds_succeeded", 0))}/{_cell(monitoring.get("feeds_attempted", 0))}. Status berdasarkan laporan yang dibuat.</p></article><article class="control-card"><h3>Riwayat &amp; tindakan</h3><span class="control-status">Laporan lokal</span><p>Gunakan timestamp laporan, status sumber, dan hasil tes workflow untuk menilai perubahan. Dashboard tidak mengubah repository.</p></article></div><h3>Daftar pemberitahuan / aturan</h3><div class="notification-list"><div class="notification-item"><strong>Gangguan sumber data</strong><span>Periksa jika FRED/BPS gagal, observasi kosong, atau status stale pada laporan berikutnya.</span></div><div class="notification-item"><strong>Build siap ditinjau</strong><span>Periksa jika semua bukti integrasi dan tes Build 1.9 sudah valid.</span></div><div class="notification-item"><strong>Perubahan repository</strong><span>Gunakan GitHub commit dan workflow sebagai bukti perubahan, bukan indikator visual dashboard semata.</span></div></div></section><section class="panel" id="live-status">
<div class="columns">
<article><div class="muted">JAM INDONESIA BARAT (WIB)</div><div id="wib-clock" class="live-clock" aria-live="off">Memuat waktu…</div><div id="wib-date" class="muted"></div></article>
<article><div class="muted">PEMBARUAN DATA TERAKHIR</div><strong id="report-updated">{_cell(generated_at or "Belum tersedia")}</strong><div class="muted">Waktu pembuatan laporan dari siklus pengumpulan terakhir</div></article>
</div>
<div class="columns">
<article><h2>Status siklus pengumpulan</h2><p><strong>{_cell(monitoring.get("cycle_status", "not reported"))}</strong></p><p class="muted">Feed berhasil: {_cell(monitoring.get("feeds_succeeded", 0))}/{_cell(monitoring.get("feeds_attempted", 0))}. Siklus terjadwal, bukan streaming kontinu.</p></article>
<article><h2>Status sumber data</h2><ul>{source_status_html}</ul></article>
</div>
<p class="notice">Privasi: halaman ini adalah file HTML mandiri untuk dibuka secara lokal. Jangan unggah atau bagikan file laporan/HTML ke layanan publik jika isinya bersifat pribadi. Jam WIB berjalan langsung; isi laporan berubah hanya setelah laporan baru dihasilkan dan file dashboard diganti.</p>
</section>
<section class="panel" id="command-center"><h2>Global Strategic Intelligence Command Center · Build 3.0</h2>
<div class="grid">{command_metrics}</div>
<p><strong>{_cell(command_posture.get("status", "not assessed"))}</strong> — {_cell(command_posture.get("note", "No command-center assessment available."))}</p>
<p class="muted">Collection: {_cell(command_cycle.get("status", "not configured"))}; generated: {_cell(command.get("generated_at", "not available"))}. This is a consolidated report view, not continuous monitoring or an autonomous risk rating.</p>
<h3>Priority review queue</h3><div class="table-wrap"><table><thead><tr><th>Priority</th><th>Signal</th><th>Country</th><th>Source</th><th>Signal ID</th></tr></thead><tbody>{command_queue_rows}</tbody></table></div>
<h3>Decision gates</h3><ul>{decision_gate_rows}</ul></section>
<section class="grid" id="overview">{cards}</section>
<section class="panel" id="monitoring"><h2>Live monitoring · latest collection cycle</h2><div class="grid">{monitor_cards}</div><p class="muted">Cycle timestamp: {_cell(monitoring.get("generated_at", "Not available"))}. Feed health is collection status, not content verification. Scheduled runs execute only when the repository workflow runs.</p></section>
<section class="panel"><h2>Multilingual source coverage</h2><div class="grid">{language_cards}</div><div class="table-wrap"><table><thead><tr><th>Declared language</th><th class="num">Records</th></tr></thead><tbody>{language_rows}</tbody></table></div><p class="muted">Language labels are supplied metadata. The bilingual research matcher is a limited lexical aid, not translation or automatic language detection.</p></section>
<section class="panel"><h2>Cross-language knowledge graph</h2><div class="grid">{graph_cards}</div>
<h3>Recognized nodes</h3><div class="table-wrap"><table><thead><tr><th>Node</th><th>Type</th><th>Evidence basis</th></tr></thead><tbody>{graph_node_rows}</tbody></table></div>
<h3>Relationships for analyst review</h3><div class="table-wrap"><table><thead><tr><th>Relationship</th><th>Source node</th><th>Target node</th><th>Supporting records</th></tr></thead><tbody>{graph_edge_rows}</tbody></table></div>
<p class="muted">Curated alias matches and shared metadata are discovery cues only. They do not establish factual truth, causality, influence, or source independence.</p></section>
<section class="panel"><h2>Analyst strategic report</h2><div class="grid">{analyst_cards}</div>
<p>{_cell(analyst.get("executive_summary") or "No analyst report available.")}</p>
<h3>Key findings for review</h3><div class="table-wrap"><table><thead><tr><th>Priority</th><th>Finding</th><th>Source</th><th>Country</th><th>Signal ID</th></tr></thead><tbody>{''.join(analyst_findings)}</tbody></table></div>
<h3>Uncertainties and evidence gaps</h3><ul>{analyst_uncertainties}</ul>
<h3>Recommended human review actions</h3><ul>{analyst_actions}</ul>
<p class="muted">Deterministic synthesis of supplied assessments, not generative AI or independent fact verification. Human approval is required.</p></section>
<section class="panel" id="signals"><h2>Strategic decision review queue</h2><div class="table-wrap"><table><thead><tr><th>Priority</th><th>Signal</th><th class="num">Score</th><th>Warning</th><th>Source</th><th>Article URL</th></tr></thead><tbody>{''.join(review_rows)}</tbody></table></div><p class="muted">Priority is a human-review ordering cue, not event severity or probability.</p></section>
<section class="columns">
<article class="panel"><h2>Warning distribution</h2><ul>{warnings}</ul></article>
<article class="panel"><h2>Source metadata status</h2><ul>{source_summary}</ul></article>
</section>
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

<section class="panel"><h2>Global intelligence overview</h2><div class="grid">{global_cards}</div></section>
<section class="columns">
<article class="panel"><h2>Country activity</h2><div class="table-wrap"><table><thead><tr><th>Country</th><th class="num">Signals</th><th class="num">Avg. score</th><th>Score profile</th></tr></thead><tbody>{country_rows}</tbody></table></div></article>
<article class="panel"><h2>Topic activity</h2><div class="table-wrap"><table><thead><tr><th>Topic</th><th class="num">Signals</th><th class="num">Avg. score</th><th>Score profile</th></tr></thead><tbody>{topic_rows}</tbody></table></div></article>
</section>
<section class="panel"><h2>Rising signals</h2><div class="table-wrap"><table><thead><tr><th>Trend</th><th>Country</th><th>Topics</th><th class="num">Score</th><th class="num">Momentum</th></tr></thead><tbody>{''.join(rising_rows)}</tbody></table></div></section>
<section class="panel"><h2>Related-event discovery</h2><div class="table-wrap"><table><thead><tr><th>Event A</th><th>Country</th><th>Event B</th><th>Country</th><th>Relationship basis</th></tr></thead><tbody>{''.join(relation_rows)}</tbody></table></div><p class="muted">These are discovery candidates based on shared metadata or wording, not evidence of causality or independent corroboration.</p></section>
<section class="panel"><h2>Source intelligence &amp; provenance</h2><div class="table-wrap"><table><thead><tr><th>Trend</th><th>Source</th><th>Domain</th><th>Metadata status</th><th class="num">Checks</th><th>Reliability verdict</th></tr></thead><tbody>{''.join(source_rows)}</tbody></table></div></section>
<section class="panel"><h2>Category distribution</h2><div class="table-wrap"><table><thead><tr><th>Category</th><th class="num">Signals</th></tr></thead><tbody>{category_rows}</tbody></table></div></section>
<section class="panel"><h2>Advanced trend intelligence</h2><div class="table-wrap"><table><thead><tr><th>Trend</th><th>Category</th><th class="num">Score</th><th>Warning</th><th>History</th><th class="num">Momentum</th><th class="num">Acceleration</th><th>Anomaly review</th><th>Confidence</th><th>Source</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<p class="notice">Source checks describe supplied metadata and provenance fields only. They do not rate source reputation or verify claims. Reliability and editorial independence are not assessed automatically. Momentum and acceleration are descriptive; anomaly flags require human review. No indicator is a probability or guaranteed forecast.</p>
<footer>Generated locally by MD V14. This dashboard is a static report; it does not transmit data or publish content.</footer>
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
  const raw = document.getElementById("report-updated").textContent.trim();
  const parsed = Date.parse(raw);
  if (Number.isFinite(parsed)) {{
    document.getElementById("report-updated").textContent =
      new Intl.DateTimeFormat("id-ID", {{ dateStyle: "medium", timeStyle: "medium", timeZone: "Asia/Jakarta" }}).format(new Date(parsed)) + " WIB";
  }}
}})();
</script></body></html>
"""
