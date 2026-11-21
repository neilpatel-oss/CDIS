from datetime import datetime
UTC = lambda: datetime.utcnow().isoformat(timespec="seconds")

PROVINCES = ["AB","BC","MB","NB","NL","NS","NT","NU","ON","PE","QC","SK","YT"]
CORPORATE_STATUSES = ["Active","Inactive","Dissolved","Amalgamated","Unknown"]
LICENSE_STATUSES = ["Active","Suspended","Cancelled","Expired","Unknown"]
MONITORING_CATEGORIES = ["Current","Potential","Closed"]
FINANCING_TYPES = ["Floor-plan financing","Operating credit","General secured lending","Other financing","Unknown"]
CONFIDENCE_LEVELS = ["Confirmed","Probable","Unverified"]
