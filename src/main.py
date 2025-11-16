# Vinicius Da Silva Cruz
# Student ID: 011739633
# C950 Task 2 — WGUPS Routing Program

from src.data_loader import DataLoader
from src.routing import Simulation, Truck
from src.models.package import PackageStatus
from datetime import time

SPEED_MPH = 18.0
TRUCK_CAPACITY = 16
HUB_INDEX = 0

DELAYED_UNTIL_905 = {32, 25, 28, 6}

TRUCK_LOADS = {
    1: [1, 13, 14, 15, 19, 20, 29, 30, 31, 34, 37, 40, 21, 16],
    2: [3, 18, 36, 38, 2, 4, 5, 7, 8, 10, 11, 12, 17, 22, 23, 24],
    3: [6, 25, 26, 27, 28, 32, 33, 35, 39, 9]
}

TRUCK_START_TIMES = {
    1: time(8, 0),
    2: time(8, 0),
    3: time(9, 5)
}

def main():
    loader = DataLoader()
    addresses, dist_matrix = loader.load_distances()
    packages_table = loader.load_packages(addresses)

    # mark delayed
    for pid in DELAYED_UNTIL_905:
        pkg = packages_table.get(pid)
        if pkg: pkg.status = PackageStatus.DELAYED

    trucks = []
    for tid, pkg_ids in TRUCK_LOADS.items():
        trucks.append(Truck(
            truck_id=tid,
            start_time=TRUCK_START_TIMES[tid],
            speed_mph=SPEED_MPH,
            capacity=TRUCK_CAPACITY,
            hub_index=HUB_INDEX,
            package_ids=list(pkg_ids)
        ))

    sim = Simulation(addresses, dist_matrix, packages_table, trucks, hub_index=HUB_INDEX, speed_mph=SPEED_MPH)
    sim.plan_and_run()

    print("\nWGUPS Routing — Menu")
    print("[1] All package statuses at time (e.g., 09:10)")
    print("[2] Lookup a package by ID at time")
    print("[3] Total mileage")
    print("[4] Exit")

    while True:
        c = input("\nSelect: ").strip()
        if c == '1':
            t = input("Enter time (e.g., 09:10 or 10:43): ").strip()
            sim.print_all_packages_at(DataLoader.parse_time_today(t))
        elif c == '2':
            pid = int(input("Package ID: ").strip())
            t = input("Enter time: ").strip()
            sim.print_package_at(pid, DataLoader.parse_time_today(t))
        elif c == '3':
            sim.print_total_mileage()
        elif c == '4':
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
