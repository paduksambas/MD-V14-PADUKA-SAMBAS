# Build 3.1 — Global Geopolitical Intelligence Map & Country Explorer

## Implemented
- `mdv14/country_explorer.py` aggregates signals by explicitly supplied country labels.
- Curated country aliases canonicalize a small number of common labels (for example US/United States).
- A curated catalog supplies approximate country-centroid coordinates for geographic plotting.
- Each country profile includes signal count, average supplied score, review-priority counts, warning-level counts, and traceable record IDs, titles, sources, URLs, and scores.
- Countries without a supported centroid are retained as unmapped records; coordinates are never guessed.
- The offline HTML dashboard renders a responsive longitude/latitude plot. Markers and country selectors open country-specific records and source links.
- CLI output includes explorer build and mapped/unmapped country counts.

## Interpretation
The plotted points are approximate country-centroid references for countries named in the source metadata. They do not represent territorial borders, disputed boundaries, or verified event locations. The display is a geographic signal explorer, not a political boundary map.

Review-priority bands are inherited from the existing strategic decision queue. They indicate analyst review order only, not geopolitical risk, threat severity, conflict probability, or national stability. Average score is the average supplied signal score, not a country risk score.

## Data and limitations
- Only explicit country labels are grouped. Missing country labels remain unknown.
- The centroid catalog is finite and approximate; unmapped countries remain in the table without a plotted point.
- Country coverage reflects configured feeds and their metadata, not global representativeness.
- Signal-level source links and metadata are preserved for human verification.
- The explorer performs no new web research, geocoding, event geolocation, territorial inference, fact verification, forecasting, or autonomous decisions.

## Validation
Run `python -m unittest discover -s tests -v`. GitHub Actions Python 3.11 is the authoritative test result.
