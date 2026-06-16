import json
import random
import os

# --- 1. CONFIGURATION ---
DEPARTMENTS = ["Computer Science", "Electrical Engineering", "Mechanical", "Civil"]
BATCH_YEARS = [2024, 2025, 2026, 2027]
SLOTS = ["A", "B", "C", "D", "P", "Q", "FN1", "AN1", "FN2", "AN2"]
ROOM_CAPACITIES = [20, 25, 30, 40]
QUALIFICATIONS = ["Machine Learning", "Python", "Digital Systems", "Control Systems", "Thermodynamics", "Structural Analysis", "Verilog", "Op-Amps", "Surveying", "Fluid Mechanics"]

# Department-specific hardware
DEPT_EQUIPMENT = {
    "Computer Science": {"type": "GPU_Compute_Nodes", "total": 30},
    "Electrical Engineering": {"type": "FPGA_Boards", "total": 25},
    "Mechanical": {"type": "CNC_Routers", "total": 8},
    "Civil": {"type": "Surveying_Total_Stations", "total": 12}
}

# --- 2. GENERATE ROOMS (Infrastructure) & BUFFER ROOMS ---
rooms = []
for i in range(1, 9):
    rooms.append({
        "room_id": f"LH-{i}",
        "type": "Lecture_Hall" if i <= 5 else "Hardware_Lab",
        "seating_capacity": random.choice(ROOM_CAPACITIES),
        "current_occupancy_by_slot": { "Monday": {}, "Tuesday": {}, "Wednesday": {}, "Thursday": {}, "Friday": {} }
    })
# Add an empty buffer room
rooms.append({"room_id": "LH-9-Buffer", "type": "Lecture_Hall", "seating_capacity": 40, "current_occupancy_by_slot": {"Monday": {}, "Tuesday": {}, "Wednesday": {}, "Thursday": {}, "Friday": {}}, "note": "Unassigned buffer room."})

# --- 3. GENERATE PROFESSORS ---
profs = []
for i in range(1, 21):
    profs.append({
        "prof_id": f"P{str(i).zfill(3)}",
        "name": f"Dr. Faculty_{i}",
        "department": DEPARTMENTS[(i-1) % 4],
        "qualifications": random.sample(QUALIFICATIONS, 3),
        "assigned_courses": [],
        "busy_blocks": [
            {"day": "Friday", "slot": "P", "reason": "Department Meeting", "is_flexible": False, "must_reschedule": False}
        ],
        "preferred_substitute_slots": ["W", "X", "Y", "Z"]
    })

# --- 4. GENERATE COURSES & MASTER TIMETABLE ---
courses = []
master_timetable = { "Monday": {s: [] for s in SLOTS}, "Tuesday": {s: [] for s in SLOTS}, "Wednesday": {s: [] for s in SLOTS}, "Thursday": {s: [] for s in SLOTS}, "Friday": {s: [] for s in SLOTS} }
course_counter = 101

# We will track labs here to dynamically assign instruments later
generated_labs = []

for dept in DEPARTMENTS:
    for batch in BATCH_YEARS:
        course_id = f"{dept[:2].upper()}{course_counter}"
        slot = random.choice(SLOTS)
        day = random.choice(["Monday", "Tuesday", "Wednesday"])
        c_type = "Theory_Only" if "FN" not in slot and "AN" not in slot else "Lab_Only"
        
        # STRICT RULE: 0 TAs for Theory, 2 TAs for Labs
        required_tas = 2 if c_type == "Lab_Only" else 0
        
        available_profs = [p for p in profs if p["department"] == dept and not any(b["slot"] == slot and b["day"] == day for b in p["busy_blocks"])]
        
        if available_profs:
            assigned_prof = available_profs[0]
            # Match room type to course type
            valid_rooms = [r for r in rooms if "Buffer" not in r["room_id"] and (("Lab" in r["type"] and c_type == "Lab_Only") or ("Lecture" in r["type"] and c_type == "Theory_Only"))]
            if not valid_rooms:
                valid_rooms = [rooms[0]] # fallback
            assigned_room = random.choice(valid_rooms)
            req_quals = random.sample(assigned_prof["qualifications"], 2)
            
            course = {
                "course_id": course_id,
                "title": f"{dept} Core {course_counter}",
                "department": dept,
                "type": c_type,
                "primary_batch": f"B.Tech {batch} {dept}",
                "eligible_batches": [], 
                "required_qualifications": req_quals,
                "schedule": {"slot": slot, "room": assigned_room["room_id"]},
                "prof_id": assigned_prof["prof_id"],
                "ta_required": required_tas
            }
            courses.append(course)
            
            if c_type == "Lab_Only":
                generated_labs.append({"dept": dept, "course_id": course_id, "day": day, "slot": slot, "room": assigned_room["room_id"]})
            
            assigned_prof["assigned_courses"].append(course_id)
            assigned_prof["busy_blocks"].append({"day": day, "slot": slot, "reason": f"Teaching {course_id}", "is_flexible": False, "must_reschedule": True})
            
            enrolled_estimate = random.randint(7, 10)
            assigned_room["current_occupancy_by_slot"][day][slot] = {
                "course_id": course_id,
                "in_use_seats": enrolled_estimate,
                "available_seats": assigned_room["seating_capacity"] - enrolled_estimate
            }
            
            master_timetable[day][slot].append(course_id)
            course_counter += 1

