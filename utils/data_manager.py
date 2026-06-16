import json
import os

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.load_all_data()

    def load_all_data(self):
        """Loads all 7 JSON files into memory."""
        files = {
            "timetable": "master_timetable.json",
            "infrastructure": "infrastructure.json",
            "professors": "professors.json",
            "courses": "courses.json",
            "students": "students.json",
            "staff_ta": "staff_ta.json",
            "instruments": "instruments.json"
        }
        self.data = {}
        for key, filename in files.items():
            path = os.path.join(self.data_dir, filename)
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.data[key] = json.load(f)
            else:
                self.data[key] = {}

    def get_course_details(self, course_id):
        """Cross-references a course ID with its structural rules."""
        for course in self.data.get("courses", []):
            if course["course_id"] == course_id:
                return course
        return None

    def get_comprehensive_summary(self):
        """
        Stitches nested data across files into plain English text.
        This gives the LLM clean, cross-referenced context.
        """
        summary = "=== CROSS-REFERENCED UNIVERSITY STATE ===\n\n"
        
        # 1. Stitched Timetable & Course Rules
        summary += "--- CURRENT LIVE SCHEDULE & COURSE REQUIREMENTS ---\n"
        for day, slots in self.data.get("timetable", {}).items():
            summary += f"📅 {day}:\n"
            for slot, course_ids in slots.items():
                if course_ids:
                    for cid in course_ids:
                        c_details = self.get_course_details(cid)
                        if c_details:
                            summary += (
                                f"  - Slot {slot}: {cid} ({c_details['title']}) | "
                                f"Dept: {c_details['department']} | Type: {c_details['type']}\n"
                                f"    Room: {c_details['schedule']['room']} | "
                                f"Req Qualifications: {', '.join(c_details['required_qualifications'])} | "
                                f"TAs Required: {c_details['ta_required']}\n"
                            )
            summary += "\n"

        # 2. Professors
        summary += "--- FACULTY REGISTRY & AVAILABILITY ---\n"
        for p in self.data.get("professors", []):
            busy = [f"{b['day']}-{b['slot']} ({b['reason']})" for b in p["busy_blocks"]]
            summary += (
                f"- Prof: {p['prof_id']} ({p['name']}) | Dept: {p['department']}\n"
                f"  Expertise: {', '.join(p['qualifications'])}\n"
                f"  Commitments: {', '.join(busy)}\n\n"
            )

        return summary
    
# --- ADD THESE TO THE BOTTOM OF THE DataManager CLASS ---

    def get_resource_summary(self):
        """Stitches infrastructure and instruments data."""
        summary = "=== CURRENT PHYSICAL & HARDWARE RESOURCES ===\n\n"
        summary += "--- INFRASTRUCTURE HOUSING ---\n"
        for r in self.data.get("infrastructure", []):
            summary += f"- Room: {r['room_id']} | Type: {r['type']} | Capacity: {r['seating_capacity']} seats\n"
            
        summary += "\n--- SPECIALIZED HARDWARE INVENTORY ---\n"
        for inst in self.data.get("instruments", []):
            summary += f"- Equipment: {inst['equipment_type']} | Usable Inventory: {inst['usable_inventory']}/{inst['total_inventory']} units\n"
            if "allocations_by_slot" in inst:
                for day, slots in inst["allocations_by_slot"].items():
                    for slot, details in slots.items():
                        summary += f"  * Assigned to {details['allocated_to_course']} on {day} at Slot {slot} ({details['units_in_use']} units in use)\n"
        return summary

    def get_personnel_summary(self):
        """Stitches TA data."""
        summary = "=== TEACHING ASSISTANT ROSTER ===\n\n"
        for ta in self.data.get("staff_ta", []):
            summary += f"- TA ID: {ta['ta_id']} | Name: {ta['name']} | Dept: {ta['department']}\n"
            summary += f"  Qualifications: {', '.join(ta['qualifications'])}\n"
            summary += f"  Assigned Labs: {', '.join(ta['assigned_courses']) if ta['assigned_courses'] else 'None'} ({ta['current_assigned_hours']}/10 hours max)\n\n"
        return summary