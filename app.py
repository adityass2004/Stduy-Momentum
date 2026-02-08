import streamlit as st
import storage.data_manager as dm
import logic.task_generator as tg
import logic.progress_tracker as pt
import ui.visualizations as viz
from models.user_profile import UserProfile
from datetime import date, datetime

def render_onboarding():
    st.title("Welcome to Study Momentum! 🎓")
    st.markdown("Let's set up your personalized IELTS plan.")
    
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            target_score = st.number_input("Target Band Score", 0.0, 9.0, 7.0, 0.5)
            exam_date = st.date_input("Exam Date", min_value=date.today())
        with col2:
            daily_minutes = st.number_input("Daily Study Time (mins)", 15, 300, 60, 15)
            weakest_skill = st.selectbox("Weakest Skill", ["Reading", "Writing", "Listening", "Speaking"])
        
        if st.form_submit_button("Start My Journey"):
            profile = UserProfile(target_score, str(exam_date), daily_minutes, weakest_skill)
            dm.save_profile(profile)
            st.rerun()

def render_dashboard(profile):
    res = pt.process_check_in(profile)
    if res["score_updated"] or res["date_updated"] or res["skips_replenished"]:
        dm.save_profile(profile)
        
    if res["penalty"] > 0:
        st.error(f"⚠️ Missed {res['days_missed']} days! Penalty: -{res['penalty']} (Score: {res['new_score']})")
        if res["streak_reset"]: st.warning("🔥 Streak reset to 0!")
    elif res["skips_used"] > 0:
        st.info(f"🛡️ Missed {res['skips_used']} day(s). Streak saved! ({profile.skips_left} skips left)")
    if res["skips_replenished"]:
        st.success("🎁 Weekly Skip Replenished! (+1 🛡️)")

    with st.sidebar:
        st.header("Hi, Scholar! 👋")
        st.metric("Current Streak", f"{profile.current_streak} days")
        st.metric("Skips Available", f"{profile.skips_left} 🛡️")
        st.divider()
        st.subheader("Study Buddy 🤖")
        if st.button("👋 Wave to Buddy"): st.toast("Buddy waved back! Keep pushing!")
        st.divider()
        st.subheader("Badges 🏆")
        for b in profile.badges:
            st.caption(f"{pt.BADGES.get(b, {}).get('name', b)}")

    st.title("Daily Dashboard 📅")
    st.markdown(f"### Momentum Score: {profile.momentum_score}/100")
    st.progress(profile.momentum_score / 100)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Target", profile.target_score)
    try:
        days = (datetime.strptime(profile.exam_date, "%Y-%m-%d").date() - date.today()).days
        col2.metric("Days Left", f"{days} days")
    except: col2.metric("Days Left", "N/A")
    col3.metric("Focus", profile.weakest_skill)
    st.markdown("---")

    st.subheader("Today's Tasks")
    saved_tasks = dm.get_today_tasks_status()
    if "daily_tasks" not in st.session_state:
        st.session_state.daily_tasks = saved_tasks if saved_tasks else tg.generate_daily_tasks(profile)
        dm.save_today_tasks_status(st.session_state.daily_tasks)

    tasks = st.session_state.daily_tasks
    tasks_updated = False
    
    for i, t in enumerate(tasks):
        c1, c2, c3 = st.columns([0.5, 4, 1])
        checked = c1.checkbox("", key=f"t_{i}", value=t["completed"])
        if checked != t["completed"]:
            t["completed"] = checked
            tasks_updated = True
        
        style = "text-decoration: line-through; color: gray;" if t["completed"] else ""
        c2.markdown(f"<div style='{style}'><b>{t['skill']}</b>: {t['desc']}</div>", unsafe_allow_html=True)
        c3.caption(f"{t['time']}m")

    if tasks_updated: dm.save_today_tasks_status(tasks)
    st.markdown("---")

    history = dm.get_history()
    if history:
        st.subheader("Weekly Summary 🗓️")
        w_stats = pt.get_weekly_stats(history)
        c1, c2, c3 = st.columns(3)
        c1.metric("Tasks (7d)", w_stats["weekly_tasks"])
        c2.metric("Active Days (7d)", w_stats["active_days"])
        c3.metric("Momentum", profile.momentum_score)
        
        st.subheader("Skill Progress 📈")
        fig = viz.plot_skill_progress(history)
        if fig: st.pyplot(fig)
        st.markdown("---")

    if st.button("🏁 Finalize Day"):
        stats = pt.finalize_session(profile, tasks)
        dm.save_profile(profile)
        dm.save_daily_history(stats)
        st.balloons()
        
        for b in stats["new_badges"]: st.success(f"🏆 Unlocked: {b['name']}!")
        st.success(f"Momentum Gained: +{stats['momentum_gained']}")
        st.rerun()

if __name__ == "__main__":
    st.set_page_config(page_title="Study Momentum", page_icon="🚀", layout="wide")
    profile = dm.get_user_profile()
    if not profile: render_onboarding()
    else: render_dashboard(profile)
