from cdis.database import connection
from cdis.models import UTC, PROVINCES


def find_duplicate_entities(db_path, legal_name, corporation_number=None):
    legal_name = (legal_name or "").strip().lower()
    corporation_number = "".join(ch for ch in (corporation_number or "") if ch.isalnum()).lower()
    matches = []
    with connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM legal_entities").fetchall()
    for row in rows:
        name = (row["legal_business_name"] or "").strip().lower()
        corp = "".join(ch for ch in (row["corporation_number"] or "") if ch.isalnum()).lower()
        if corporation_number and corporation_number == corp:
            matches.append(dict(row) | {"match_basis": "Corporation number"})
        elif legal_name and name == legal_name:
            matches.append(dict(row) | {"match_basis": "Normalized legal name"})
    return matches


def add_entity(db_path, name, trade_name=None, corporation_number=None, jurisdiction=None,
               corporate_status="Unknown", status_source=None, status_verified=None, notes=None):
    if not name or not name.strip():
        raise ValueError("Legal business name is required")
    now = UTC()
    with connection(db_path) as conn:
        cur = conn.execute("""INSERT INTO legal_entities
            (legal_business_name,operating_trade_name,corporation_number,incorporation_jurisdiction,
             corporate_status,corporate_status_source,corporate_status_last_verified,date_created,date_last_updated,notes)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (name.strip(), trade_name, corporation_number, jurisdiction, corporate_status,
             status_source, status_verified, now, now, notes))
        conn.commit()
        return cur.lastrowid


def add_location(db_path, entity_id, data):
    province = data.get("province_territory")
    if province not in PROVINCES:
        raise ValueError("Invalid province/territory code")
    if not data.get("physical_street_address"):
        raise ValueError("Physical street address is required")
    now = UTC()
    with connection(db_path) as conn:
        cur = conn.execute("""INSERT INTO dealership_locations
            (entity_id,dealership_location_name,physical_street_address,address_line2,city,
             province_territory,postal_code,country,dealer_license_number,dealer_license_status,
             external_registry_id,source_name,source_record_date,last_verified_date,date_created,date_last_updated)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (entity_id, data.get("dealership_location_name"), data.get("physical_street_address"),
             data.get("address_line2"), data.get("city"), province, data.get("postal_code"),
             data.get("country","Canada"), data.get("dealer_license_number"),
             data.get("dealer_license_status","Unknown"), data.get("external_registry_id"),
             data.get("source_name"), data.get("source_record_date"), data.get("last_verified_date"), now, now))
        location_id = cur.lastrowid
        conn.execute("""INSERT INTO monitoring_records
            (location_id,monitoring_category,monitoring_active,reason_for_monitoring,date_added,date_last_updated,internal_notes)
            VALUES(?,?,?,?,?,?,?)""",
            (location_id, data.get("monitoring_category","Potential"),
             int(data.get("monitoring_active", True)), data.get("monitoring_reason"), now, now, data.get("notes")))
        conn.execute("""INSERT INTO audit_history
            (location_id,entity_id,action_type,new_value,source,action_date)
            VALUES(?,?,?,?,?,?)""",
            (location_id, entity_id, "Dealership added", data.get("dealership_location_name"),
             data.get("source_name","Manual entry"), now))
        conn.commit()
        return location_id


def archive_location(db_path, location_id, reason):
    now = UTC()
    with connection(db_path) as conn:
        conn.execute("UPDATE dealership_locations SET archived=1,archive_reason=?,date_last_updated=? WHERE location_id=?",
                     (reason, now, location_id))
        conn.execute("UPDATE monitoring_records SET monitoring_active=0,date_last_updated=? WHERE location_id=?",
                     (now, location_id))
        conn.execute("INSERT INTO audit_history(location_id,action_type,new_value,action_date) VALUES(?,?,?,?)",
                     (location_id, "Dealership archived", reason, now))
        conn.commit()


def restore_location(db_path, location_id):
    now = UTC()
    with connection(db_path) as conn:
        conn.execute("UPDATE dealership_locations SET archived=0,archive_reason=NULL,date_last_updated=? WHERE location_id=?",
                     (now, location_id))
        conn.execute("UPDATE monitoring_records SET monitoring_active=1,date_last_updated=? WHERE location_id=?", (now, location_id))
        conn.execute("INSERT INTO audit_history(location_id,action_type,action_date) VALUES(?,?,?)",
                     (location_id, "Dealership restored", now))
        conn.commit()
