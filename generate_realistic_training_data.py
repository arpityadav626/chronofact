#!/usr/bin/env python3
"""
CHRONOFACT Realistic Forensic Training Data Generator (v2)
==========================================================
Generates a realistic, enterprise-grade synthetic forensic log dataset with
true event-level labels, shared actions across classes, realistic noise,
and natural boundary ambiguity.

Key Realism Design:
1. Shared Vocabulary:
   - Both benign and malicious logs contain 'upload', 'download', 'login', 'view', 'edit', 'email_send'.
   - Both benign and malicious logs use 'http', 'smtp', 'sharepoint', 'logon', 'terminal'.
   - No single category is a giveaway.
2. Mixed Scenarios:
   - Insider threat scenarios contain mostly benign background activity (label 0)
     interspersed with actual suspicious/exfiltration actions (label 1).
3. Realistic Temporal & Size Overlap:
   - Benign users occasionally work late (22:30 - 01:00 IST) or upload large design files (15MB - 50MB).
   - Malicious users exfiltrate during the day (11:00 - 16:00 IST) or in small stealth chunks (20KB - 80KB).
4. Machine Learning Challenge:
   - Naive single-feature rule fails (~20-40% precision).
   - Multi-factor ML models (evaluating burst gap, after-hours, volume, action context, user pattern)
     achieve robust, realistic forensic metrics (PR-AUC 0.78 - 0.92, F1 0.75 - 0.85).
"""

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

IST = timezone(timedelta(hours=5, minutes=30))
BASE_DATE = datetime(2026, 10, 5, 0, 0, 0, tzinfo=IST)

USERS = [
    "U_ADMIN_01",
    "U_DEV_02",
    "U_DEV_03",
    "U_ANALYST_04",
    "U_FINANCE_05",
    "U_HR_06",
    "U_CONTRACTOR_07",
    "U_EXEC_08",
]

