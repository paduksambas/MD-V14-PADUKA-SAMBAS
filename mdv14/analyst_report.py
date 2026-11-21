"""Auditable analyst report assembled from existing MD V14 assessments.

This is deterministic report composition, not a generative AI model or fact verifier.
"""
from __future__ import annotations

from typing import Any


def build_analyst_report(report: dict[str, Any], *, limit: int = 10) -> dict[str, Any]:
    """Compose an executive brief, traceable findings, uncertainty and review actions."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    signals = report.get("signals", [])
    signals = [item for item in signals if isinstance(item, dict)] if isinstance(signals, list) else []
    decision = report.get("strategic_decision", {})
    decision = decision if isinstance(decision, dict) else {}
    queue = decision.get("review_queue", [])
    queue = [item for item in queue if isinstance(item, dict)] if isinstance(queue, list) else []
    research = report.get("research", {})
    research = research if isinstance(research, dict) else {}
    graph = report.get("knowledge_graph", {})
    graph = graph if isinstance(graph, dict) else {}
    impact = report.get("strategic_impact", {})
    impact = impact if isinstance(impact, dict) else {}
    collection = report.get("collection", {})
    collection = collection if isinstance(collection, dict) else {}

    evidence_complete = sum(
        1 for item in signals
        if isinstance(item.get("evidence"), dict)
        and item["evidence"].get("evidence_complete") is True
    )
    evidence_missing = sum(
        1 for item in signals
        if not isinstance(item.get("evidence"), dict)
        or item["evidence"].get("evidence_complete") is not True
    )
    unknown_country = sum(1 for item in signals if not item.get("country") or str(item.get("country")).casefold() == "unknown")
    missing_url = sum(1 for item in signals if not item.get("url"))
    language = report.get("language_intelligence", {})
    language = language if isinstance(language, dict) else {}
    unknown_language = language.get("records_with_unknown_language", len(signals))
    try:
        unknown_language = max(0, int(unknown_language))
    except (TypeError, ValueError):
        unknown_language = len(signals)

    bands = decision.get("priority_band_counts", {})
    bands = bands if isinstance(bands, dict) else {}
    high = int(bands.get("high", 0) or 0)
    medium = int(bands.get("medium", 0) or 0)
    routine = int(bands.get("routine", 0) or 0)
    graph_edges = int(graph.get("edges_total", 0) or 0)
    cross_border = impact.get("cross_border_review_candidates", [])
    cross_border_count = len(cross_border) if isinstance(cross_border, list) else 0
    research_gaps = research.get("research_gaps", [])
    research_gaps = [str(item) for item in research_gaps] if isinstance(research_gaps, list) else []
    feed_failures = int(collection.get("feeds_failed", 0) or 0)

    if not signals:
        executive = "Belum ada rekaman yang dapat dianalisis. Periksa konfigurasi sumber dan konektivitas sebelum menarik kesimpulan."
    else:
        executive = (
            f"MD V14 meninjau {len(signals)} rekaman. Antrean memuat {high} prioritas tinjauan tinggi, "
            f"{medium} menengah, dan {routine} rutin. {evidence_missing} rekaman belum memiliki metadata bukti lengkap. "
            "Peringkat ini mengarahkan urutan pemeriksaan, bukan mengukur probabilitas atau tingkat bahaya."
        )

    findings = []
    for item in queue[:limit]:
        findings.append({
            "signal_id": str(item.get("signal_id") or ""),
            "title": str(item.get("title") or ""),
            "source": str(item.get("source") or "unknown"),
            "url": str(item.get("url") or ""),
            "country": str(item.get("country") or "unknown"),
            "review_priority": item.get("priority_band", "routine"),
            "priority_score": item.get("priority_score"),
            "warning_level": item.get("warning_level", "not_assessed"),
            "impact_dimensions": item.get("impact_dimensions", []),
            "evidence_complete": item.get("evidence_complete"),
            "interpretation": "Kandidat untuk pemeriksaan analis berdasarkan skor dan metadata yang tersedia; klaim belum diverifikasi secara independen.",
        })

    uncertainties = [
        f"{evidence_missing} dari {len(signals)} rekaman tidak memiliki metadata bukti lengkap.",
        f"{missing_url} rekaman tidak memiliki URL artikel.",
        f"{unknown_country} rekaman tidak memiliki label negara yang diketahui.",
        f"{unknown_language} rekaman tidak memiliki label bahasa yang diketahui.",
        "Kelengkapan metadata tidak membuktikan kebenaran isi, kredibilitas penerbit, atau independensi sumber.",
    ]
    if feed_failures:
        uncertainties.append(f"{feed_failures} feed gagal pada siklus koleksi ini.")
    uncertainties.extend(research_gaps[:5])
    if not signals:
        uncertainties.append("Tidak tersedia sampel untuk menilai cakupan atau relevansi.")

    actions = []
    if evidence_missing or missing_url:
        actions.append({
            "priority": "high",
            "action": "Periksa artikel asli, atribusi penulis, tanggal publikasi, dan dokumen primer untuk rekaman dengan bukti tidak lengkap.",
            "basis": "evidence_metadata_gaps",
            "human_approval_required": True,
        })
    if high or medium:
        actions.append({
            "priority": "high" if high else "medium",
            "action": "Tinjau antrean prioritas berdasarkan urutan skor; bandingkan klaim dengan sumber primer dan catat bukti yang bertentangan.",
            "basis": "strategic_decision_review_queue",
            "human_approval_required": True,
        })
    if cross_border_count:
        actions.append({
            "priority": "medium",
            "action": "Validasi label negara, entitas, dan topik pada kandidat lintas negara sebelum menyimpulkan keterkaitan.",
            "basis": "explicit_metadata_cross_border_candidates",
            "human_approval_required": True,
        })
    if graph_edges:
        actions.append({
            "priority": "medium",
            "action": "Periksa node, alias, dan ID rekaman pendukung pada knowledge graph; buang kecocokan ambigu yang tidak didukung konteks.",
            "basis": "knowledge_graph_discovery_edges",
            "human_approval_required": True,
        })
    if feed_failures or unknown_country or unknown_language:
        actions.append({
            "priority": "medium",
            "action": "Perbaiki metadata katalog sumber dan pulihkan feed yang gagal sebelum memperluas kesimpulan cakupan global.",
            "basis": "collection_and_coverage_gaps",
            "human_approval_required": True,
        })
    if not actions:
        actions.append({
            "priority": "routine",
            "action": "Lanjutkan pemeriksaan sumber primer dan dokumentasikan ketidakpastian sebelum menggunakan laporan untuk keputusan.",
            "basis": "standard_quality_control",
            "human_approval_required": True,
        })

    return {
        "engine": "MD V14 Analyst Report Composer",
        "build": "2.9",
        "report_type": "deterministic_human_review_brief",
        "records_analyzed": len(signals),
        "executive_summary": executive,
        "priority_overview": {"high": high, "medium": medium, "routine": routine},
        "metadata_coverage": {
            "records_with_complete_evidence_metadata": evidence_complete,
            "records_with_incomplete_evidence_metadata": evidence_missing,
            "records_without_article_url": missing_url,
            "records_with_unknown_country": unknown_country,
            "records_with_unknown_language": unknown_language,
            "interpretation": "Metadata coverage only; not confidence in factual truth.",
        },
        "key_findings": findings,
        "strategic_context": {
            "cross_border_review_candidates": cross_border_count,
            "knowledge_graph_nodes": graph.get("nodes_total", 0),
            "knowledge_graph_edges": graph_edges,
            "research_question": research.get("research_question"),
            "research_candidates": research.get("records_with_keyword_match", 0),
        },
        "uncertainties_and_gaps": uncertainties,
        "recommended_human_actions": actions,
        "methodology": {
            "composition": "Rule-based synthesis of MD V14 pipeline assessments and source metadata; no new external research is performed in this stage.",
            "priority": "Copies the strategic decision queue's heuristic review order; not severity, probability, or a policy recommendation.",
            "metadata_coverage": "Describes completeness of supplied fields only; it is not a factual-confidence score.",
            "traceability": "Each finding preserves the signal ID, source, URL, and review metadata from the source record.",
        },
        "limitations": [
            "This module is deterministic report composition, not a connected large-language model or autonomous analyst.",
            "No claim is independently verified and no additional websites are discovered.",
            "Recommendations are human review tasks, not automated policy or operational instructions.",
            "Missing or biased source coverage can materially change the report.",
            "Human approval is required before escalation, publication, or strategic action.",
        ],
        "notice": "Analyst decision support only. Verify original sources, context, alternative explanations, and affected stakeholders before acting.",
    }
