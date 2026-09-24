"""
=============================================================
  FastBox Delivery System Simulator
  Assignment: Mystery Delivery System
  Company: FastBox (Fictional Logistics Simulator)
=============================================================

Technology Stack:
  - Language  : Python 3.8+
  - Libraries : json, math, csv, random, os, sys (all built-in)
  - No external dependencies required

Project Structure:
  main.py         — This file: complete simulator
  data.json       — Default input (assignment sample data)
  report.json     — Output report (auto-generated)
  top_performer.csv — Bonus: CSV export of best agent

Author  : FastBox Simulator
Version : 1.0.0
=============================================================
"""

import json
import math
import csv
import random
import os
import sys

# -----------------------------------------------------------
#  SECTION 1 — UTILITY
# ___________________________________________________________

def euclidean_distance(point_a, point_b):
    
    return math.sqrt(
        (point_b[0] - point_a[0]) ** 2 +
        (point_b[1] - point_a[1]) ** 2
    )


# -----------------------------------------------------------
#  SECTION 2 — JSON PARSING  (Task 1)
# -----------------------------------------------------------

def load_data(filepath):
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"[ERROR] Input file not found: '{filepath}'")

    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"[ERROR] Invalid JSON in '{filepath}': {e}")

    return data


def parse_input(data):
    warehouses = {}
    agents = {}
    packages = []

    # ── Parse warehouses ──────────────────────────────────
    raw_warehouses = data.get('warehouses', {})

    if isinstance(raw_warehouses, dict):
        # Format B: {"W1": [x, y], ...}
        warehouses = {wid: list(loc) for wid, loc in raw_warehouses.items()}

    elif isinstance(raw_warehouses, list):
        # Format A: [{"id": "W1", "location": [x, y]}, ...]
        for w in raw_warehouses:
            warehouses[w['id']] = list(w['location'])

    # ── Parse agents ──────────────────────────────────────
    raw_agents = data.get('agents', {})

    if isinstance(raw_agents, dict):
        # Format B: {"A1": [x, y], ...}
        agents = {aid: list(loc) for aid, loc in raw_agents.items()}

    elif isinstance(raw_agents, list):
        # Format A: [{"id": "A1", "location": [x, y]}, ...]
        for a in raw_agents:
            agents[a['id']] = list(a['location'])

    # ── Parse packages ────────────────────────────────────
    for p in data.get('packages', []):
        pkg_id     = p.get('id')
        # Accept both 'warehouse' and 'warehouse_id' keys
        warehouse  = p.get('warehouse') or p.get('warehouse_id')
        destination = list(p.get('destination', []))

        # Skip packages with missing required fields
        if not pkg_id or not warehouse or len(destination) < 2:
            print(f"  [WARNING] Skipping malformed package entry: {p}")
            continue

        # Validate warehouse reference
        if warehouse not in warehouses:
            print(f"  [WARNING] Package {pkg_id} references unknown warehouse '{warehouse}', skipping.")
            continue

        packages.append({
            'id': pkg_id,
            'warehouse': warehouse,
            'destination': destination
        })

    return warehouses, agents, packages


# -----------------------------------------------------------
#  SECTION 3 — PACKAGE ASSIGNMENT  (Task 2)
# -----------------------------------------------------------

def assign_packages(packages, agents, warehouses):
    
    # Create empty assignment buckets for every agent
    assignments = {agent_id: [] for agent_id in agents}

    for pkg in packages:
        warehouse_loc = warehouses[pkg['warehouse']]

        nearest_agent = None
        min_distance = float('inf')

        # Compare every agent's distance to this package's warehouse
        for agent_id, agent_loc in agents.items():
            dist = euclidean_distance(agent_loc, warehouse_loc)
            if dist < min_distance:
                min_distance = dist
                nearest_agent = agent_id

        # Assign this package to the closest agent
        assignments[nearest_agent].append(pkg)

        print(f"    {pkg['id']}  warehouse={pkg['warehouse']}{warehouse_loc}"
              f"  →  {nearest_agent}  (dist={min_distance:.2f})")

    return assignments


# -----------------------------------------------------------
#  SECTION 4 — DELIVERY SIMULATION  (Task 3)
# -----------------------------------------------------------