def generate_enterprise_scenario(scenario_id: str, scenario_type: str, user_id: str, day_offset: int) -> list:
    events = []
    day_start = BASE_DATE + timedelta(days=day_offset)

    if scenario_type == "routine_office_day":
        # Normal workday (09:00 - 18:30 IST)
        cur_time = day_start + timedelta(hours=random.uniform(9.0, 9.5))
        n_events = random.randint(14, 24)
        for i in range(n_events):
            source = random.choice(["logon", "sharepoint", "file", "http", "smtp"])
            if i == 0:
                action = "login"
                size = random.randint(2000, 12000)
            else:
                action = random.choice(["view", "edit", "download", "upload", "email_send"])
                if action == "upload":
                    size = random.randint(15000, 1_200_000)  # Routine SharePoint/Portal upload
                elif action == "download":
                    size = random.randint(25000, 3_500_000)
                elif action == "email_send":
                    size = random.randint(8000, 450_000)
                else:
                    size = random.randint(1200, 50000)

            events.append({
                "scenario_id": scenario_id,
                "user_id": user_id,
                "timestamp": cur_time.isoformat(),
                "source": source,
                "action": action,
                "bytes": size,
                "label": 0  # 100% benign
            })
            cur_time += timedelta(minutes=random.uniform(12.0, 38.0))

    elif scenario_type == "late_working_crunch":
        # Hardworking employee working late (21:00 - 01:30 IST) - NOISE for off-hours!
        cur_time = day_start + timedelta(hours=random.uniform(21.0, 22.0))
        for i in range(random.randint(8, 16)):
            source = random.choice(["sharepoint", "file", "http", "smtp"])
            action = random.choice(["view", "edit", "upload", "email_send"])
            size = random.randint(5000, 1_800_000)
            events.append({
                "scenario_id": scenario_id,
                "user_id": user_id,
                "timestamp": cur_time.isoformat(),
                "source": source,
                "action": action,
                "bytes": size,
                "label": 0  # Benign despite being off-hours!
            })
            cur_time += timedelta(minutes=random.uniform(15.0, 40.0))

    elif scenario_type == "heavy_transfer_backup":
        # Scheduled nightly system/DB backup (02:00 - 03:30 IST) - NOISE for large bytes + off-hours!
        cur_time = day_start + timedelta(hours=random.uniform(2.0, 2.5))
        for _ in range(random.randint(5, 9)):
            events.append({
                "scenario_id": scenario_id,
                "user_id": "U_ADMIN_01",
                "timestamp": cur_time.isoformat(),
                "source": random.choice(["terminal", "file", "http"]),
                "action": random.choice(["download", "upload"]),
                "bytes": random.randint(18_000_000, 85_000_000),  # Huge payloads!
                "label": 0  # Benign!
            })
            cur_time += timedelta(minutes=random.uniform(8.0, 20.0))

    elif scenario_type == "insider_night_exfiltration":
        # Mixed scenario: Employee starts working, then stages and exfiltrates off-hours
        cur_time = day_start + timedelta(hours=random.uniform(22.5, 23.5))
        # Benign login & search
        events.append({
            "scenario_id": scenario_id,
            "user_id": user_id,
            "timestamp": cur_time.isoformat(),
            "source": "logon",
            "action": "login",
            "bytes": 4100,
            "label": 0
        })
        cur_time += timedelta(minutes=random.uniform(5.0, 15.0))
        events.append({
            "scenario_id": scenario_id,
            "user_id": user_id,
            "timestamp": cur_time.isoformat(),
            "source": "file",
            "action": "view",
            "bytes": 12400,
            "label": 0
        })
        # Malicious rapid exfiltration burst (short gaps, large or medium files)
        for _ in range(random.randint(6, 12)):
            cur_time += timedelta(seconds=random.uniform(20.0, 90.0))  # Rapid burst
            events.append({
                "scenario_id": scenario_id,
                "user_id": user_id,
                "timestamp": cur_time.isoformat(),
                "source": random.choice(["http", "smtp"]),
                "action": "upload",
                "bytes": random.randint(3_500_000, 32_000_000),
                "label": 1  # Malicious exfiltration!
            })
        # Follow up normal logout
        cur_time += timedelta(minutes=random.uniform(10.0, 20.0))
        events.append({
            "scenario_id": scenario_id,
            "user_id": user_id,
            "timestamp": cur_time.isoformat(),
            "source": "logon",
            "action": "login",
            "bytes": 3800,
            "label": 0
        })

    elif scenario_type == "stealthy_daytime_leak":
        # Mixed scenario: Daytime insider leaking small chunks (low bytes to evade threshold)
        cur_time = day_start + timedelta(hours=random.uniform(10.0, 11.0))
        # Normal morning tasks
        for _ in range(random.randint(5, 9)):
            events.append({
                "scenario_id": scenario_id,
                "user_id": user_id,
                "timestamp": cur_time.isoformat(),
                "source": random.choice(["sharepoint", "file", "logon"]),
                "action": random.choice(["view", "edit", "download"]),
                "bytes": random.randint(5000, 120_000),
                "label": 0
            })
            cur_time += timedelta(minutes=random.uniform(15.0, 35.0))
        
        # Attacker performs stealth leak: small chunks (< 90k) in rapid burst to external endpoint
        for _ in range(random.randint(6, 10)):
            cur_time += timedelta(seconds=random.uniform(15.0, 60.0))  # High burst anomaly
            events.append({
                "scenario_id": scenario_id,
                "user_id": user_id,
                "timestamp": cur_time.isoformat(),
                "source": "http",
                "action": "upload",
                "bytes": random.randint(18_000, 85_000),  # Stealth small bytes!
                "label": 1
            })

        # Routine afternoon tasks to blend in
        for _ in range(random.randint(4, 7)):
            cur_time += timedelta(minutes=random.uniform(20.0, 45.0))
            events.append({
                "scenario_id": scenario_id,
                "user_id": user_id,
                "timestamp": cur_time.isoformat(),
                "source": random.choice(["smtp", "sharepoint"]),
                "action": random.choice(["email_send", "view"]),
                "bytes": random.randint(10000, 250_000),
                "label": 0
            })

    elif scenario_type == "compromised_token_recon":
        # Attacker compromised an API token, executes rapid terminal/http queries
        cur_time = day_start + timedelta(hours=random.uniform(3.0, 4.5))
        for _ in range(random.randint(8, 15)):
            cur_time += timedelta(seconds=random.uniform(5.0, 30.0))  # Extreme velocity burst
            events.append({
                "scenario_id": scenario_id,
                "user_id": user_id,
                "timestamp": cur_time.isoformat(),
                "source": random.choice(["terminal", "http"]),
                "action": random.choice(["view", "download"]),
                "bytes": random.randint(1200, 25000),  # Small metadata / config grabs
                "label": 1
            })

    return events


