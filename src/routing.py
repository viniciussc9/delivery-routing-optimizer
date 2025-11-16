
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import List
from .models.package import Package, PackageStatus
from .structures.hash_table import HashTable

def miles_to_hours(miles: float, mph: float) -> float: return miles / mph
def add_hours(dt: datetime, hours: float) -> datetime: return dt + timedelta(hours=hours)

@dataclass
class Truck:
    truck_id: int
    start_time: time
    speed_mph: float
    capacity: int
    hub_index: int
    package_ids: List[int] = field(default_factory=list)
    mileage: float = 0.0
    route: List[int] = field(default_factory=list)

class Simulation:
    def __init__(self, addresses: List[str], distances: List[List[float]], packages: HashTable,
                 trucks: List[Truck], hub_index: int = 0, speed_mph: float = 18.0):
        self.addresses = addresses
        self.dist = distances
        self.packages = packages
        self.trucks = trucks
        self.hub = hub_index
        self.speed_mph = speed_mph
        # Assign truck_id to all packages right away (so UI shows truck numbers before delivery)
        for t in self.trucks:
            for pid in t.package_ids:
                pkg = self.packages.get(pid)
                if pkg:
                    pkg.truck_id = t.truck_id

        self.pkg9_fix_time = datetime.combine(date.today(), time(10,20))
        self._prepare_pkg9()

    def _prepare_pkg9(self):
        pkg9 = self.packages.get(9)
        if not pkg9: return
        pkg9.corrected_after = self.pkg9_fix_time
        idx = None
        for i, a in enumerate(self.addresses):
            al = str(a).lower().replace(',', '')
            if "410" in al and "state" in al and (" st" in al or "street" in al):
                idx = i; break
        pkg9.corrected_address_index = idx

    def plan_and_run(self):
        for truck in self.trucks: self._run_truck(truck)

    def _run_truck(self, truck: Truck):
        today = date.today()
        current_time = datetime.combine(today, truck.start_time)
        current_loc = self.hub
        truck.route = [self.hub]

        # mark left hub
        for pid in truck.package_ids:
            pkg = self.packages.get(pid)
            if pkg:
                pkg.left_hub_time = current_time
                pkg.truck_id = truck.truck_id
                if pkg.status in (PackageStatus.AT_HUB, PackageStatus.DELAYED):
                    pkg.status = PackageStatus.EN_ROUTE

        remaining = set(truck.package_ids)
        while remaining:
            # feasible: available by time and has a destination
            feasible = []
            for pid in remaining:
                pkg = self.packages.get(pid)
                if pkg and pkg.is_available_at(current_time):
                    dest = pkg.address_idx_at(current_time)
                    if dest is not None:
                        feasible.append((pid, dest))

            if not feasible:
                # wait until earliest unblock
                if current_time.time() < time(9,5):
                    current_time = datetime.combine(today, time(9,5))
                elif current_time.time() < time(10,20):
                    current_time = datetime.combine(today, time(10,20))
                else:
                    break
                continue

            # nearest neighbor selection by address (group deliveries together)
            best_dest, best_dist = None, 10**9
            for _, dest in feasible:
                d = self.dist[current_loc][dest]
                if 0 <= d < best_dist:
                    best_dist = d; best_dest = dest

            # travel to best_dest
            travel_hours = best_dist / truck.speed_mph
            current_time += timedelta(hours=travel_hours)
            truck.mileage += best_dist
            current_loc = best_dest
            if truck.route[-1] != current_loc: truck.route.append(current_loc)

            # deliver ALL packages for this address in one stop
            to_deliver = [pid for pid in list(remaining)
                          if self.packages.get(pid) and self.packages.get(pid).address_idx_at(current_time)==current_loc]
            for pid in to_deliver:
                pkg = self.packages.get(pid)
                pkg.delivered_time = current_time
                pkg.status = PackageStatus.DELIVERED
                remaining.remove(pid)

        # return to hub
        back = self.dist[current_loc][self.hub]
        truck.mileage += back
        if truck.route[-1] != self.hub:
            truck.route.append(self.hub)

    def package_status_at(self, pkg: Package, t: datetime) -> str:
        if pkg.delivered_time and t >= pkg.delivered_time:
            return f"DELIVERED at {pkg.delivered_time.time().strftime('%H:%M')}"
        if pkg.left_hub_time and t >= pkg.left_hub_time:
            if "9:05" in pkg.notes.replace(" ", "") and t.time() < time(9,5):
                return "DELAYED"
            return "EN_ROUTE"
        if "9:05" in pkg.notes.replace(" ", "") and t.time() < time(9,5):
            return "DELAYED"
        return "AT_HUB"

    def _clean_addr_text(self, s: str) -> str:

        """If the address string contains multiple lines (e.g., 'Location Name\\n123 Main St'),
        return the line that looks like a street address.
        """
        parts = [p.strip() for p in str(s).splitlines() if p.strip()]
        for p in parts:
            if any(ch.isdigit() for ch in p):
                return p
        # Fallback: join everything on one line
        return " ".join(parts)

    def _display_address_for(self, pkg: Package, t: datetime) -> str:
        """
        UI-only address display:
         Before correction time: don't show a specific (wrong or right) street address.
         At/after correction time: show the corrected address text if we have its index.
        """
        # BEFORE correction time: neutral placeholder
        if pkg.corrected_after is not None and t < pkg.corrected_after:
            return "Address pending correction at 10:20"

        # AFTER correction time: show the corrected street line only
        if pkg.corrected_after is not None and t >= pkg.corrected_after and pkg.corrected_address_index is not None:
            raw = self.addresses[pkg.corrected_address_index]
            return self._clean_addr_text(raw)

        # Normal case for other packages
        return pkg.address

    def _format_full_address(self, pkg: Package, t: datetime) -> str:
        """
        Show a single, final address string for the UI:
         Package #9 BEFORE 10:20 -> 'Address pending correction at 10:20'
         Package #9 AT/AFTER 10:20 -> corrected street + 'Salt Lake City, UT 84111'
         All other packages -> 'address, city, UT zip'
        """
        # Special handling for #9
        if pkg.package_id == 9 and pkg.corrected_after is not None:
            if t < pkg.corrected_after:
                return "Address pending correction at 10:20"
            # After correction time, show the corrected full address
            if pkg.corrected_address_index is not None:
                raw = self.addresses[pkg.corrected_address_index]
                # Some rows have two lines ("Place name\n410 S State St"). Keep only the street line.
                parts = [p.strip() for p in str(raw).splitlines() if p.strip()]
                street = next((p for p in parts if any(ch.isdigit() for ch in p)), parts[0] if parts else str(raw).strip())
                return f"{street}, Salt Lake City, UT 84111"

        # All other packages: always show the full known address
        return f"{pkg.address}, {pkg.city}, UT {pkg.zipcode}"

    def print_all_packages_at(self, query_time: datetime):
        print(f"\nPackage statuses at {query_time.time().strftime('%H:%M')}:")
        for pid, pkg in sorted(self.packages.items(), key=lambda kv: kv[0]):
            status = self.package_status_at(pkg, query_time)
            addr = self._format_full_address(pkg, query_time)
            print(
                f'Truck {pkg.truck_id if pkg.truck_id is not None else "-"} | '
                f'#{pid:02d} | {addr} | '
                f'deadline={pkg.deadline_str} | weight={pkg.weight_kg} | status={status}'
            )

    def print_package_at(self, package_id: int, query_time: datetime):
        pkg = self.packages.get(package_id)
        if not pkg:
            print(f"Package {package_id} not found.")
            return
        status = self.package_status_at(pkg, query_time)
        print(f"Package {package_id}:")
        print(f"  Address: {self._format_full_address(pkg, query_time)}")
        print(f"  Deadline: {pkg.deadline_str}")
        print(f"  Weight: {pkg.weight_kg}")
        print(f"  Truck: {pkg.truck_id if pkg.truck_id is not None else '-'}")
        print(f"  Status at {query_time.time().strftime('%H:%M')}: {status}")

    def print_total_mileage(self):
        total = sum(t.mileage for t in self.trucks)
        print("\nTruck mileage:")
        for t in self.trucks:
            print(f"  Truck {t.truck_id}: {t.mileage:.2f} miles")
        print(f"TOTAL: {total:.2f} miles")
