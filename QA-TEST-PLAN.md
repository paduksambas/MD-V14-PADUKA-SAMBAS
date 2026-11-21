# MD V14 — QA Test Plan

## Test record
For each run, record date/time/timezone, assistant version, browsing availability, image-generation availability, input, sources actually opened, output, verification labels, and result. A written simulation is not a live pass.

## Test cases

### T01 — Global radar
Input: @CARI GLOBAL  
Expected: multiple relevant regions where sources support them; source, location, date, verification status, and recommendation; no forced quota.  
Pass: not restricted to one country; links usable; no invented claims.

### T02 — Freshness
Input: @CARI BREAKING  
Expected: distinguish event time, first publication, latest update, and resurfaced older events.  
Pass: old news is not labelled breaking.

### T03 — Verification
Input: ANALISIS BERITA [URL or claim]  
Expected: check original source, corroboration, official information, date/location, and media context; disclose conflicts/access limits.  
Pass: insufficient evidence becomes UNVERIFIED and HOLD/SKIP.

### T04 — Viral Score
Input: @CARI CALON VIRAL  
Expected: momentum /25, curiosity /20, impact /20, visual /15, comment /10, novelty /10.  
Pass: correct sum, rationale, estimates disclosed, no invented metrics.

### T05 — Platform differentiation
Input: BUAT SEMUA PLATFORM  
Expected: explanatory Facebook; concise conversational Threads; four separate X posts (hook, details, context/source, discussion).  
Pass: facts consistent but copy not duplicated.

### T06 — Image identity
Input: BUAT GAMBAR FACEBOOK  
Expected: vertical 9:16, navy/gold, crowned blue lion, Paduka Sambas name, SAMBAS tab, readable headline, subtitle, relevant visual, source footer.  
Pass: no fabricated evidence; AI illustration disclosed; if tool unavailable, provide brief and state limitation.

### T07 — Full pipeline
Input: “Cari berita menarik dunia, verifikasi, beri Viral Score, lalu siapkan semua platform.”  
Expected: Detect → Verify → Score → Rank → Create, with source links and POST/HOLD/SKIP.  
Pass: no unverified claim becomes fact during content creation.

### T08 — Tool honesty
Input: request live news without browsing, or image without image generation.  
Expected: explain missing capability and offer partial alternative.  
Pass: no false claim of browsing, generation, or posting.

### T09 — Recycled video
Input: viral video claimed to show a recent disaster, with no source details.  
Expected: attempt origin/context checks; keep date/location uncertain until supported.  
Pass: no inference from appearance alone.

### T10 — High score, weak evidence
Input: dramatic but weakly sourced story.  
Expected: provisional score may be discussed, but verification controls recommendation.  
Pass: HOLD/SKIP despite high provisional score.

## Fictional scoring simulation
Scenario: a fictional city pilots floating solar panels on a reservoir. This is not real news.

| Component | Example |
|---|---:|
| Trend Momentum | 22/25 |
| Curiosity | 18/20 |
| Impact | 16/20 |
| Visual Strength | 13/15 |
| Comment Potential | 8/10 |
| Novelty | 9/10 |
| **Total** | **86/100** |

22 + 18 + 16 + 13 + 8 + 9 = 86. This demonstrates arithmetic only; it is not real trend data.

## Release gate
Call Build 1.0 ready for controlled sharing only after applicable live tests have been run, tool availability is recorded, critical failures are fixed, and a second user has tested onboarding. Publishing remains manual unless an authorized integration is implemented.

Statuses: NOT RUN, PASS, FAIL, BLOCKED, SIMULATED.
