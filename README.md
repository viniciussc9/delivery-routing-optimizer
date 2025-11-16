# Delivery Routing Optimizer

This is a small Python project where I built a custom delivery routing system for a fictional local parcel service.

The program takes a list of around 40 packages, three trucks, and a distance table, then:

- Loads all package and distance data
- Uses a custom hash table to store and look up package info
- Simulates three trucks driving around a city
- Delivers every package under a mileage cap while respecting constraints and deadlines

You can run the app from the command line, see the total mileage, and check the delivery status of any package at a specific time.

---

## Technical Overview

This project was built as part of a data structures and algorithms course and focuses on how the solution is structured internally, not just on getting the right answer.

### Core Features

- **Custom hash table** (no Python `dict` for core storage)  
  - Stores package data (address, deadline, city, ZIP, weight, status, delivery time)  
  - Supports insert and lookup by package ID in approximately O(1) average time  

- **Routing logic**  
  - Heuristic / greedy-style approach to building truck routes  
  - Handles multiple trucks with capacity limits (16 packages per truck)  
  - Respects special constraints (for example delayed address correction, grouped packages, time-dependent address fixes)  

- **Time simulation**  
  - Trucks start from the hub at 8:00 AM  
  - Travel times are computed from the distance table and the truck’s average speed  
  - Package status changes over time: `At Hub → En Route → Delivered @ HH:MM`  

- **Data structures and algorithms**  
  - Hash-based storage for package information  
  - List/array-based structures for distances and routes  
  - Self-adjusting and heuristic logic to keep total mileage low while meeting deadlines  

---

## Project Structure

```text
delivery-routing-optimizer/
├── data/
│   ├── distances_raw.csv       # Distance table between all locations
│   ├── distances_debug.csv     # Optional debug/cleaned distances
│   └── packages.csv            # Package list: addresses, deadlines, notes, etc.
└── src/
    ├── main.py                 # Entry point – runs the simulation / CLI
    ├── routing.py              # Core routing and truck logic
    ├── data_loader.py          # CSV loaders for package and distance data
    ├── models/
    │   └── package.py          # Package class (ID, address, deadline, status...)
    └── structures/
        └── hash_table.py       # Custom hash table implementation
