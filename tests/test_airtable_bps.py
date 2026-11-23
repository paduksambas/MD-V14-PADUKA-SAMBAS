"""Tests for PADUKA's Airtable BPS synchronization and validated export."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import airtable_bps


def observation(variable="163", value=4.99):
    return {
        "region_code": "6101",
        "region_name": "Kabupaten Sambas",
        "level": "regency_city",
        "indicator_code": variable,
        "indicator_name": "Tingkat Pengangguran Terbuka (TPT)" if variable == "163" else "EPR",
        "period": "2024",
        "value": value,
        "unit": "Persen",
        "source": "BPS WebAPI",
        "source_url": "https://webapi.bps.go.id/documentation/",
        "bps_variable_id": variable,
        "bps_period_id": "124",
    }


def airtable_record(record_id, fields):
    return {"id": record_id, "fields": fields}


class AirtableBpsSyncTests(unittest.TestCase):
    def test_sync_creates_new_observation_and_writes_log(self):
        report = {"bps_regional_tables": {"observations": [observation()]}}
        with patch.object(airtable_bps, "_list_all_records", return_value=[]), patch.object(
            airtable_bps, "_api_request", return_value={"records": [{"id": "recCreated"}]}
        ) as api:
            result = airtable_bps.sync_bps_observations(report, "fake-token")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["created"], 1)
        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["rejected"], 0)
        self.assertEqual(api.call_count, 1)
        method, path = api.call_args.args[1:3]
        self.assertEqual(method, "POST")
        self.assertEqual(path, f"/{airtable_bps.DEFAULT_BASE_ID}/{airtable_bps.OBSERVATIONS_TABLE_ID}")
        fields = api.call_args.kwargs["payload"]["records"][0]["fields"]
        self.assertEqual(fields["Kunci Observasi"], "6101|163|2024")
        self.assertEqual(fields["Nilai"], 4.99)
        self.assertEqual(fields["Status Validasi"], "Belum ditinjau")

    def test_sync_preserves_valid_status_when_value_is_unchanged(self):
        report = {"bps_regional_tables": {"observations": [observation()]}}
        existing = airtable_record("recExisting", {
            "Kunci Observasi": "6101|163|2024",
            "Kode Domain BPS": "6101",
            "Nama Wilayah": "Kabupaten Sambas",
            "Level Wilayah": "regency_city",
            "Kode Variabel BPS": "163",
            "Kode Indikator": "163",
            "Nama Indikator": "Tingkat Pengangguran Terbuka (TPT)",
            "Periode": "2024",
            "Nilai": 4.99,
            "Satuan": "Persen",
            "Status Validasi": "Valid",
        })
        with patch.object(airtable_bps, "_list_all_records", return_value=[existing]), patch.object(
            airtable_bps, "_api_request", return_value={"records": [{"id": "recExisting"}]}
        ) as api:
            result = airtable_bps.sync_bps_observations(report, "fake-token")

        self.assertEqual(result["created"], 0)
        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["unchanged"], 1)
        patch_fields = api.call_args.kwargs["payload"]["records"][0]["fields"]
        self.assertEqual(patch_fields["Status Validasi"], "Valid")

    def test_sync_resets_validation_if_bps_value_changes(self):
        report = {"bps_regional_tables": {"observations": [observation(value=5.1)]}}
        existing = airtable_record("recExisting", {
            "Kunci Observasi": "6101|163|2024",
            "Kode Domain BPS": "6101",
            "Nama Wilayah": "Kabupaten Sambas",
            "Level Wilayah": "regency_city",
            "Kode Variabel BPS": "163",
            "Kode Indikator": "163",
            "Nama Indikator": "Tingkat Pengangguran Terbuka (TPT)",
            "Periode": "2024",
            "Nilai": 4.99,
            "Satuan": "Persen",
            "Status Validasi": "Valid",
        })
        with patch.object(airtable_bps, "_list_all_records", return_value=[existing]), patch.object(
            airtable_bps, "_api_request", return_value={"records": [{"id": "recExisting"}]}
        ) as api:
            result = airtable_bps.sync_bps_observations(report, "fake-token")

        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["unchanged"], 0)
        patch_fields = api.call_args.kwargs["payload"]["records"][0]["fields"]
        self.assertEqual(patch_fields["Nilai"], 5.1)
        self.assertEqual(patch_fields["Status Validasi"], "Belum ditinjau")

    def test_sync_resets_validation_if_indicator_metadata_changes(self):
        changed = observation()
        changed["unit"] = "Jiwa"
        report = {"bps_regional_tables": {"observations": [changed]}}
        existing = airtable_record("recExisting", {
            "Kunci Observasi": "6101|163|2024",
            "Kode Domain BPS": "6101",
            "Nama Wilayah": "Kabupaten Sambas",
            "Level Wilayah": "regency_city",
            "Kode Variabel BPS": "163",
            "Kode Indikator": "163",
            "Nama Indikator": "Tingkat Pengangguran Terbuka (TPT)",
            "Periode": "2024",
            "Nilai": 4.99,
            "Satuan": "Persen",
            "Status Validasi": "Valid",
        })
        with patch.object(airtable_bps, "_list_all_records", return_value=[existing]), patch.object(
            airtable_bps, "_api_request", return_value={"records": [{"id": "recExisting"}]}
        ) as api:
            result = airtable_bps.sync_bps_observations(report, "fake-token")
        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["unchanged"], 0)
        patch_fields = api.call_args.kwargs["payload"]["records"][0]["fields"]
        self.assertEqual(patch_fields["Status Validasi"], "Belum ditinjau")

    def test_sync_rejects_duplicate_keys_within_one_bps_response(self):
        report = {"bps_regional_tables": {"observations": [observation(), observation()]}}
        with patch.object(airtable_bps, "_list_all_records", return_value=[]), patch.object(
            airtable_bps, "_api_request", return_value={"records": [{"id": "recCreated"}]}
        ) as api:
            result = airtable_bps.sync_bps_observations(report, "fake-token")
        self.assertEqual(result["created"], 1)
        self.assertEqual(result["rejected"], 1)
        self.assertEqual(result["status"], "partial")
        api.assert_called_once()

    def test_sync_rejects_non_numeric_values_instead_of_zero_filling(self):
        report = {"bps_regional_tables": {"observations": [
            observation(value=None),
            observation(value=True),
            {"region_code": "6101", "value": "not-a-number"},
        ]}}
        with patch.object(airtable_bps, "_list_all_records", return_value=[]), patch.object(
            airtable_bps, "_api_request"
        ) as api:
            result = airtable_bps.sync_bps_observations(report, "fake-token")

        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["received"], 3)
        self.assertEqual(result["created"], 0)
        self.assertEqual(result["rejected"], 3)
        api.assert_not_called()

    def test_sync_rejects_duplicate_keys_already_in_airtable(self):
        report = {"bps_regional_tables": {"observations": [observation()]}}
        existing = [
            airtable_record("recOne", {"Kunci Observasi": "6101|163|2024"}),
            airtable_record("recTwo", {"Kunci Observasi": "6101|163|2024"}),
        ]
        with patch.object(airtable_bps, "_list_all_records", return_value=existing), patch.object(
            airtable_bps, "_api_request"
        ) as api:
            with self.assertRaisesRegex(RuntimeError, "duplicate Kunci Observasi"):
                airtable_bps.sync_bps_observations(report, "fake-token")
        api.assert_not_called()

    def test_empty_bps_response_is_no_data_without_airtable_write(self):
        report = {"bps_regional_tables": {"observations": []}}
        with patch.object(airtable_bps, "_list_all_records") as list_records, patch.object(
            airtable_bps, "_api_request"
        ) as api:
            result = airtable_bps.sync_bps_observations(report, "fake-token")
        self.assertEqual(result["status"], "no_data")
        list_records.assert_not_called()
        api.assert_not_called()

    def test_export_only_includes_rows_marked_valid(self):
        records = [
            airtable_record("recValid", {
                "Status Validasi": "Valid", "Kode Domain BPS": "6101",
                "Nama Wilayah": "Kabupaten Sambas", "Level Wilayah": "regency_city",
                "Kode Indikator": "163", "Nama Indikator": "TPT",
                "Periode": "2024", "Nilai": 4.99, "Satuan": "Persen",
                "Sumber": "BPS WebAPI", "URL Sumber": "https://webapi.bps.go.id/documentation/",
            }),
            airtable_record("recPending", {
                "Status Validasi": "Belum ditinjau", "Kode Domain BPS": "6101",
                "Nama Wilayah": "Kabupaten Sambas", "Level Wilayah": "regency_city",
                "Kode Indikator": "168", "Nama Indikator": "EPR",
                "Periode": "2024", "Nilai": 69.15,
            }),
        ]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "valid.json"
            with patch.object(airtable_bps, "_list_all_records", return_value=records):
                result = airtable_bps.export_validated_observations("fake-token", output)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(result["exported"], 1)
        self.assertEqual(payload["observations"][0]["value"], 4.99)
        self.assertEqual(payload["observations"][0]["indicator_code"], "163")

    def test_export_skips_valid_rows_with_invalid_values(self):
        records = [airtable_record("recInvalid", {
            "Status Validasi": "Valid", "Kode Domain BPS": "6101",
            "Nama Wilayah": "Kabupaten Sambas", "Level Wilayah": "regency_city",
            "Kode Indikator": "163", "Nama Indikator": "TPT",
            "Periode": "2024", "Nilai": True,
        })]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "valid.json"
            with patch.object(airtable_bps, "_list_all_records", return_value=records):
                result = airtable_bps.export_validated_observations("fake-token", output)
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(result["exported"], 0)
        self.assertEqual(result["rejected"], 1)
        self.assertEqual(payload, {"observations": []})

    def test_api_error_message_does_not_expose_token(self):
        token = "DO_NOT_PRINT_THIS_SECRET"
        with patch.object(airtable_bps.urllib.request, "urlopen", side_effect=airtable_bps.urllib.error.HTTPError(
            "https://api.airtable.com/v0/app/tbl", 401, "unauthorized", {}, None
        )):
            with self.assertRaises(RuntimeError) as caught:
                airtable_bps._api_request(token, "GET", "/app/tbl")
        self.assertNotIn(token, str(caught.exception))
        self.assertIn("HTTP 401", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
