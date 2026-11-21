import pandas as pd
import re
from cdis.database import connection

ALIASES = {
    "legal_business_name": ["legal_name","legal_business_name","business_name","company_name","corporate_name"],
    "dealership_location_name": ["dealer_name","dealership_name","dealership_location_name","location_name","trade_name"],
    "physical_street_address": ["physical_address","street_address","address","dealer_address","location_address"],
    "city": ["city","municipality"], "province_territory": ["province","province_territory","province_code","region"],
    "postal_code": ["postal_code","postcode","zip"], "dealer_license_number": ["licence_number","license_number","dealer_license_number","licence_no"],
    "external_registry_id": ["registry_id","external_registry_id","source_id","record_id"],
    "corporation_number": ["corporation_number","registry_number","corp_number"],
    "dealer_license_status": ["license_status","licence_status","dealer_license_status"],
    "corporate_status": ["corporate_status","company_status","corporation_status"]
}


def normalize_header(value):
    return re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")


def suggest_mapping(columns):
    mapped = {}
    for canon, aliases in ALIASES.items():
        for column in columns:
            if normalize_header(column) in aliases:
                mapped[canon] = column
                break
    return mapped


def read_import(file):
    name = getattr(file, "name", str(file)).lower()
    if name.endswith(".csv"):
        return pd.read_csv(file)
    if name.endswith(".xlsx"):
        return pd.read_excel(file, engine="openpyxl")
    raise ValueError("Only CSV and XLSX imports are supported")


def detect_location_duplicate(db_path, row):
    external = str(row.get("external_registry_id") or "").strip()
    licence = str(row.get("dealer_license_number") or "").strip()
    with connection(db_path) as conn:
        locations = conn.execute("""SELECT l.*,e.legal_business_name,e.corporation_number
            FROM dealership_locations l JOIN legal_entities e ON e.entity_id=l.entity_id""").fetchall()
    for loc in locations:
        if external and external.lower() == str(loc["external_registry_id"] or "").lower():
            return dict(loc), "External registry ID"
        if licence and licence.lower() == str(loc["dealer_license_number"] or "").lower():
            return dict(loc), "Dealer licence number"
        corp = str(loc["corporation_number"] or "").lower()
        corp_input = str(row.get("corporation_number") or "").lower()
        address = str(loc["physical_street_address"] or "").strip().lower()
        if corp and corp_input and corp == corp_input and address == str(row.get("physical_street_address") or "").strip().lower():
            return dict(loc), "Corporation number and location"
    return None, None