def simulate_deliveries(assignments, agents, warehouses, random_delays=False):
    
    simulation_result = {}

    for agent_id in sorted(assignments.keys()):
        packages = assignments[agent_id]

        # Agent starts at their initial position
        current_pos = list(agents[agent_id])
        total_distance = 0.0
        delivered_package_ids = []
        route_steps = []          # Detailed route log for ASCII map (Bonus)
        delay_log = {}            # {package_id: delay_minutes} for Bonus

        print(f"\n    Agent {agent_id}  start={current_pos}  packages={len(packages)}")

        for pkg in packages:
            warehouse_loc = list(warehouses[pkg['warehouse']])
            destination   = list(pkg['destination'])

            # Leg 1: current position → warehouse  (travel to pick up)
            leg1 = euclidean_distance(current_pos, warehouse_loc)

            # Leg 2: warehouse → destination  (delivery trip)
            leg2 = euclidean_distance(warehouse_loc, destination)

            trip_total = leg1 + leg2
            total_distance += trip_total

            # ── Bonus: Random delivery delay ────────────────
            delay_minutes = 0.0
            if random_delays:
                delay_minutes = round(random.uniform(0.0, 30.0), 1)
                delay_log[pkg['id']] = delay_minutes

            # Store step for ASCII visualization
            route_steps.append({
                'package'     : pkg['id'],
                'from'        : current_pos[:],       # snapshot before move
                'warehouse'   : warehouse_loc[:],
                'destination' : destination[:],
                'leg1'        : round(leg1, 4),
                'leg2'        : round(leg2, 4),
                'trip'        : round(trip_total, 4),
                'delay_min'   : delay_minutes,
            })

            delay_str = f"  delay={delay_minutes}min" if random_delays else ""
            print(f"      {pkg['id']}:  {current_pos} → W{warehouse_loc}"
                  f" → {destination}  dist={trip_total:.2f}{delay_str}")

            # Move agent to the delivery destination
            current_pos = destination[:]
            delivered_package_ids.append(pkg['id'])

        # ── Per-agent summary ────────────────────────────
        n = len(delivered_package_ids)

        # Efficiency = average distance per package (lower is better)
        efficiency = round(total_distance / n, 2) if n > 0 else 0.0

        simulation_result[agent_id] = {
            'packages_delivered'   : n,
            'total_distance'       : round(total_distance, 2),
            'efficiency'           : efficiency,
            '_delivered_ids'       : delivered_package_ids,  # internal
            '_route'               : route_steps,            # internal (for ASCII)
        }

        if random_delays and delay_log:
            simulation_result[agent_id]['delays'] = delay_log

    # ── Determine Best Agent ─────────────────────────────
    # Best agent = lowest efficiency score (least distance per package)
    # Only agents who delivered at least 1 package are considered
    active_agents = {
        aid: res
        for aid, res in simulation_result.items()
        if res['packages_delivered'] > 0
    }

    if active_agents:
        best_agent = min(active_agents, key=lambda a: active_agents[a]['efficiency'])
        simulation_result['best_agent'] = best_agent
    else:
        simulation_result['best_agent'] = None

    return simulation_result


# -----------------------------------------------------------
#  SECTION 5 — REPORT GENERATION & SAVING  (Task 4 & 5)
# -----------------------------------------------------------

def build_report(simulation_result):
    
    report = {}

    for agent_id, data in simulation_result.items():
        if agent_id == 'best_agent':
            continue  # handled separately below

        agent_report = {
            'packages_delivered': data['packages_delivered'],
            'total_distance'    : data['total_distance'],
            'efficiency'        : data['efficiency'],
        }

        # Include delay info if random delays were used (Bonus)
        if 'delays' in data:
            agent_report['delays'] = data['delays']

        report[agent_id] = agent_report

    report['best_agent'] = simulation_result.get('best_agent')
    return report


def save_report(report, filepath='report.json'):
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"\n  ✔  Report saved → {filepath}")


# -----------------------------------------------------------
#  BONUS 1 — RANDOM DELIVERY DELAYS
#  (Handled inline in simulate_deliveries via random_delays=True)
# -----------------------------------------------------------
# Random delays of 0–30 minutes per package are appended to
# each agent's report entry under the key "delays".


# -----------------------------------------------------------
#  BONUS 2 — ASCII ROUTE VISUALIZATION
# -----------------------------------------------------------

