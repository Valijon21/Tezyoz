# TypeMaster --- Software Architecture

## 1. Architecture Goal

TypeMaster desktop application should remain:

-   modular
-   testable
-   lightweight
-   offline
-   maintainable
-   compatible with Windows targets
-   independent of unnecessary frameworks

------------------------------------------------------------------------

## 2. High-Level Architecture

``` text
┌───────────────────────────────────────┐
│                 UI                    │
│ Login / Test / Result / Dashboard     │
└──────────────────┬────────────────────┘
                   │
┌──────────────────▼────────────────────┐
│              Services                 │
│ Auth / Test / Statistics / Gamification│
└──────────────────┬────────────────────┘
                   │
┌──────────────────▼────────────────────┐
│             Domain Engine             │
│ TypingEngine / Calculator / Timer     │
└──────────────────┬────────────────────┘
                   │
┌──────────────────▼────────────────────┐
│            Repositories               │
│ User / Test / Stats / Settings        │
└──────────────────┬────────────────────┘
                   │
┌──────────────────▼────────────────────┐
│               SQLite                  │
└───────────────────────────────────────┘
```

------------------------------------------------------------------------

## 3. Project Structure

``` text
TypeMaster/
│
├── main.py
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── application.py
│   └── config.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── schema.py
│   └── repositories/
│       ├── user_repository.py
│       ├── test_repository.py
│       ├── stats_repository.py
│       └── settings_repository.py
│
├── models/
│   ├── user.py
│   ├── test_result.py
│   ├── daily_stat.py
│   └── settings.py
│
├── engine/
│   ├── typing_engine.py
│   ├── timer.py
│   ├── calculator.py
│   └── text_generator.py
│
├── services/
│   ├── auth_service.py
│   ├── test_service.py
│   ├── statistics_service.py
│   ├── gamification_service.py
│   └── streak_service.py
│
├── ui/
│   ├── base.py
│   ├── login.py
│   ├── register.py
│   ├── home.py
│   ├── typing_test.py
│   ├── result.py
│   ├── dashboard.py
│   ├── history.py
│   ├── statistics.py
│   ├── profile.py
│   └── settings.py
│
├── charts/
│   ├── line_chart.py
│   ├── bar_chart.py
│   ├── progress_bar.py
│   └── heatmap.py
│
├── gamification/
│   ├── xp.py
│   ├── levels.py
│   ├── streak.py
│   └── achievements.py
│
├── data/
│   ├── english_1k.txt
│   ├── english_5k.txt
│   └── quotes.json
│
├── assets/
│   ├── fonts/
│   ├── icons/
│   └── sounds/
│
├── logs/
│
└── tests/
    ├── test_calculator.py
    ├── test_typing_engine.py
    ├── test_auth.py
    └── test_statistics.py
```

------------------------------------------------------------------------

## 4. Layer Responsibilities

### UI Layer

Responsible for:

-   rendering
-   user input
-   navigation
-   displaying validation messages
-   displaying service results

UI must not contain business rules or raw SQL.

### Service Layer

Responsible for use cases:

-   login
-   registration
-   complete test
-   update statistics
-   update XP
-   update streak
-   calculate dashboard data

### Engine Layer

Pure domain logic:

-   typing state
-   character matching
-   timer state
-   metrics

The engine should be testable without starting the full GUI.

### Repository Layer

Responsible for SQLite access.

Repositories contain SQL and database persistence logic.

### Model Layer

Simple domain/data structures.

------------------------------------------------------------------------

## 5. Main Classes

### TypingEngine

Responsibilities:

-   `start()`
-   `handle_key()`
-   `process_character()`
-   `finish()`
-   `abort()`
-   `get_live_stats()`

Must not know about Tkinter widgets or SQL.

### StatisticsCalculator

Responsibilities:

-   `calculate_wpm()`
-   `calculate_raw_wpm()`
-   `calculate_accuracy()`
-   `calculate_errors()`
-   `calculate_consistency()`

Functions should be deterministic where possible.

### TestService

Responsibilities:

-   create test
-   start test
-   finish test
-   save result
-   retrieve result

### StatisticsService

Responsibilities:

-   today stats
-   week stats
-   month stats
-   all-time stats
-   growth calculation

### GamificationService

Responsibilities:

-   calculate XP
-   update level
-   update streak
-   detect Personal Best

------------------------------------------------------------------------

## 6. Dependency Direction

Allowed:

``` text
UI → Services
Services → Engine
Services → Repositories
Repositories → Database
```

Avoid:

``` text
Engine → UI
Engine → SQLite
Repository → UI
Model → Tkinter
```

The domain engine must remain independent.

------------------------------------------------------------------------

## 7. Typing Session Flow

``` text
User opens test
        ↓
UI creates test configuration
        ↓
TypingEngine receives text/config
        ↓
User presses first valid key
        ↓
Timer starts
        ↓
TypingEngine processes key events in memory
        ↓
Timer reaches limit OR text is completed
        ↓
Engine returns raw result
        ↓
StatisticsCalculator calculates metrics
        ↓
TestService persists result
        ↓
Gamification updates XP/streak/PB
        ↓
Result screen
```

------------------------------------------------------------------------

## 8. Performance Rule

Do not execute SQLite queries for every keypress.

Correct:

``` text
keypress → RAM
test finished → SQLite
```

Incorrect:

``` text
keypress → SQLite
keypress → SQLite
keypress → SQLite
```

------------------------------------------------------------------------

## 9. Tkinter Threading Rule

Never block the main UI thread with long-running operations.

Use:

-   `after()`
-   short operations
-   carefully isolated background work only when necessary

Do not use blocking `time.sleep()` in GUI event flow.

------------------------------------------------------------------------

## 10. Charts

V1 should prefer lightweight Tkinter Canvas-based charts.

Reason:

-   fewer dependencies
-   smaller deployment
-   easier control of visual style
-   better compatibility strategy

Charts should receive prepared data from `StatisticsService`; chart
components must not query SQLite.

------------------------------------------------------------------------

## 11. Error Handling

User-facing layer:

-   friendly message
-   no traceback

Developer layer:

-   structured logging
-   exception context
-   timestamps
-   optional debug mode

Example:

``` text
logs/app.log
```

------------------------------------------------------------------------

## 12. Configuration

Centralize:

-   application version
-   paths
-   database location
-   default theme
-   default font
-   supported modes
-   XP constants
-   logging configuration

Avoid hard-coded values across many files.

------------------------------------------------------------------------

## 13. Testability

Pure calculations should be unit tested first.

Examples:

-   WPM
-   Raw WPM
-   Accuracy
-   Growth
-   XP
-   Level
-   Streak

Then integration tests:

-   Register → Login
-   Test → Save
-   Save → Dashboard
-   Test → XP
-   Test → Personal Best
