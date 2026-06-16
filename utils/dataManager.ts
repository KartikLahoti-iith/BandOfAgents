import * as fs from 'fs';
import * as path from 'path';

export class DataManager {
    private dataDir: string;
    private data: Record<string, any>;

    constructor(dataDir = './data') {
        this.dataDir = dataDir;
        this.data = {};
        this.loadAllData();
    }

    private loadAllData() {
        const files: Record<string, string> = {
            "timetable": "master_timetable.json",
            "infrastructure": "infrastructure.json",
            "professors": "professors.json",
            "courses": "courses.json",
            "students": "students.json",
            "staff_ta": "staff_ta.json",
            "instruments": "instruments.json"
        };

        for (const [key, filename] of Object.entries(files)) {
            const filePath = path.join(this.dataDir, filename);
            try {
                if (fs.existsSync(filePath)) {
                    const fileContent = fs.readFileSync(filePath, 'utf-8');
                    this.data[key] = JSON.parse(fileContent);
                } else {
                    this.data[key] = {};
                }
            } catch (error) {
                console.error(`❌ Error loading ${filename}:`, error);
                this.data[key] = {};
            }
        }
    }

    private getCourseDetails(courseId: string) {
        const courses = this.data["courses"] || [];
        return courses.find((c: any) => c.course_id === courseId) || null;
    }

    // 1. Timetable / General Summary
    public getComprehensiveSummary(): string {
        let summary = "=== CROSS-REFERENCED UNIVERSITY STATE ===\n\n";
        summary += "--- CURRENT LIVE SCHEDULE & COURSE REQUIREMENTS ---\n";
        
        const timetable = this.data["timetable"] || {};
        for (const [day, slots] of Object.entries(timetable)) {
            summary += `📅 ${day}:\n`;
            for (const [slot, courseIds] of Object.entries(slots as Record<string, string[]>)) {
                if (courseIds && courseIds.length > 0) {
                    for (const cid of courseIds) {
                        const cDetails = this.getCourseDetails(cid);
                        if (cDetails) {
                            summary += `  - Slot ${slot}: ${cid} (${cDetails.title}) | Dept: ${cDetails.department} | Type: ${cDetails.type}\n`;
                            summary += `    Room: ${cDetails.schedule.room} | Req Qualifications: ${cDetails.required_qualifications.join(', ')} | TAs Required: ${cDetails.ta_required}\n`;
                        }
                    }
                }
            }
            summary += "\n";
        }

        summary += "--- FACULTY REGISTRY & AVAILABILITY ---\n";
        const professors = this.data["professors"] || [];
        for (const p of professors) {
            const busy = p.busy_blocks.map((b: any) => `${b.day}-${b.slot} (${b.reason})`).join(', ');
            summary += `- Prof: ${p.prof_id} (${p.name}) | Dept: ${p.department}\n`;
            summary += `  Expertise: ${p.qualifications.join(', ')}\n`;
            summary += `  Commitments: ${busy}\n\n`;
        }
        return summary;
    }

    // 2. Resource Summary
    public getResourceSummary(): string {
        let summary = "=== CURRENT PHYSICAL & HARDWARE RESOURCES ===\n\n";
        summary += "--- INFRASTRUCTURE HOUSING ---\n";
        const infra = this.data["infrastructure"] || [];
        for (const r of infra) {
            summary += `- Room: ${r.room_id} | Type: ${r.type} | Capacity: ${r.seating_capacity} seats\n`;
        }
            
        summary += "\n--- SPECIALIZED HARDWARE INVENTORY ---\n";
        const instruments = this.data["instruments"] || [];
        for (const inst of instruments) {
            summary += `- Equipment: ${inst.equipment_type} | Usable Inventory: ${inst.usable_inventory}/${inst.total_inventory} units\n`;
            if (inst.allocations_by_slot) {
                for (const [day, slots] of Object.entries(inst.allocations_by_slot)) {
                    for (const [slot, details] of Object.entries(slots as Record<string, any>)) {
                        summary += `  * Assigned to ${details.allocated_to_course} on ${day} at Slot ${slot} (${details.units_in_use} units in use)\n`;
                    }
                }
            }
        }
        return summary;
    }

    // 3. Personnel Summary
    public getPersonnelSummary(): string {
        let summary = "=== TEACHING ASSISTANT ROSTER ===\n\n";
        const staff = this.data["staff_ta"] || [];
        for (const ta of staff) {
            summary += `- TA ID: ${ta.ta_id} | Name: ${ta.name} | Dept: ${ta.department}\n`;
            summary += `  Qualifications: ${ta.qualifications.join(', ')}\n`;
            const assigned = ta.assigned_courses.length > 0 ? ta.assigned_courses.join(', ') : 'None';
            summary += `  Assigned Labs: ${assigned} (${ta.current_assigned_hours}/10 hours max)\n\n`;
        }
        return summary;
    }
}