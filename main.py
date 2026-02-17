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


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .block-container {
                max-width: 760px;
                padding-top: 1rem;
                padding-bottom: 4rem;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }
            .hero {
                background: linear-gradient(135deg, #121826 0%, #1f2a44 100%);
                border-radius: 16px;
                padding: 1rem 1rem 0.8rem 1rem;
                margin-bottom: 0.8rem;
                border: 1px solid rgba(255,255,255,0.08);
            }
            .hero h1 {
                margin: 0;
                font-size: 1.35rem;
            }
            .hero p {
                margin: 0.35rem 0 0 0;
                color: #c9d1e6;
                font-size: 0.92rem;
            }
            .kpi {
                background: #111827;
                border: 1px solid #253047;
                border-radius: 12px;
                padding: 0.55rem 0.75rem;
                margin-bottom: 0.5rem;
            }
            .kpi strong {
                font-size: 1rem;
            }
            @media (max-width: 640px) {
                .hero h1 { font-size: 1.2rem; }
                .hero p { font-size: 0.86rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(data: dict) -> None:
    context = data.get("context", {})
    duration = context.get("session_duration_minutes", {})
    duration_text = f"{duration.get('min', '-')}-{duration.get('max', '-')} min"
    st.markdown(
        f"""
        <div class="hero">
            <h1>{data.get("program_name", "Scheda pesistica")}</h1>
            <p>Sessioni smart post-BJJ - durata target: {duration_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_kpis(data: dict) -> None:
    weekly_count = len(data.get("weekly_template", []))
    micro_count = len(data.get("optional_micro_sessions", []))
    rules_count = len(data.get("progression_rules", []))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="kpi"><small>Workout / settimana</small><br><strong>'
                    f"{weekly_count}</strong></div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi"><small>Regole progressione</small><br><strong>'
                    f"{rules_count}</strong></div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi"><small>Micro sessioni</small><br><strong>'
                    f"{micro_count}</strong></div>", unsafe_allow_html=True)


def render_meta(sets: int | str | None, reps: str, rir: str, rest: str) -> None:
    left, right = st.columns(2)
    with left:
        st.markdown(f"**Serie:** `{sets if sets is not None else '-'}`")
        st.markdown(f"**Rep:** `{reps}`")
    with right:
        st.markdown(f"**RIR:** `{rir}`")
        st.markdown(f"**Recupero:** `{rest}`")


def render_notes(notes: list[str]) -> None:
    if not notes:
        return
    st.caption("Note")
    st.markdown("\n".join(f"- {note}" for note in notes))


def render_single_exercise_block(
    title: str,
    sets: int | str | None,
    reps: str,
    rir: str,
    rest: str,
    notes: list[str],
    label: str | None = None,
) -> None:
    with st.container(border=True):
        if label:
            st.caption(label)
        st.markdown(f"#### {title}")
        render_meta(sets, reps, rir, rest)
        render_notes(notes)


def exercise_card(exercise: dict) -> None:
    if exercise.get("superset"):
        with st.container(border=True):
            st.markdown(f"#### {exercise.get('name', 'Superset')}")
            pair = exercise.get("pair", [])
            for idx, sub in enumerate(pair, start=1):
                st.markdown(f"**{idx}) {sub.get('name', 'Esercizio')}**")
                render_meta(
                    sets=sub.get("sets", "-"),
                    reps=fmt_range(sub.get("reps_range")),
                    rir=fmt_range(sub.get("target_RIR")),
                    rest=fmt_range(sub.get("rest_seconds"), "s"),
                )
                render_notes(sub.get("notes", []))
                if idx < len(pair):
                    st.divider()
        return

    if exercise.get("choose_one"):
        st.markdown(f"#### {exercise.get('name', 'Scegli 1 opzione')}")
        for option in exercise.get("options", []):
            reps_or_time = (
                fmt_range(option.get("duration_seconds_range"), "s")
                if "duration_seconds_range" in option
                else fmt_range(option.get("reps_range"))
            )
            reps_label = f"tempo {reps_or_time}" if "duration_seconds_range" in option else reps_or_time
            render_single_exercise_block(
                title=option.get("variant", "-"),
                sets=option.get("sets", "-"),
                reps=reps_label,
                rir=fmt_range(option.get("target_RIR")),
                rest=fmt_range(option.get("rest_seconds"), "s"),
                notes=option.get("notes", []),
                label="Scegli una variante",
            )
        return

    reps_value = (
        f"Tempo {fmt_range(exercise.get('duration_seconds_range'), 's')}"
        if "duration_seconds_range" in exercise
        else fmt_range(exercise.get("reps_range"))
    )
    render_single_exercise_block(
        title=exercise.get("name", "Esercizio"),
        sets=exercise.get("sets", "-"),
        reps=reps_value,
        rir=fmt_range(exercise.get("target_RIR")),
        rest=fmt_range(exercise.get("rest_seconds"), "s"),
        notes=exercise.get("notes", []),
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
    st.set_page_config(page_title="Scheda pesistica", layout="centered")
    inject_styles()

    data = load_program("scheda.json")
    render_hero(data)
    render_quick_kpis(data)

    workouts_by_id = {w["workout_id"]: w for w in data.get("workouts", [])}
    weekly_template = data.get("weekly_template", [])
    day_to_workout = {
        item["day"]: workouts_by_id.get(item["workout_id"])
        for item in weekly_template
    }
    ordered_days = list(day_to_workout.keys())

    st.markdown("### Seleziona giorno")
    selected_day = st.radio(
        "Giorno",
        ordered_days,
        horizontal=True,
        label_visibility="collapsed",
    )

    tab_workout, tab_rules, tab_micro = st.tabs(
        ["Workout del giorno", "Progressione", "Micro-sessioni"]
    )

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
