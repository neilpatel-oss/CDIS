import pandas as pd

ENTITIES = [
("Northstar Auto Group Ltd.","Northstar Motors","DEMO-ON-1001","ON","Active"),
("Prairie Pines Automotive Inc.","Prairie Pines Dealers","DEMO-AB-1002","AB","Active"),
("Pacific Lantern Cars Ltd.","Pacific Lantern","DEMO-BC-1003","BC","Active"),
("Atlas Harbour Motors Inc.","Atlas Harbour","DEMO-NL-1004","NL","Dissolved"),
("Maple Horizon Holdings Ltd.","Maple Horizon","DEMO-ALL-1005","ON","Active"),
("Boreal Transit Motors Inc.","Boreal Transit","DEMO-NT-1006","NT","Unknown"),
]

LOCATIONS = [
("Northstar Auto Group Ltd.","Northstar Toronto","123 Demonstration Ave","Toronto","ON","M1A 1A1","DL-DEMO-001","Active","Current","EX-DEMO-001","Northstar Toronto change demo"),
("Northstar Auto Group Ltd.","Northstar Ottawa","45 Fiction Road","Ottawa","ON","K1A 1A1","DL-DEMO-002","Suspended","Current","EX-DEMO-002",""),
("Prairie Pines Automotive Inc.","Prairie Pines Calgary","88 Sample Boulevard","Calgary","AB","T1A 1A1","DL-DEMO-003","Active","Current","EX-DEMO-003",""),
("Prairie Pines Automotive Inc.","Prairie Pines Edmonton","77 Example Crescent","Edmonton","AB","T2A 2A2","DL-DEMO-004","Unknown","Potential","EX-DEMO-004",""),
("Pacific Lantern Cars Ltd.","Pacific Lantern Vancouver","210 Imaginary Street","Vancouver","BC","V1A 1A1","DL-DEMO-005","Active","Current","EX-DEMO-005",""),
("Pacific Lantern Cars Ltd.","Pacific Lantern Victoria","61 Synthetic Way","Victoria","BC","V2A 2A2","DL-DEMO-006","Active","Potential","EX-DEMO-006",""),
("Atlas Harbour Motors Inc.","Atlas Harbour St. John's","12 Fictional Harbour Road","St. John's","NL","A1A 1A1","DL-DEMO-007","Cancelled","Closed","EX-DEMO-007",""),
("Maple Horizon Holdings Ltd.","Maple Horizon Winnipeg","300 Test Avenue","Winnipeg","MB","R1A 1A1","DL-DEMO-008","Active","Potential","EX-DEMO-008",""),
("Maple Horizon Holdings Ltd.","Maple Horizon Halifax","14 Mock Lane","Halifax","NS","B1A 1A1","DL-DEMO-009","Active","Potential","EX-DEMO-009",""),
("Maple Horizon Holdings Ltd.","Maple Horizon Moncton","22 Illustration Court","Moncton","NB","E1A 1A1","DL-DEMO-010","Suspended","Potential","EX-DEMO-010",""),
("Boreal Transit Motors Inc.","Boreal Yellowknife","9 Made-up Drive","Yellowknife","NT","X1A 1A1","DL-DEMO-011","Unknown","Potential","EX-DEMO-011",""),
]

rows=[]
for entity_name,loc,address,city,province,postal,license_num,license_status,category,external,note in LOCATIONS:
    entity=next(e for e in ENTITIES if e[0]==entity_name)
    if external=="EX-DEMO-001": address="456 Changed Demonstration Ave"
    rows.append({"legal_name":entity_name,"operating_trade_name":entity[1],"corporation_number":entity[2],"corporate_status":entity[4],"dealership_name":loc,"physical_address":address,"city":city,"province":province,"postal_code":postal,"license_number":license_num,"licence_status":license_status,"external_registry_id":external})

pd.DataFrame(rows).to_csv("data/demo_registry_snapshot.csv",index=False)
pd.DataFrame(columns=["legal_name","operating_trade_name","corporation_number","corporate_status","dealership_name","physical_address","city","province","postal_code","license_number","licence_status","external_registry_id"]).to_csv("data/import_template.csv",index=False)
pd.DataFrame([{k:v for k,v in zip(["legal_name","operating_trade_name","corporation_number","corporate_status","dealership_name","physical_address","city","province","postal_code","license_number","licence_status","external_registry_id"],r.values())} for r in rows]).to_csv("data/demo_dealers.csv",index=False)
