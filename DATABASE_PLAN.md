# Database Architecture Plan

## Target Engine
- Production: PostgreSQL via Supabase / Supavisor connection pooling
- Local & Staging: SQLite3

## Entity Relationship Overview
```
┌───────────────┐
│     User      │
└───────┬───────┘
        │ 1:1
        ▼
┌───────────────┐
│    Profile    │ (full_name, avatar_url, role, university, created_at)
└───────┬───────┘
        │ 1:N
        ├───► ┌────────────────────┐
        │     │  SolutionHistory   │ (solver_slug, input_payload, result_summary, created_at)
        │     └────────────────────┘
        │
        ├───► ┌────────────────────┐
        │     │    SavedProblem    │ (title, solver_slug, input_payload, notes, is_favorite)
        │     └────────────────────┘
        │
        ├───► ┌────────────────────┐
        │     │  PracticeAttempt   │ (topic_slug, question_id, is_correct, xp_earned, timestamp)
        │     └────────────────────┘
        │
        └───► ┌────────────────────┐
              │  UserProgressStats │ (total_solved, streak_days, total_xp, level)
              └────────────────────┘

┌───────────────┐
│ PracticeTopic │
└───────┬───────┘
        │ 1:N
        ▼
┌───────────────┐
│ QuizQuestion  │ (topic, question_text, options_json, correct_answer, explanation)
└───────────────┘
```