def draw_ascii_map(warehouses, agents, simulation_result, grid_w=50, grid_h=30):
    

    # ── Find coordinate bounds for scaling ──────────────
    all_x, all_y = [], []
    for loc in warehouses.values():
        all_x.append(loc[0]); all_y.append(loc[1])
    for loc in agents.values():
        all_x.append(loc[0]); all_y.append(loc[1])
    for aid, data in simulation_result.items():
        if aid == 'best_agent':
            continue
        for step in data.get('_route', []):
            all_x.append(step['destination'][0])
            all_y.append(step['destination'][1])

    min_x, max_x = min(all_x, default=0), max(all_x, default=100)
    min_y, max_y = min(all_y, default=0), max(all_y, default=100)

    # Padding to avoid clipping
    range_x = max(max_x - min_x, 1)
    range_y = max(max_y - min_y, 1)

    def to_grid(x, y):
        """Map real coordinates → grid cell (col, row)."""
        col = int((x - min_x) / range_x * (grid_w - 1))
        row = int((y - min_y) / range_y * (grid_h - 1))
        col = max(0, min(col, grid_w - 1))
        row = max(0, min(row, grid_h - 1))
        return col, row

    def draw_line(grid, x0, y0, x1, y1, char):
        """Bresenham's line algorithm to draw a path on the grid."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            # Only overwrite empty cells (preserve landmark markers)
            if grid[y0][x0] == '·':
                grid[y0][x0] = char
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy; x0 += sx
            if e2 < dx:
                err += dx; y0 += sy

    # ── Build empty grid ─────────────────────────────────
    grid = [['·'] * grid_w for _ in range(grid_h)]

    # Route characters, one per agent
    route_chars = ['-', '~', '+', '=', '#']

    # Draw routes first (so landmarks can overwrite them)
    for i, (aid, data) in enumerate(sorted(simulation_result.items())):
        if aid == 'best_agent':
            continue
        char = route_chars[i % len(route_chars)]
        for step in data.get('_route', []):
            # Draw agent-start → warehouse
            ac, ar = to_grid(*step['from'])
            wc, wr = to_grid(*step['warehouse'])
            draw_line(grid, ac, ar, wc, wr, char)
            # Draw warehouse → destination
            dc, dr = to_grid(*step['destination'])
            draw_line(grid, wc, wr, dc, dr, char)

    # Mark destinations (*)
    for aid, data in simulation_result.items():
        if aid == 'best_agent':
            continue
        for step in data.get('_route', []):
            dc, dr = to_grid(*step['destination'])
            if grid[dr][dc] not in ('W', 'A'):
                grid[dr][dc] = '*'

    # Mark warehouses (W) — overwrite routes
    for wid, loc in warehouses.items():
        c, r = to_grid(*loc)
        grid[r][c] = 'W'

    # Mark agent start positions (A) — overwrite routes
    for aid, loc in agents.items():
        c, r = to_grid(*loc)
        grid[r][c] = 'A'

    # ── Render ───────────────────────────────────────────
    print(f"\n  ╔{'═' * grid_w}╗  (Y↑ flipped, origin bottom-left)")
    for row in reversed(grid):          # Flip Y so y=0 is at bottom
        print("  ║" + "".join(row) + "║")
    print(f"  ╚{'═' * grid_w}╝")
    print("  Legend:  A=Agent start   W=Warehouse   *=Destination   ·=Empty")
    print("  Routes : - ~ + = # (one per agent)")


# -----------------------------------------------------------
#  BONUS 3 — NEW AGENT JOINING MID-DAY
# -----------------------------------------------------------

def add_midday_agent(new_id, new_location, undelivered_packages,
                     all_agents, all_warehouses):
   
    print(f"\n  [MID-DAY JOIN] Agent '{new_id}' arrived at {new_location}")

    # Add new agent to the pool
    all_agents[new_id] = list(new_location)

    if not undelivered_packages:
        print("  No remaining packages to re-assign.")
        return {new_id: []}

    # Re-assign undelivered packages considering the new agent
    new_assignments = assign_packages(undelivered_packages, all_agents, all_warehouses)

    # Report what the new agent got
    new_agent_pkgs = new_assignments.get(new_id, [])
    print(f"  '{new_id}' received {len(new_agent_pkgs)} package(s): "
          f"{[p['id'] for p in new_agent_pkgs]}")

    return new_assignments


# -----------------------------------------------------------
#  BONUS 4 — EXPORT TOP PERFORMER TO CSV
# -----------------------------------------------------------

def export_top_performer_csv(report, filepath='top_performer.csv'):
    
    best_id = report.get('best_agent')
    if not best_id:
        print("  [CSV] No best agent found; CSV not created.")
        return

    best_data = report.get(best_id, {})

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Header row
        writer.writerow(['Agent ID', 'Packages Delivered',
                         'Total Distance', 'Efficiency'])
        # Data row
        writer.writerow([
            best_id,
            best_data.get('packages_delivered', 0),
            best_data.get('total_distance', 0.0),
            best_data.get('efficiency', 0.0),
        ])

    print(f"  ✔  Top performer CSV saved → {filepath}")


# -----------------------------------------------------------
#  SECTION 6 — PRINT SUMMARY
# -----------------------------------------------------------

def print_summary(report, total_packages):
    """Print a human-readable console summary of the simulation."""
    print("\n" + "═" * 60)
    print("  DELIVERY SUMMARY")
    print("═" * 60)

    delivered_count = 0
    for agent_id in sorted(report.keys()):
        if agent_id == 'best_agent':
            continue
        d = report[agent_id]
        delivered_count += d['packages_delivered']
        star = " ← BEST" if agent_id == report.get('best_agent') else ""
        print(f"  {agent_id}:  {d['packages_delivered']} pkg(s)"
              f"  |  distance={d['total_distance']:.2f}"
              f"  |  efficiency={d['efficiency']:.2f}{star}")

    print(f"\n  Total packages: {total_packages}")
    print(f"  Delivered     : {delivered_count}")
    print(f"  Best Agent    : {report.get('best_agent', 'N/A')}")

    if delivered_count != total_packages:
        print(f"\n  [WARNING] Mismatch: {total_packages - delivered_count}"
              f" package(s) not accounted for!")
    else:
        print("  [OK] All packages delivered ✔")
    print("═" * 60)


# -----------------------------------------------------------
#  MAIN ENTRY POINT
# -----------------------------------------------------------

def run(input_file='data.json',
        report_file='report.json',
        csv_file='top_performer.csv',
        enable_delays=False,
        enable_ascii=True,
        enable_csv=True,
        midday_agent=None):
    
    print("\n" + "═" * 60)
    print("  🚚  FastBox Delivery System Simulator")
    print("═" * 60)

    # ── Step 1: Load & Parse ─────────────────────────────
    print(f"\n[1] Loading input: {input_file}")
    raw_data = load_data(input_file)
    warehouses, agents, packages = parse_input(raw_data)

    print(f"  Warehouses : {len(warehouses)}  {list(warehouses.keys())}")
    print(f"  Agents     : {len(agents)}  {list(agents.keys())}")
    print(f"  Packages   : {len(packages)}  {[p['id'] for p in packages]}")

    if not packages:
        print("  [ERROR] No valid packages found. Exiting.")
        return {}

    # ── Step 2: Assign Packages ──────────────────────────
    print("\n[2] Assigning packages to nearest agents...")
    assignments = assign_packages(packages, agents, warehouses)

    # Show assignment summary
    print("\n  Assignment summary:")
    for aid in sorted(assignments.keys()):
        ids = [p['id'] for p in assignments[aid]]
        print(f"    {aid}: {ids if ids else '(none)'}")

    # ── Bonus: Mid-day Agent ─────────────────────────────
    if midday_agent:
        # Pretend first half of packages have been handled, new agent joins
        # For demo purposes, we inject the new agent and re-run assignment
        # on the second half of packages
        half = len(packages) // 2
        remaining = packages[half:]
        print(f"\n[BONUS] Mid-day agent joining — reassigning {len(remaining)} packages...")
        new_assignments = add_midday_agent(
            new_id=midday_agent['id'],
            new_location=midday_agent['location'],
            undelivered_packages=remaining,
            all_agents=agents,
            all_warehouses=warehouses
        )
        # Merge new_assignments into existing assignments
        for aid, pkgs in new_assignments.items():
            if aid in assignments:
                assignments[aid].extend(pkgs)
            else:
                assignments[aid] = pkgs

    # ── Step 3: Simulate ─────────────────────────────────
    print("\n[3] Simulating deliveries...")
    if enable_delays:
        print("  [BONUS] Random delays (0–30 min) enabled")
    simulation_result = simulate_deliveries(
        assignments, agents, warehouses, random_delays=enable_delays
    )

    # ── Step 4 & 5: Build Report & Save ──────────────────
    print("\n[4] Building report...")
    report = build_report(simulation_result)
    print(json.dumps(report, indent=2))
    save_report(report, report_file)

    # ── Print Summary ─────────────────────────────────────
    print_summary(report, len(packages))

    # ── Bonus: ASCII Map ─────────────────────────────────
    if enable_ascii:
        print("\n[BONUS] ASCII Route Map:")
        draw_ascii_map(warehouses, agents, simulation_result)

    # ── Bonus: CSV Export ────────────────────────────────
    if enable_csv:
        print("\n[BONUS] Exporting top performer to CSV...")
        export_top_performer_csv(report, csv_file)

    return report


# -----------------------------------------------------------
#  COMMAND-LINE USAGE
# -----------------------------------------------------------

if __name__ == '__main__':
    

    # Choose input file from command line or default to data.json
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data.json'

    run(
        input_file    = input_file,
        report_file   = 'report.json',
        csv_file      = 'top_performer.csv',
        enable_delays = True,    # Bonus: random delays
        enable_ascii  = True,    # Bonus: ASCII map
        enable_csv    = True,    # Bonus: CSV export

        # Bonus: uncomment to simulate a mid-day agent joining
        # midday_agent = {"id": "A_NEW", "location": [50, 50]},
    )
