"""Synthetic demonstration data for CDIS."""
import csv
from pathlib import Path
from cdis.database import connection
from cdis.models import UTC

ENTITIES = [
("Northstar Auto Group Ltd.","Northstar Motors","DEMO-ON-1001","ON","Active"),
("Prairie Pines Automotive Inc.","Prairie Pines Dealers","DEMO-AB-1002","AB","Active"),
("Pacific Lantern Cars Ltd.","Pacific Lantern","DEMO-BC-1003","BC","Active"),
("Atlas Harbour Motors Inc.","Atlas Harbour","DEMO-NL-1004","NL","Dissolved"),
("Maple Horizon Holdings Ltd.","Maple Horizon","DEMO-ALL-1005","ON","Active"),
("Boreal Transit Motors Inc.","Boreal Transit","DEMO-NT-1006","NT","Unknown"),
]

LOCATIONS = [
("Northstar Auto Group Ltd.","Northstar Toronto","123 Demonstration Ave","Toronto","ON","M1A 1A1","DL-DEMO-001","Active","Current","EX-DEMO-001","Active","2026-10-15"),
("Northstar Auto Group Ltd.","Northstar Ottawa","45 Fiction Road","Ottawa","ON","K1A 1A1","DL-DEMO-002","Suspended","Current","EX-DEMO-002","Active","2026-09-20"),
("Prairie Pines Automotive Inc.","Prairie Pines Calgary","88 Sample Boulevard","Calgary","AB","T1A 1A1","DL-DEMO-003","Active","Current","EX-DEMO-003","Active","2026-10-01"),
("Prairie Pines Automotive Inc.","Prairie Pines Edmonton","77 Example Crescent","Edmonton","AB","T2A 2A2","DL-DEMO-004","Unknown","Potential","EX-DEMO-004","Unknown","2026-08-12"),
("Pacific Lantern Cars Ltd.","Pacific Lantern Vancouver","210 Imaginary Street","Vancouver","BC","V1A 1A1","DL-DEMO-005","Active","Current","EX-DEMO-005","Active","2026-11-01"),
("Pacific Lantern Cars Ltd.","Pacific Lantern Victoria","61 Synthetic Way","Victoria","BC","V2A 2A2","DL-DEMO-006","Active","Potential","EX-DEMO-006","Active","2026-10-20"),
("Atlas Harbour Motors Inc.","Atlas Harbour St. John's","12 Fictional Harbour Road","St. John's","NL","A1A 1A1","DL-DEMO-007","Cancelled","Closed","EX-DEMO-007","Dissolved","2026-07-02"),
("Maple Horizon Holdings Ltd.","Maple Horizon Winnipeg","300 Test Avenue","Winnipeg","MB","R1A 1A1","DL-DEMO-008","Active","Potential","EX-DEMO-008","Active","2026-10-18"),
("Maple Horizon Holdings Ltd.","Maple Horizon Halifax","14 Mock Lane","Halifax","NS","B1A 1A1","DL-DEMO-009","Active","Potential","EX-DEMO-009","Active","2026-09-30"),
("Maple Horizon Holdings Ltd.","Maple Horizon Moncton","22 Illustration Court","Moncton","NB","E1A 1A1","DL-DEMO-010","Suspended","Potential","EX-DEMO-010","Active","2026-09-15"),
("Boreal Transit Motors Inc.","Boreal Yellowknife","9 Made-up Drive","Yellowknife","NT","X1A 1A1","DL-DEMO-011","Unknown","Potential","EX-DEMO-011","Unknown","2026-06-01"),
]


def seed_demo_data(db_path=None):
    with connection(db_path) as conn:
        for name,trade,corp,prov,status in ENTITIES:
            if conn.execute("SELECT 1 FROM legal_entities WHERE corporation_number=?",(corp,)).fetchone():
                continue
            now=UTC()
            cur=conn.execute("""INSERT INTO legal_entities
              (legal_business_name,operating_trade_name,corporation_number,incorporation_jurisdiction,
               corporate_status,corporate_status_source,corporate_status_last_verified,date_created,date_last_updated,notes)
              VALUES(?,?,?,?,?,?,?,?,?,?)""",(name,trade,corp,prov,status,"Synthetic demonstration data","2026-11-01",now,now,"SYNTHETIC DEMONSTRATION DATA — not a real business"))
        for name,loc,address,city,province,postal,license_num,license_status,category,external,corp_status,last_verified in LOCATIONS:
            entity=conn.execute("SELECT entity_id FROM legal_entities WHERE legal_business_name=?",(name,)).fetchone()
            if not entity or conn.execute("SELECT 1 FROM dealership_locations WHERE external_registry_id=?",(external,)).fetchone():
                continue
            now=UTC()
            cur=conn.execute("""INSERT INTO dealership_locations
              (entity_id,dealership_location_name,physical_street_address,city,province_territory,postal_code,country,
               dealer_license_number,dealer_license_status,external_registry_id,source_name,source_record_date,last_verified_date,date_created,date_last_updated)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(entity[0],loc,address,city,province,postal,"Canada",license_num,license_status,external,"Synthetic demonstration dataset","2026-11-01",last_verified,now,now))
            lid=cur.lastrowid
            conn.execute("""INSERT INTO monitoring_records(location_id,monitoring_category,monitoring_active,reason_for_monitoring,date_added,date_last_updated,internal_notes)
              VALUES(?,?,?,?,?,?,?)""",(lid,category,1,"Synthetic demo portfolio record",now,now,"Fictional demonstration record"))
        conn.commit()
