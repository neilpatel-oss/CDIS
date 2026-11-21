import re
from cdis.database import connection
from cdis.models import UTC


def normalize_address(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def find_change_location(db_path, row):
    external = str(row.get("external_registry_id") or "").strip()
    licence = str(row.get("dealer_license_number") or "").strip()
    with connection(db_path) as conn:
        rows = conn.execute("""SELECT l.*,e.legal_business_name FROM dealership_locations l
            JOIN legal_entities e ON e.entity_id=l.entity_id""").fetchall()
    for loc in rows:
        if external and external.lower() == str(loc["external_registry_id"] or "").lower():
            return dict(loc), "High"
        if licence and licence.lower() == str(loc["dealer_license_number"] or "").lower():
            return dict(loc), "High"
        name_match = str(loc["legal_business_name"] or "").strip().lower() == str(row.get("legal_business_name") or "").strip().lower()
        address_match = normalize_address(loc["physical_street_address"]) == normalize_address(row.get("physical_street_address"))
        if name_match and address_match:
            return dict(loc), "Medium"
    return None, None


def detect_changes(db_path, filename, source_name, source_record_date, df, mapping):
    detected = 0
    with connection(db_path) as conn:
        for _, input_row in df.iterrows():
            row = {target: input_row[source] if source in input_row and pd_notna(input_row[source]) else None
                   for target, source in mapping.items()}
            match, confidence = find_change_location(db_path, row)
            if not match:
                continue
            fields = {
                "physical_street_address": (match["physical_street_address"], row.get("physical_street_address")),
                "corporate_status": (None, row.get("corporate_status")),
                "dealer_license_status": (match["dealer_license_status"], row.get("dealer_license_status")),
                "dealership_location_name": (match["dealership_location_name"], row.get("dealership_location_name"))
            }
            if row.get("corporate_status"):
                entity = conn.execute("SELECT corporate_status FROM legal_entities WHERE entity_id=?", (match["entity_id"],)).fetchone()
                fields["corporate_status"] = (entity["corporate_status"] if entity else None, row.get("corporate_status"))
            for field, (old, new) in fields.items():
                old_text = "" if old is None else str(old)
                new_text = "" if new is None else str(new)
                if new_text and old_text.strip().lower() != new_text.strip().lower():
                    conn.execute("""INSERT INTO change_log
                        (location_id,entity_id,field_changed,previous_value,proposed_value,source,
                         source_record_date,date_detected,review_status)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                        (match["location_id"], match["entity_id"], field, old_text, new_text,
                         source_name, source_record_date, UTC(), "Pending"))
                    detected += 1
        conn.execute("INSERT INTO import_history(filename,import_type,rows_processed,records_added,records_skipped,date_imported,import_notes) VALUES(?,?,?,?,?,?,?)",
                     (filename, "Registry snapshot", len(df), 0, 0, UTC(), f"Detected {detected} proposed change(s); missing records were ignored"))
        conn.commit()
    return detected


def pd_notna(value):
    try:
        import pandas as pd
        return not pd.isna(value)
    except Exception:
        return value is not None
