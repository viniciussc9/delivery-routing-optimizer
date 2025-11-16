# Delivery Routing Optimizer

Python delivery routing optimizer for a local parcel service. The program loads ~40 packages, assigns them across multiple trucks, and computes efficient delivery routes under real-world constraints.

## What this project does

- Loads package data into a **custom hash table** (no Python dicts) for fast lookups by package ID.
- Reads distances between addresses from a distance table.
- Uses a **greedy routing heuristic** to:
  - Respect package **deadlines**  
  - Respect **truck capacity** limits  
  - Handle **special notes** (delayed address corrections, grouped deliveries, etc.)
  - Keep total mileage under a specified limit (e.g., \< 140 miles).

## Tech & concepts

- **Language:** Python 3  
- **Data structures:** custom hash table implementation  
- **Algorithms:** greedy / heuristic routing  
- **Other:** time simulation for truck departure and delivery timestamps

## How to run

1. Clone or download this repository.
2. Make sure you have **Python 3** installed.
3. From the project folder, run:

```bash
python main.py
