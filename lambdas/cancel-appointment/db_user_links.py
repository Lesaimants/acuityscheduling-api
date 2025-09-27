import os
import time
from typing import Optional, Dict, Any

from db_repository import DBRepository


class DBUserLinks(DBRepository):
    def __init__(self):
        super(DBUserLinks, self).__init__(os.environ["USER_LINKS_TABLE"])

    def upsert_profile(self, customer_id: str, data: dict) -> dict:
        """Create or update profile item. Ensures timestamps and fixed keys.
        Expected optional attributes include: email, acuityClientId, shopDomain,
        firstName, lastName, phone, createdAt, updatedAt.
        """
        now_iso = int(time.time() * 1000)
        item = {
            "customerId": str(customer_id),
            "profile": "les-aimants",
        }
        # Merge provided data without None values
        for k, v in (data or {}).items():
            if v is not None:
                item[k] = v
        # Timestamps
        if not item.get("createdAt"):
            item["createdAt"] = now_iso
        item["updatedAt"] = now_iso
        # Save performs a put (upsert)
        self.save(item)
        return item
