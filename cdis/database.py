import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "cdis.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS legal_entities (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    legal_business_name TEXT NOT NULL,
    operating_trade_name TEXT,
    corporation_number TEXT,
    incorporation_jurisdiction TEXT,
    corporate_status TEXT NOT NULL DEFAULT 'Unknown',
    corporate_status_source TEXT,
    corporate_status_last_verified TEXT,
    date_created TEXT NOT NULL,
    date_last_updated TEXT NOT NULL,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS dealership_locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    dealership_location_name TEXT,
    physical_street_address TEXT,
    address_line2 TEXT,
    city TEXT,
    province_territory TEXT,
    postal_code TEXT,
    country TEXT DEFAULT 'Canada',
    dealer_license_number TEXT,
    dealer_license_status TEXT NOT NULL DEFAULT 'Unknown',
    external_registry_id TEXT,
    source_name TEXT,
    source_record_date TEXT,
    last_verified_date TEXT,
    date_created TEXT NOT NULL,
    date_last_updated TEXT NOT NULL,
    archived INTEGER NOT NULL DEFAULT 0,
    archive_reason TEXT,
    FOREIGN KEY(entity_id) REFERENCES legal_entities(entity_id)
);
CREATE TABLE IF NOT EXISTS monitoring_records (
    monitoring_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL UNIQUE,
    monitoring_category TEXT NOT NULL,
    monitoring_active INTEGER NOT NULL DEFAULT 1,
    reason_for_monitoring TEXT,
    date_added TEXT NOT NULL,
    date_last_updated TEXT NOT NULL,
    internal_notes TEXT,
    FOREIGN KEY(location_id) REFERENCES dealership_locations(location_id)
);
CREATE TABLE IF NOT EXISTS financing_relationships (
    relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
    legal_entity_id INTEGER NOT NULL,
    location_id INTEGER,
    financial_institution_name TEXT NOT NULL,
    financing_type TEXT NOT NULL,
    relationship_status TEXT NOT NULL DEFAULT 'Unknown',
    source_document TEXT,
    source_date TEXT,
    last_verified_date TEXT,
    confidence_level TEXT NOT NULL,
    notes TEXT,
    date_created TEXT NOT NULL,
    FOREIGN KEY(legal_entity_id) REFERENCES legal_entities(entity_id)
);
CREATE TABLE IF NOT EXISTS change_log (
    change_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER,
    entity_id INTEGER,
    field_changed TEXT NOT NULL,
    previous_value TEXT,
    proposed_value TEXT,
    source TEXT,
    source_record_date TEXT,
    date_detected TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'Pending',
    reviewer_note TEXT,
    date_reviewed TEXT,
    decision TEXT
);
CREATE TABLE IF NOT EXISTS source_records (
    source_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER,
    source_name TEXT,
    external_registry_id TEXT,
    imported_source_information TEXT,
    retrieval_date TEXT,
    source_record_date TEXT
);
CREATE TABLE IF NOT EXISTS import_history (
    import_id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    import_type TEXT,
    rows_processed INTEGER DEFAULT 0,
    records_added INTEGER DEFAULT 0,
    records_skipped INTEGER DEFAULT 0,
    date_imported TEXT NOT NULL,
    import_notes TEXT
);
CREATE TABLE IF NOT EXISTS audit_history (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER,
    entity_id INTEGER,
    action_type TEXT NOT NOT NULL,
    field_name TEXT,
    previous_value TEXT,
    new_value TEXT,
    source TEXT,
    action_date TEXT NOT NULL,
    reviewer TEXT
);
CREATE TABLE IF NOT EXISTS source_register (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    province_territory TEXT,
    authority TEXT,
    official_url TEXT,
    data_available TEXT,
    api_availability TEXT,
    bulk_availability TEXT,
    cost TEXT,
    commercial_permission TEXT,
    update_frequency TEXT,
    physical_address_available TEXT,
    legal_name_available TEXT,
    dealer_license_status_available TEXT,
    corporate_status_available TEXT,
    access_method TEXT,
    notes TEXT,
    verification_date TEXT
);
"""

@contextmanager
def connection(db_path=None):
    path = str(db_path or DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()

def init_db(db_path=None):
    with connection(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()

def reset_db(db_path=None, seed=True):
    path = db_path or DB_PATH
    if hasattr(path, "unlink"):
        path.unlink(missing_ok=True)
    else:
        Path(path).unlink(missing_ok=True)
    init_db(path)
    if seed:
        from cdis.demo_data import seed_demo_data
        seed_demo_data(path)
