import 'dotenv/config';
import { Agent, SimpleAdapter } from '@thenvoi/sdk'; 
import OpenAI from 'openai';
import { DataManager } from './utils/dataManager';

// --- 1. INITIALIZE DATA ENGINE & LLM ---
const dataEngine = new DataManager('./data');

const featherless = new OpenAI({
    baseURL: "https://api.featherless.ai/v1",
    apiKey: process.env.FEATHERLESS_API_KEY,
});

// Reusable function to call Featherless safely (No streaming bugs)
async function askAI(systemPrompt: string, userMessage: string): Promise<string> {
    try {
        const completion = await featherless.chat.completions.create({
            model: "Qwen/Qwen2.5-7B-Instruct",
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userMessage }
            ],
            temperature: 0.1,
            stream: false 
        });
        return completion.choices[0]?.message?.content || "Error analyzing data.";
    } catch (error) {
        console.error("❌ API Error:", error);
        return "Network API crashed or timed out.";
    }
}

// --- 2. BUILD THE 3 ADAPTERS ---

const personnelAdapter = new SimpleAdapter({
    async onMessage(message: string) {
        console.log("📥 [@Personnel_Agent] Received request...");
        const context = dataEngine.getPersonnelSummary();
        const prompt = `You are the University Personnel Agent. You manage TA assignments. STRICT MANDATE: Theory courses require EXACTLY 0 TAs. Lab courses require EXACTLY 2 TAs. Never allocate 1 TA to a course under any circumstances. Ensure no TA exceeds 10 hours per week. YOUR RESPONSE FORMAT: State the current tracking metrics and explicitly list the TA IDs assigned or unassigned.\n\nContext Data:\n${context}`;
        return await askAI(prompt, message);
    }
});

const resourceAdapter = new SimpleAdapter({
    async onMessage(message: string) {
        console.log("📥 [@Resource_Agent] Received request...");
        const context = dataEngine.getResourceSummary();
        const prompt = `You are the expert Resource Agent for a university. Your job is to allocate rooms and specialized lab hardware (FPGAs, GPUs, CNCs, 3D Printers). You must maximize resource utilization without causing double-bookings or exceeding available physical inventory limits. YOUR RESPONSE FORMAT: Provide your logical assessment followed by a clear specification of the room or hardware asset allocated.\n\nContext Data:\n${context}`;
        return await askAI(prompt, message);
    }
});

const timetableAdapter = new SimpleAdapter({
    async onMessage(message: string) {
        console.log("📥 [@Timetable_Agent] Received request...");
        const context = dataEngine.getComprehensiveSummary();
        const prompt = `You are the expert Timetable Agent for a university. Your job is to resolve scheduling conflicts, handling teacher leaves, or room reassignments. You must be mathematically rigorous and absolute in enforcing operational rules. CRITICAL OPERATIONAL RULES: 1. No Professor can be double-booked in the same Day and Slot. 2. No Room can host two courses in the same Day and Slot. 3. You must only substitute a professor with another professor from the SAME department who shares at least one required qualification. 4. Keep structural changes minimal. Swap slots or change a professor only if absolutely necessary. YOUR OUTPUT FORMAT: Reply with step-by-step reasoning first, and end with a structured summary of specific changes made.\n\nContext Data:\n${context}`;
        return await askAI(prompt, message);
    }
});

// --- 3. BOOT THE NETWORK ---
async function main() {
    console.log("🚀 Booting All 3 Native Node.js Agents...");
    
    const personnel = new Agent({
        adapter: personnelAdapter,
        agentId: process.env.PERSONNEL_ID as string,
        apiKey: process.env.PERSONNEL_TOKEN as string
    });

    const resource = new Agent({
        adapter: resourceAdapter,
        agentId: process.env.RESOURCE_ID as string,
        apiKey: process.env.RESOURCE_TOKEN as string
    });

    const timetable = new Agent({
        adapter: timetableAdapter,
        agentId: process.env.TIMETABLE_ID as string,
        apiKey: process.env.TIMETABLE_TOKEN as string
    });

    // Start all agents concurrently using the correct SDK method
    await Promise.all([
        personnel.start(),
        resource.start(),
        timetable.start()
    ]);

    console.log("✅ All 3 Agents connected flawlessly to Band.ai! Waiting for messages...");
}

main().catch(console.error);