from typing import List, Dict
from datetime import date, datetime, timedelta
from models.user_profile import UserProfile

BADGES = {
    "streak_3": {"id": "streak_3", "name": "🔥 3 Day Streak", "desc": "Completed tasks for 3 consecutive days"},
    "streak_7": {"id": "streak_7", "name": "🚀 7 Day Streak", "desc": "Completed tasks for 7 consecutive days"},
    "momentum_50": {"id": "momentum_50", "name": "⭐ Momentum Builder", "desc": "Reached a momentum score of 50"},
    "momentum_100": {"id": "momentum_100", "name": "👑 Momentum Master", "desc": "Reached a momentum score of 100"},
    "perfect_day": {"id": "perfect_day", "name": "✅ Perfect Day", "desc": "Completed all daily tasks"},
}

def calculate_skipped_penalty(last_check_in: str) -> int:
    if not last_check_in: return 0
    try:
        last_date = datetime.strptime(last_check_in, "%Y-%m-%d").date()
        diff = (date.today() - last_date).days
        return (diff - 1) * 3 if diff > 1 else 0
    except ValueError:
        return 0

def update_momentum_score(current_score: int, delta: int) -> int:
    return max(0, min(100, current_score + delta))

def process_check_in(profile: UserProfile) -> Dict:
    today = date.today()
    today_str = str(today)
    
    skips_replenished = 0
    try:
        last_grant = datetime.strptime(profile.last_skip_grant, "%Y-%m-%d").date()
        if (today - last_grant).days >= 7:
            if profile.skips_left < 3:
                profile.skips_left += 1
                skips_replenished = 1
            profile.last_skip_grant = today_str
    except ValueError:
        profile.last_skip_grant = today_str

    if profile.last_check_in == today_str:
        return {
            "penalty": 0, "days_missed": 0, "skips_used": 0,
            "score_updated": False, "date_updated": False,
            "old_score": profile.momentum_score, "new_score": profile.momentum_score,
            "streak_reset": False, "skips_replenished": skips_replenished
        }

    penalty = calculate_skipped_penalty(profile.last_check_in)
    days_missed = penalty // 3 if penalty > 0 else 0
    result = {
        "penalty": penalty, "days_missed": days_missed, "skips_used": 0,
        "score_updated": False, "date_updated": False,
        "old_score": profile.momentum_score, "new_score": profile.momentum_score,
        "streak_reset": False, "skips_replenished": skips_replenished
    }
    
    if penalty > 0:
        if profile.skips_left >= days_missed:
            profile.skips_left -= days_missed
            result["skips_used"] = days_missed
            result["penalty"] = 0 
        else:
            profile.momentum_score = update_momentum_score(profile.momentum_score, -penalty)
            profile.current_streak = 0
            result["new_score"] = profile.momentum_score
            result["score_updated"] = True
            result["streak_reset"] = True
            
        profile.last_check_in = today_str
        result["date_updated"] = True
        
    elif profile.last_check_in != today_str:
        profile.last_check_in = today_str
        result["date_updated"] = True
        
    return result

def check_for_badges(profile: UserProfile, completed_all: bool) -> List[Dict]:
    new_badges = []
    def unlock(key):
        b = BADGES[key]
        if b["id"] not in profile.badges:
            profile.badges.append(b["id"])
            new_badges.append(b)
            
    if profile.current_streak >= 3: unlock("streak_3")
    if profile.current_streak >= 7: unlock("streak_7")
    if profile.momentum_score >= 50: unlock("momentum_50")
    if profile.momentum_score >= 100: unlock("momentum_100")
    if completed_all: unlock("perfect_day")
    return new_badges

def finalize_session(profile: UserProfile, tasks: List[Dict]) -> Dict:
    """Finalizes day: +Score, +Streak, Check Badges."""
    completed = [t for t in tasks if t["completed"]]
    count = len(completed)
    total = len(tasks)
    
    # Score: +5/task, +10 bonus for all
    gain = count * 5
    if total > 0 and count == total: gain += 10
    
    profile.momentum_score = update_momentum_score(profile.momentum_score, gain)
    
    # Increment Streak
    profile.current_streak += 1
    if profile.current_streak > profile.max_streak:
        profile.max_streak = profile.current_streak
        
    # Skills
    skills_improved = {}
    for t in completed:
        skills_improved[t["skill"]] = skills_improved.get(t["skill"], 0) + 1
        
    new_badges = check_for_badges(profile, count == total and total > 0)
    
    return {
        "date": str(date.today()),
        "completed_count": count,
        "total_count": total,
        "momentum_gained": gain,
        "skills_improved": skills_improved,
        "new_streak": profile.current_streak,
        "new_badges": new_badges
    }

def get_weekly_stats(history: List[Dict]) -> Dict:
    today = date.today()
    last_week = today - timedelta(days=7)
    
    weekly_tasks = 0
    active_days = 0
    skill_gains = {}
    
    for entry in history:
        try:
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            if last_week < entry_date <= today:
                weekly_tasks += entry.get("completed_count", 0)
                active_days += 1
                for skill, count in entry.get("skills_improved", {}).items():
                    skill_gains[skill] = skill_gains.get(skill, 0) + count
        except (ValueError, KeyError):
            continue
            
    return {"weekly_tasks": weekly_tasks, "active_days": active_days, "skill_gains": skill_gains}