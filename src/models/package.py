
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, time

# Enum-like constants for tracking package delivery state
class PackageStatus:
    AT_HUB   = "AT_HUB"
    DELAYED  = "DELAYED"
    EN_ROUTE = "EN_ROUTE"
    DELIVERED= "DELIVERED"

# Stores all package attributes and tracking information
# Used as value in the hash table
@dataclass
class Package:
    package_id: int
    address: str
    city: str
    state: str
    zipcode: str
    deadline_str: str
    weight_kg: str
    notes: str
    address_index: int | None = None

    truck_id: int | None = None

    # Current status of the package. Default is "AT_HUB".
    # Changes to DELAYED, EN_ROUTE, DELIVERED as simulation runs.
    status: str = field(default=PackageStatus.AT_HUB)
    # Time the package actually left the hub (when truck departed with it).
    # Filled in when truck departs.
    left_hub_time: datetime | None = None
    # Time the package was delivered to its address.
    # Filled in when delivery occurs.
    delivered_time: datetime | None = None

    # Time when a wrong address is officially corrected.
    # Before this, the package cannot be delivered.
    corrected_after: datetime | None = None
    # The corrected index (position in distance matrix) to use after correction time.
    # Ensures the package gets routed to the right place.
    corrected_address_index: int | None = None

    truck_id: int | None = None

    def deadline_time(self) -> time | None:
        s = self.deadline_str.strip().upper()
        if s in ("EOD", "END OF DAY"):
            return None
        try:
            return datetime.strptime(s, "%I:%M:%S").time()
        except Exception:
            try:
                return datetime.strptime(s, "%I:%M %p").time()
            except Exception:
                return None

    def is_available_at(self, t: datetime) -> bool:
        if "9:05" in self.notes.replace(" ", "") and t.time().hour < 9 or (t.time().hour==9 and t.time().minute < 5):
            return False
        if self.status == PackageStatus.DELAYED and (t.time().hour < 9 or (t.time().hour==9 and t.time().minute<5)):
            return False
        return True

    def address_idx_at(self, t: datetime) -> int | None:
        """Return the deliverable address index for time t.
        If a correction time is set, package is NOT deliverable before that time.
        After that time, use the corrected index if provided; otherwise use original.
        """
        if self.corrected_after is not None:
            if t < self.corrected_after:
                return None
            if self.corrected_address_index is not None:
                return self.corrected_address_index
        return self.address_index
