import random
from typing import List, Dict
from datetime import date

TASK_POOL = {
    "Reading": [
        {"desc": "Solve 10 passages", "time": 40},
        {"desc": "Read 2 academic articles", "time": 30},
        {"desc": "Complete 1 full mock test section", "time": 60},
        {"desc": "Speed read 5 pages", "time": 15},
    ],
    "Writing": [
        {"desc": "Write Task 1 (150 words)", "time": 20},
        {"desc": "Write Task 2 (250 words)", "time": 40},
        {"desc": "Review grammar rules", "time": 15},
        {"desc": "Paraphrase 5 sentences", "time": 10},
    ],
    "Listening": [
        {"desc": "Practice audio quiz", "time": 30},
        {"desc": "Listen to a TED Talk", "time": 15},
        {"desc": "Transcribe 2 mins of audio", "time": 20},
        {"desc": "Full Listening Mock Test", "time": 40},
    ],
    "Speaking": [
        {"desc": "Record 2 minute speech", "time": 10},
        {"desc": "Practice Part 1 questions", "time": 15},
        {"desc": "Describe a picture", "time": 5},
        {"desc": "Shadowing exercise", "time": 20},
    ]
}

def generate_daily_tasks(profile) -> List[Dict]:
    today_seed = date.today().toordinal()
    random.seed(today_seed)
    
    tasks = []
    
    weakest = profile.weakest_skill
    if weakest in TASK_POOL:
        t = random.choice(TASK_POOL[weakest])
        tasks.append({
            "skill": weakest, "desc": t["desc"], "time": t["time"], "completed": False
        })
    
    skills = ["Reading", "Writing", "Listening", "Speaking"]
    
    while len(tasks) < 3:
        skill = random.choice(skills)
        t = random.choice(TASK_POOL[skill])
        
        if any(existing['desc'] == t['desc'] for existing in tasks):
            continue
            
        tasks.append({
            "skill": skill, "desc": t["desc"], "time": t["time"], "completed": False
        })
        
    return tasks