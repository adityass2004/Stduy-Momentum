import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict, Optional

def plot_skill_progress(history: List[Dict]) -> Optional[plt.Figure]:
    if not history: return None
        
    valid_history = [h for h in history if "date" in h]
    if not valid_history: return None

    sorted_history = sorted(valid_history, key=lambda x: x["date"])
    dates = [datetime.strptime(entry["date"], "%Y-%m-%d").date() for entry in sorted_history]
    skills = ["Reading", "Writing", "Listening", "Speaking"]
    
    cumulative_skills = {skill: [] for skill in skills}
    current_totals = {skill: 0 for skill in skills}
    
    for entry in sorted_history:
        daily_skills = entry.get("skills_improved", {})
        for skill in skills:
            current_totals[skill] += daily_skills.get(skill, 0)
            cumulative_skills[skill].append(current_totals[skill])
            
    with plt.style.context('dark_background'):
        fig, ax = plt.subplots(figsize=(10, 5))
        
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        for skill in skills:
            ax.plot(dates, cumulative_skills[skill], marker='o', label=skill)
            
        ax.set_title("Skill Mastery Progress", color='white')
        ax.set_xlabel("Date", color='white')
        ax.set_ylabel("Tasks Completed", color='white')
        
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
            
        legend = ax.legend()
        plt.setp(legend.get_texts(), color='white')
        
        ax.grid(True, linestyle='--', alpha=0.3)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator())
        fig.autofmt_xdate()
        
    return fig