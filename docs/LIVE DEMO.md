# 🧪 NeuroAegis Cortex: Live Demo Testing Steps

**System Version:** 3.0.0 | **Core:** Google Gemini 3

This guide provides a structured walkthrough to test the **Intent-Based Reasoning** and **Autonomous Response** layers of the NeuroAegis Cortex.

---

### **Step 1: Environment Readiness**

Before starting the test, ensure the dashboard shows the following baseline metrics:

* **System Load:** < 15% (Demonstrating efficient resource management).
* **API Connection:** `Gemini-3-Pro` or `Gemini-3-Flash` Status: **Active**.
* **Feed Status:** Live Surveillance Feed is visible and running at ~30 FPS.

### **Step 2: The "Benign Movement" Test (Filtering Noise)**

* **Action:** Walk across the camera's view casually (e.g., carrying a cup or looking at a phone).
* **What to look for:**
* **Detection:** The system should identify a "Person."
* **Reasoning:** Look at the **Latest Analysis** log. It should describe the activity as "Normal transit" or "Non-threatening behavior."
* **Verdict:** The **Severity Level** must stay **LOW** (Green). This proves the system successfully ignores false positives that usually plague traditional cameras.



### **Step 3: The "Temporal Intent" Test (Loitering)**

* **Action:** Stand in the corner of the frame for 10–15 seconds while looking around or "scoping" the area.
* **What to look for:**
* **Observation:** Notice the **Reasoning Trace**. Because of Gemini 3’s **2-million-token context window**, the system "remembers" your duration.
* **Verdict:** The severity should escalate to **MEDIUM** with a note stating: *"Prolonged loitering detected; behavioral pattern suggests reconnaissance."*



### **Step 4: The "High-Threat" Test (Aggressive Posture)**

* **Action:** Mimic a hostile action, such as the **Gun Gesture** (finger gun) or wearing a mask/hoodie that obscures your face while moving toward the camera.
* **What to look for:**
* **Latency:** The detection should occur in **< 1.5 seconds** (using the Flash model optimization).
* **Verdict:** The status will flip to **CRITICAL** (Red) with an **Intent Score > 90%**.
* **Reasoning:** The log will state: *"Subject is masked/armed; high-confidence hostile intent identified."*



### **Step 5: The "Autonomous Response" Test**

* **Action:** While the High-Threat alert is active, check the **Active Response Plan** panel at the bottom of the dashboard.
* **What to look for:**
* **Execution:** The status should change from `Standby` to `Active Deterrence`.
* **Automated Steps:** Verify the dashboard lists the following simulated steps:
1. `[LOCK_ENGAGED]` - Digital locking of entry points.
2. `[STROBE_ACTIVE]` - Visual deterrence initiated.
3. `[DISPATCH_READY]` - Emergency protocols prepared.

---

### **💡 Summary for Judges**

| Feature | Technical Proof |
| --- | --- |
| **Noise Filtering** | System ignored benign motion in Step 2. |
| **Memory/Context** | System recognized "Time" as a factor in Step 3. |
| **Deep Reasoning** | AI explained *why* it felt threatened in Step 4. |
| **Speed** | End-to-end inference was achieved in near real-time. |

---

**Created by:** Timothee RINGUYENEZA

**Project:** [NeuroAegis Cortex](https://github.com/Thimethane/NEUROAEGIS-CORTEX)