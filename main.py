import json
from pathlib import Path

import streamlit as st


def load_program(path: str = "scheda.json") -> dict:
    file_path = Path(path)
    if not file_path.exists():
        st.error(f"File non trovato: {file_path}")
        st.stop()

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fmt_range(value: list[int] | None, suffix: str = "") -> str:
    if not value:
        return "-"
    if len(value) == 1:
        return f"{value[0]}{suffix}"
    if value[0] == value[1]:
        return f"{value[0]}{suffix}"
    return f"{value[0]}-{value[1]}{suffix}"


def exercise_card(exercise: dict) -> None:
    if exercise.get("superset"):
        st.markdown(f"#### {exercise.get('name', 'Superset')}")
        pair = exercise.get("pair", [])
        for idx, sub in enumerate(pair, start=1):
            with st.container(border=True):
                st.markdown(f"**{idx}. {sub.get('name', 'Esercizio')}**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Serie", sub.get("sets", "-"))
                c2.metric("Ripetizioni", fmt_range(sub.get("reps_range")))
                c3.metric("RIR", fmt_range(sub.get("target_RIR")))
                st.caption(f"Recupero: {fmt_range(sub.get('rest_seconds'), 's')}")
                notes = sub.get("notes", [])
                if notes:
                    st.markdown("  \n".join(f"- {n}" for n in notes))
        return

    if exercise.get("choose_one"):
        st.markdown(f"#### {exercise.get('name', 'Scegli 1 opzione')}")
        for option in exercise.get("options", []):
            with st.container(border=True):
                st.markdown(f"**Opzione: {option.get('variant', '-') }**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Serie", option.get("sets", "-"))
                if "duration_seconds_range" in option:
                    c2.metric("Durata", fmt_range(option.get("duration_seconds_range"), "s"))
                else:
                    c2.metric("Ripetizioni", fmt_range(option.get("reps_range")))
                c3.metric("RIR", fmt_range(option.get("target_RIR")))
                st.caption(f"Recupero: {fmt_range(option.get('rest_seconds'), 's')}")
                notes = option.get("notes", [])
                if notes:
                    st.markdown("  \n".join(f"- {n}" for n in notes))
        return

    with st.container(border=True):
        st.markdown(f"#### {exercise.get('name', 'Esercizio')}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Serie", exercise.get("sets", "-"))
        c2.metric("Ripetizioni", fmt_range(exercise.get("reps_range")))
        c3.metric("RIR", fmt_range(exercise.get("target_RIR")))
        if "duration_seconds_range" in exercise:
            c2.metric("Durata", fmt_range(exercise.get("duration_seconds_range"), "s"))
        st.caption(f"Recupero: {fmt_range(exercise.get('rest_seconds'), 's')}")
        notes = exercise.get("notes", [])
        if notes:
            st.markdown("  \n".join(f"- {n}" for n in notes))


def render_overview(data: dict) -> None:
    st.subheader(data.get("program_name", "Scheda pesistica"))
    st.caption(f"Versione: {data.get('version', '-')}")

    goal = data.get("goal", {})
    primary = ", ".join(goal.get("primary", [])) or "-"
    secondary = ", ".join(goal.get("secondary", [])) or "-"
    st.markdown(f"**Obiettivi principali:** {primary}")
    st.markdown(f"**Obiettivi secondari:** {secondary}")

    context = data.get("context", {})
    st.markdown("### Contesto")
    st.write(
        {
            "BJJ prima dei pesi": context.get("bjj_before_weights", False),
            "Frequenza BJJ": context.get("bjj_frequency", "-"),
            "Durata sessione (min)": context.get("session_duration_minutes", {}),
            "Politica intensita": context.get("intensity_policy", {}),
        }
    )


def render_workout(day: str, workout: dict) -> None:
    st.subheader(f"{day} - {workout.get('title', workout.get('workout_id', 'Workout'))}")
    for exercise in workout.get("exercises", []):
        exercise_card(exercise)
    conditional_note = workout.get("conditional_note")
    if conditional_note:
        st.info(conditional_note)


def render_progression_rules(data: dict) -> None:
    st.subheader("Regole di progressione")
    for rule in data.get("progression_rules", []):
        with st.container(border=True):
            st.markdown(f"**{rule.get('rule', 'Regola')}**")
            if "frequency_weeks" in rule:
                st.caption(f"Frequenza: {fmt_range([rule['frequency_weeks'].get('min', 0), rule['frequency_weeks'].get('max', 0)], ' settimane')}")
            st.write(rule.get("description", ""))


def render_optional_micro_sessions(data: dict) -> None:
    st.subheader("Micro-sessioni opzionali")
    for session in data.get("optional_micro_sessions", []):
        with st.container(border=True):
            st.markdown(f"### {session.get('title', 'Micro-sessione')}")
            freq = session.get("frequency_per_week", {})
            st.caption(f"Frequenza: {freq.get('min', 0)}-{freq.get('max', 0)} volte/settimana")
            for ex in session.get("exercises", []):
                details = [
                    f"Serie: {ex.get('sets', '-')}",
                    f"Ripetizioni: {fmt_range(ex.get('reps_range'))}",
                    f"Recupero: {fmt_range(ex.get('rest_seconds'), 's')}",
                ]
                st.markdown(f"- **{ex.get('name', '-') }** ({', '.join(details)})")
            condition = session.get("condition")
            if condition:
                st.info(condition)


def main() -> None:
    st.set_page_config(page_title="Scheda pesistica", layout="wide")
    st.title("Scheda pesistica")

    data = load_program("scheda.json")

    workouts_by_id = {w["workout_id"]: w for w in data.get("workouts", [])}
    weekly_template = data.get("weekly_template", [])
    day_to_workout = {
        item["day"]: workouts_by_id.get(item["workout_id"])
        for item in weekly_template
    }

    st.sidebar.header("Navigazione")
    selected_day = st.sidebar.selectbox("Giorno", list(day_to_workout.keys()), index=0)

    tab_overview, tab_workout, tab_rules, tab_micro = st.tabs(
        ["Panoramica", "Workout del giorno", "Progressione", "Micro-sessioni"]
    )

    with tab_overview:
        render_overview(data)

    with tab_workout:
        workout = day_to_workout.get(selected_day)
        if not workout:
            st.warning("Workout non trovato per il giorno selezionato.")
        else:
            render_workout(selected_day, workout)

    with tab_rules:
        render_progression_rules(data)

    with tab_micro:
        render_optional_micro_sessions(data)


if __name__ == "__main__":
    main()