# --- 5. GENERATE STUDENTS ---
students = []
student_id_counter = 1000
for dept in DEPARTMENTS:
    for year in BATCH_YEARS:
        num_students = random.randint(7, 10)
        batch_courses = [c["course_id"] for c in courses if c["primary_batch"] == f"B.Tech {year} {dept}"]
        for _ in range(num_students):
            students.append({
                "student_id": f"S{student_id_counter}",
                "degree": "B.Tech",
                "batch_year": year,
                "branch": dept,
                "enrolled_courses": batch_courses,
                "interests": random.sample(QUALIFICATIONS, 2)
            })
            student_id_counter += 1

# --- 6. GENERATE TAs (NO is_flexible flag here per our rules) ---
tas = []
ta_id_counter = 1
for dept in DEPARTMENTS:
    for _ in range(3): 
        ta_id = f"TA_{str(ta_id_counter).zfill(3)}"
        tas.append({
            "ta_id": ta_id,
            "name": f"MTech_Student_{ta_id_counter}",
            "department": dept,
            "qualifications": random.sample(QUALIFICATIONS, 3),
            "max_hours_per_week": 10,
            "current_assigned_hours": 0,
            "assigned_courses": [],
            "unavailable_blocks": [{"day": "Thursday", "slot": "A", "reason": "M.Tech Core Class"}]
        })
        ta_id_counter += 1

# --- 7. GENERATE INSTRUMENTS (Dynamic Allocation) ---
instruments = []

# Map the generated labs to the department's equipment
for dept, eq_info in DEPT_EQUIPMENT.items():
    dept_labs = [lab for lab in generated_labs if lab["dept"] == dept]
    
    allocations = {"Monday": {}, "Tuesday": {}, "Wednesday": {}, "Thursday": {}, "Friday": {}}
    
    # Process up to 2 labs to create realistic usage data
    for lab in dept_labs[:2]:
        units_used = random.randint(5, eq_info["total"] - 2)
        allocations[lab["day"]][lab["slot"]] = {
            "allocated_to_course": lab["course_id"],
            "units_in_use": units_used,
            "units_available": eq_info["total"] - units_used - 1 # Assuming 1 in maintenance
        }
    
    # Clean up empty days
    allocations = {day: slots for day, slots in allocations.items() if slots}
    
    instruments.append({
        "equipment_type": eq_info["type"],
        "total_inventory": eq_info["total"],
        "in_maintenance": 1,
        "usable_inventory": eq_info["total"] - 1,
        "allocations_by_slot": allocations
    })

# Add the universal MakerSpace 3D Printers
instruments.append({
    "equipment_type": "3D_Printers",
    "total_inventory": 8,
    "in_maintenance": 1,
    "usable_inventory": 7,
    "booking_queue": []
})

# --- 8. EXPORT TO JSON ---
os.makedirs("data", exist_ok=True)
files = {
    "infrastructure.json": rooms,
    "professors.json": profs,
    "courses.json": courses,
    "students.json": students,
    "staff_ta.json": tas,
    "instruments.json": instruments,
    "master_timetable.json": master_timetable
}

for filename, data in files.items():
    with open(f"data/{filename}", "w") as f:
        json.dump(data, f, indent=2)

print("✅ Perfect! All 7 interconnected files generated with strict TA limits and custom department instruments.")