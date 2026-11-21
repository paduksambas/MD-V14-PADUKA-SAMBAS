"""Generate a self-contained, offline HTML analytics dashboard."""
from __future__ import annotations

from collections import Counter
from html import escape
from typing import Any


def _cell(value: Any) -> str:
    return escape(str(value if value is not None else ""), quote=True)


def build_dashboard_html(report: dict[str, Any]) -> str:
    """Render an accessible static dashboard from an existing MD V14 report."""
    signals = report.get("signals", [])
    brief = report.get("daily_brief", {})
    warning_counts = report.get("warning_summary", {})
    categories = Counter(str(item.get("category") or "Unclassified") for item in signals)
    history = [item.get("history") for item in signals if item.get("history")]
    reviewed = sum(1 for item in signals if not item.get("evidence", {}).get("evidence_complete", False))
    avg_score = (sum(float(item.get("score", 0) or 0) for item in signals) / len(signals)) if signals else 0.0
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
    for item in sorted(signals, key=lambda x: float(x.get("score", 0) or 0), reverse=True):
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
<style>
:root{{color-scheme:light dark;--bg:#101827;--panel:#182438;--line:#314158;--muted:#a9b8cc;--text:#f2f6fc;--accent:#83b7ff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,sans-serif}}
main{{max-width:1180px;margin:auto;padding:28px 20px 56px}}header{{margin-bottom:24px}}h1{{font-size:clamp(1.6rem,4vw,2.35rem);margin:0 0 6px}}h2{{font-size:1.1rem;margin:0 0 14px}}.muted,small{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:12px;margin:20px 0}}
.metric,.panel{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:17px}}.metric strong{{display:block;font-size:1.9rem;margin:5px 0}}.metric small{{display:block}}
.columns{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0}}@media(max-width:700px){{.columns{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}}th,td{{text-align:left;padding:10px 8px;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:var(--muted);font-weight:600}}.num{{font-variant-numeric:tabular-nums;text-align:right}}.table-wrap{{overflow-x:auto}}ul{{list-style:none;padding:0;margin:0}}li{{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--line)}}.notice{{border-left:3px solid var(--accent);padding:10px 14px;background:var(--panel);border-radius:5px;color:var(--muted);margin-top:18px}}footer{{margin-top:22px;color:var(--muted);font-size:.85rem}}
</style></head><body><main>
<header><div class="muted">PADUKA SAMBAS · GLOBAL TREND INTELLIGENCE</div>
<h1>{_cell(title)}</h1><div class="muted">Report date: {_cell(date_label)}</div></header>
<section class="grid">{cards}</section>
<section class="columns">
<article class="panel"><h2>Warning distribution</h2><ul>{warnings}</ul></article>
<article class="panel"><h2>Source metadata status</h2><ul>{source_summary}</ul></article>
</section>
<section class="panel"><h2>Source intelligence &amp; provenance</h2><div class="table-wrap"><table><thead><tr><th>Trend</th><th>Source</th><th>Domain</th><th>Metadata status</th><th class="num">Checks</th><th>Reliability verdict</th></tr></thead><tbody>{''.join(source_rows)}</tbody></table></div></section>
<section class="panel"><h2>Category distribution</h2><div class="table-wrap"><table><thead><tr><th>Category</th><th class="num">Signals</th></tr></thead><tbody>{category_rows}</tbody></table></div></section>
<section class="panel"><h2>Advanced trend intelligence</h2><div class="table-wrap"><table><thead><tr><th>Trend</th><th>Category</th><th class="num">Score</th><th>Warning</th><th>History</th><th class="num">Momentum</th><th class="num">Acceleration</th><th>Anomaly review</th><th>Confidence</th><th>Source</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<p class="notice">Source checks describe supplied metadata and provenance fields only. They do not rate source reputation or verify claims. Reliability and editorial independence are not assessed automatically. Momentum and acceleration are descriptive; anomaly flags require human review. No indicator is a probability or guaranteed forecast.</p>
<footer>Generated locally by MD V14. This dashboard is a static report; it does not transmit data or publish content.</footer>
</main></body></html>
