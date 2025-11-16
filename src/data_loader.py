
from __future__ import annotations
import csv
from datetime import datetime, date
from pathlib import Path
from .models.package import Package
from .structures.hash_table import HashTable

import re

def _norm_addr(s: str) -> str:
    s = s.lower()
    s = s.replace(',', ' ')
    s = re.sub(r'\s+', ' ', s)
    # common abbreviations seen in WGUPS data
    s = s.replace(' station ', ' sta ')
    s = s.replace(' street ', ' st ')
    s = s.replace(' avenue ', ' ave ')
    s = s.replace(' boulevard ', ' blvd ')
    s = s.strip()
    return s

# All data files (CSV) live here. Keeping this as a constant makes the loader portable.
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

class DataLoader:
    @staticmethod
    def parse_time_today(hhmm: str) -> datetime:
        hhmm = hhmm.strip().lower()
        today = date.today()
        for fmt in ("%H:%M","%I:%M%p","%I:%M %p"):
            try:
                dt = datetime.strptime(hhmm.replace(" ",""), fmt)
                return datetime.combine(today, dt.time())
            except ValueError:
                continue
        raise ValueError("Time format should be HH:MM or H:MM AM/PM")

    # Reads the distance CSV and builds a full symmetric distance matrix
    # by locating the HUB row, collecting all addresses, and filling values
    # from the lower-triangular table into an NxN matrix.
    def load_distances(self):
        # Loads the raw distance CSV into a list of rows
        path = DATA_DIR / "distances_raw.csv"
        rows = []
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for r in reader:
                rows.append(r)

        # Find row like: [<address>, " HUB", "0", ...]
        start_row = None
        for i, r in enumerate(rows):
            c0 = (r[0] if len(r)>0 else "").strip()
            c1 = (r[1] if len(r)>1 else "").strip().upper()
            c2 = (r[2] if len(r)>2 else "").strip()
            if c0 and c1 == "HUB" and c2 in ("0","0.0"):
                start_row = i
                break
        if start_row is None:
            raise ValueError("Could not locate start of distance matrix")

        # addresses until blank c0
        addresses = []
        idx = start_row
        while idx < len(rows):
            c0 = (rows[idx][0] if len(rows[idx])>0 else "").strip()
            if not c0:
                break
            addresses.append(c0)
            idx += 1
        n = len(addresses)

        # lower triangle begins at col2 (index 2)
        mat = [[0.0]*n for _ in range(n)]
        for i in range(n):
            r = rows[start_row + i]
            for j in range(i+1):
                col = 2 + j
                if col >= len(r): continue
                cell = r[col].strip()
                try:
                    v = float(cell)
                except Exception:
                    continue
                mat[i][j] = v
                mat[j][i] = v
        return addresses, mat

    # Reads package data from CSV, creates Package objects with all fields,
    # matches each address to the distance matrix index, and inserts into
    # the custom HashTable keyed by package ID.
    def load_packages(self, addresses):
        path = DATA_DIR / "packages.csv"
        table = HashTable(initial_capacity=128)
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = int(row.get('Package ID'))
                address = (row.get('Address') or '').strip()
                city = (row.get('City') or '').strip()
                state = (row.get('State') or '').strip()
                zipcode = str(row.get('Zip') or '').strip()
                deadline = (row.get('Deadline') or 'EOD').strip()
                weight = (row.get('Weight') or '0').strip()
                notes = (row.get('Notes') or '').strip()

                addr_idx = None
                a_low = _norm_addr(address)
                for i, a in enumerate(addresses):
                    al = _norm_addr(str(a))
                    if a_low in al or al in a_low:
                        addr_idx = i
                        break

                pkg = Package(pid, address, city, state, zipcode, deadline, weight, notes, addr_idx)
                table.put(pid, pkg)
        return table
