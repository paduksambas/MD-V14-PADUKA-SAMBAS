import io
import unittest
import zipfile
from unittest.mock import patch

from mdv14.commodity_data import (
    _parse_workbook, fetch_world_bank_commodity_data,
    discover_monthly_workbook_url, render_world_bank_commodity_html,
)


def workbook_fixture():
    files = {
        "xl/workbook.xml": """<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Monthly Prices" sheetId="1" r:id="rId1"/></sheets></workbook>""",
        "xl/_rels/workbook.xml.rels": """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="worksheet"/></Relationships>""",
        "xl/sharedStrings.xml": """<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>Period</t></si><si><t>Crude oil, Brent</t></si><si><t>Gold</t></si><si><t>USD per barrel</t></si><si><t>USD per troy ounce</t></si><si><t>2026M08</t></si><si><t>2026M09</t></si><si><t>...</t></si></sst>""",
        "xl/worksheets/sheet1.xml": """<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>
        <row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c></row>
        <row r="2"><c r="B2" t="s"><v>3</v></c><c r="C2" t="s"><v>4</v></c></row>
        <row r="3"><c r="A3" t="s"><v>5</v></c><c r="B3"><v>72.5</v></c><c r="C3"><v>3400</v></c></row>
        <row r="4"><c r="A4" t="s"><v>6</v></c><c r="B4"><v>...</v></c><c r="C4"><v>3500</v></c></row>
        </sheetData></worksheet>"""
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


class WorldBankCommodityTests(unittest.TestCase):
    def test_parses_selected_monthly_prices_and_preserves_missing_values(self):
        result = _parse_workbook(workbook_fixture(), start_date="2026-08-01", end_date="2026-09-30")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["series_id"], "WB:CRUDE_BRENT")
        self.assertEqual(result[0]["value"], 72.5)
        self.assertEqual(result[0]["unit"], "USD per barrel")
        self.assertEqual(result[-1]["date"], "2026-09-01")
        self.assertFalse(any(item["series_id"] == "WB:CRUDE_BRENT" and item["date"] == "2026-09-01" for item in result))

    def test_date_filter_is_applied_by_month(self):
        result = _parse_workbook(workbook_fixture(), start_date="2026-09-01", end_date="2026-09-30")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["series_id"], "WB:GOLD")

    @patch("mdv14.commodity_data._read_url")
    def test_discovers_current_release_link_and_checks_host(self, read):
        read.return_value = (b'<a href="https://thedocs.worldbank.org/en/doc/abc/related/CMO-Historical-Data-Monthly.xlsx">Monthly</a>', "https://www.worldbank.org/en/research/commodity-markets")
        self.assertIn("thedocs.worldbank.org", discover_monthly_workbook_url())
        read.assert_called_once()

    @patch("mdv14.commodity_data.discover_monthly_workbook_url")
    @patch("mdv14.commodity_data._read_url")
    def test_fetch_success_normalizes_and_attributes(self, read, discover):
        discover.return_value = "https://thedocs.worldbank.org/en/doc/abc/related/CMO-Historical-Data-Monthly.xlsx"
        read.return_value = (workbook_fixture(), discover.return_value)
        result = fetch_world_bank_commodity_data(start_date="2026-08-01", end_date="2026-09-30")
        self.assertEqual(result["build"], "3.7")
        self.assertEqual(result["status"], "available")
        self.assertEqual(result["observation_count"], 3)
        self.assertIn("CC BY 4.0", result["license"])
        self.assertEqual(read.call_count, 1)

    @patch("mdv14.commodity_data.discover_monthly_workbook_url")
    def test_provider_failure_is_explicit(self, discover):
        discover.side_effect = RuntimeError("service unavailable")
        result = fetch_world_bank_commodity_data(start_date="2026-01-01", end_date="2026-02-01")
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["observation_count"], 0)
        self.assertEqual(result["requests_failed"], 1)

    def test_validates_range_and_timeout(self):
        with self.assertRaises(ValueError):
            fetch_world_bank_commodity_data(start_date="2026-02-01", end_date="2026-01-01")
        with self.assertRaises(ValueError):
            fetch_world_bank_commodity_data(start_date="2010-01-01", end_date="2026-01-01")
        with self.assertRaises(ValueError):
            fetch_world_bank_commodity_data(timeout=0)

    def test_dashboard_escapes_provider_data(self):
        html = render_world_bank_commodity_html({
            "status": "available", "observation_count": 1, "requests_succeeded": 2,
            "observations": [{"series": "<script>", "date": "2026-09-01",
                              "value": 1, "unit": "USD", "category": "energy"}],
            "errors": [],
        })
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn("CC BY 4.0", html)


if __name__ == "__main__":
    unittest.main()