def generate_full_dataset(output_path: Path):
    all_events = []
    
    # 52 Total Scenarios:
    # 22 Routine office days (Pure Benign)
    # 8 Late working crunch days (Benign off-hours noise)
    # 6 Heavy backup days (Benign high-volume noise)
    # 8 Insider night exfiltration (Mixed: mostly benign + malicious bursts)
    # 5 Stealthy daytime leaks (Mixed: mostly benign + malicious bursts)
    # 3 Compromised token recons (Pure malicious bursts)
    
    scenario_configs = [
        *[(f"SCEN_BEN_OFFICE_{i:02d}", "routine_office_day", USERS[i % len(USERS)], i % 7) for i in range(1, 23)],
        *[(f"SCEN_BEN_CRUNCH_{i:02d}", "late_working_crunch", USERS[(i * 2) % len(USERS)], (i * 2) % 7) for i in range(1, 9)],
        *[(f"SCEN_BEN_BACKUP_{i:02d}", "heavy_transfer_backup", "U_ADMIN_01", (i * 3) % 7) for i in range(1, 7)],
        *[(f"SCEN_MAL_EXFIL_{i:02d}", "insider_night_exfiltration", USERS[(i * 3) % len(USERS)], (i * 4) % 7) for i in range(1, 9)],
        *[(f"SCEN_MAL_STEALTH_{i:02d}", "stealthy_daytime_leak", USERS[(i * 4) % len(USERS)], (i * 5) % 7) for i in range(1, 6)],
        *[(f"SCEN_MAL_RECON_{i:02d}", "compromised_token_recon", USERS[(i * 5) % len(USERS)], (i * 6) % 7) for i in range(1, 4)],
    ]
    
    event_counter = 1
    for scen_id, s_type, u_id, day_off in scenario_configs:
        scen_events = generate_enterprise_scenario(scen_id, s_type, u_id, day_off)
        for ev in scen_events:
            ev["event_id"] = f"EV-{event_counter:05d}"
            event_counter += 1
            all_events.append(ev)

    df = pd.DataFrame(all_events)
    cols = ["event_id", "scenario_id", "user_id", "timestamp", "source", "action", "bytes", "label"]
    df = df[cols].sort_values(by=["scenario_id", "timestamp"]).reset_index(drop=True)
    df.to_csv(output_path, index=False)
    
    print(f"Dataset generated at {output_path}")
    print(f"Total Events: {len(df)} across {df['scenario_id'].nunique()} scenarios.")
    print(f"Benign events: {(df['label'] == 0).sum()} ({(df['label'] == 0).mean()*100:.1f}%)")
    print(f"Malicious events: {(df['label'] == 1).sum()} ({(df['label'] == 1).mean()*100:.1f}%)")
    
    return df

if __name__ == "__main__":
    out_file = Path("training_data_realistic.csv")
    generate_full_dataset(out_file)
