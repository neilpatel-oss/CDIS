from cdis.database import connection
from cdis.models import UTC


def decide_change(db_path, change_id, decision, note=""):
    if decision not in ("Approved", "Rejected", "Investigate"):
        raise ValueError("Invalid decision")
    status = "Investigate" if decision == "Investigate" else decision
    with connection(db_path) as conn:
        change = conn.execute("SELECT * FROM change_log WHERE change_id=?", (change_id,)).fetchone()
        if not change:
            raise ValueError("Change not found")
        now = UTC()
        conn.execute("""UPDATE change_log SET review_status=?,reviewer_note=?,date_reviewed=?,decision=? WHERE change_id=?""",
                     (status, note, now, decision, change_id))
        if decision == "Approved":
            field_map = {
                "physical_street_address": "physical_street_address",
                "dealership_location_name": "dealership_location_name",
                "dealer_license_status": "dealer_license_status"
            }
            if change["field_changed"] in field_map:
                conn.execute(f"UPDATE dealership_locations SET {field_map[change['field_changed']]}=?,date_last_updated=? WHERE location_id=?",
                             (change["proposed_value"], now, change["location_id"]))
            elif change["field_changed"] == "corporate_status":
                conn.execute("UPDATE legal_entities SET corporate_status=?,corporate_status_last_verified=?,date_last_updated=? WHERE entity_id=?",
                             (change["proposed_value"], now, now, change["entity_id"]))
        conn.execute("""INSERT INTO audit_history(location_id,entity_id,action_type,field_name,previous_value,new_value,source,action_date,reviewer)
            VALUES(?,?,?,?,?,?,?,?,?)""", (change["location_id"],change["entity_id"],f"Change {decision.lower()}",
            change["field_changed"],change["previous_value"],change["proposed_value"],change["source"],now,"Local reviewer"))
        conn.commit()
