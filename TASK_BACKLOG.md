# TypeMaster --- Task Backlog

## Priority Definition

### P0

Required for V1.0. Product cannot ship without it.

### P1

Important enhancement. Planned for V1.1.

### P2

Future roadmap. Do not implement unless explicitly approved.

------------------------------------------------------------------------

# Sprint 0 --- Foundation

## TM-001 --- Project Initialization

**Priority:** P0\
**Status:** TODO

Tasks:

-   Create repository
-   Create Python virtual environment
-   Establish project directories
-   Create `main.py`
-   Create `.gitignore`
-   Create README
-   Verify Tkinter starts

Acceptance:

-   Application launches a basic window.
-   Directory structure matches architecture.
-   No unnecessary dependency is introduced.

------------------------------------------------------------------------

## TM-002 --- Configuration

**Priority:** P0\
**Status:** TODO

Tasks:

-   Create `app/config.py`
-   Centralize paths
-   Centralize version
-   Define supported modes
-   Define default settings

Acceptance:

-   No duplicated application constants across modules.

------------------------------------------------------------------------

## TM-003 --- SQLite Connection

**Priority:** P0\
**Status:** TODO

Tasks:

-   SQLite connection manager
-   Database path management
-   Transaction helper
-   Connection lifecycle

Acceptance:

-   Database opens successfully.
-   Connection errors are handled.
-   No database file is created in source root unintentionally.

------------------------------------------------------------------------

## TM-004 --- Database Schema

**Priority:** P0\
**Status:** TODO

Create:

-   users
-   tests
-   daily_stats
-   personal_bests
-   user_settings

Acceptance:

-   Schema initializes automatically.
-   Foreign keys are configured.
-   Basic CRUD tests pass.

------------------------------------------------------------------------

# Sprint 1 --- Authentication

## TM-005 --- Registration UI

**Priority:** P0

## TM-006 --- Password Hashing

**Priority:** P0

## TM-007 --- Login Service

**Priority:** P0

## TM-008 --- Current User Session

**Priority:** P0

## TM-009 --- Logout

**Priority:** P0

Acceptance for Sprint:

-   Register user
-   Close application
-   Reopen
-   Login
-   Logout
-   Login failure handled correctly

------------------------------------------------------------------------

# Sprint 2 --- Typing Engine

## TM-010 --- Text Loader

**Priority:** P0

## TM-011 --- Test Configuration

**Priority:** P0

Modes:

-   15s
-   30s
-   60s
-   120s

## TM-012 --- TypingEngine

**Priority:** P0

## TM-013 --- Keyboard Event Processing

**Priority:** P0

## TM-014 --- Character Comparison

**Priority:** P0

## TM-015 --- Timer

**Priority:** P0

## TM-016 --- WPM Calculator

**Priority:** P0

## TM-017 --- Raw WPM

**Priority:** P0

## TM-018 --- Accuracy

**Priority:** P0

## TM-019 --- Error Counter

**Priority:** P0

## TM-020 --- Test Completion

**Priority:** P0

Acceptance:

-   Test starts on first valid typing event.
-   Keypresses are processed without visible lag.
-   Correct/incorrect counts are accurate.
-   Timer completes test correctly.
-   No SQL write occurs per keypress.

------------------------------------------------------------------------

# Sprint 3 --- Results

## TM-021 --- Result Screen

**Priority:** P0

## TM-022 --- Save Test

**Priority:** P0

## TM-023 --- Personal Best

**Priority:** P0

## TM-024 --- XP Calculation

**Priority:** P0

## TM-025 --- Streak Update

**Priority:** P0

Acceptance:

-   Completed result is saved exactly once.
-   PB is detected correctly.
-   XP is updated transactionally.
-   Streak follows date rules.

------------------------------------------------------------------------

# Sprint 4 --- Dashboard

## TM-026 --- Today Statistics

**Priority:** P0

## TM-027 --- Weekly Statistics

**Priority:** P0

## TM-028 --- Monthly Statistics

**Priority:** P0

## TM-029 --- Growth Calculation

**Priority:** P0

## TM-030 --- WPM Chart

**Priority:** P0

## TM-031 --- Accuracy Chart

**Priority:** P0

## TM-032 --- Practice Time

**Priority:** P0

## TM-033 --- Dashboard Cards

**Priority:** P0

Acceptance:

-   Dashboard matches database data.
-   Empty states are handled.
-   Date boundaries are correct.
-   Charts never crash on missing data.

------------------------------------------------------------------------

# Sprint 5 --- History

## TM-034 --- Test History

**Priority:** P0

## TM-035 --- History Filters

**Priority:** P0

## TM-036 --- Personal Best Page

**Priority:** P0

------------------------------------------------------------------------

# Sprint 6 --- UX

## TM-037 --- Theme System

**Priority:** P0

## TM-038 --- Font System

**Priority:** P0

## TM-039 --- Keyboard Shortcuts

**Priority:** P0

## TM-040 --- DPI Scaling

**Priority:** P0

## TM-041 --- Window Resize Behavior

**Priority:** P0

## TM-042 --- User-Friendly Error Handling

**Priority:** P0

------------------------------------------------------------------------

# Sprint 7 --- Gamification

## TM-043 --- Level System

**Priority:** P0

## TM-044 --- XP Progress Bar

**Priority:** P0

## TM-045 --- Streak UI

**Priority:** P0

## TM-046 --- Daily Goal

**Priority:** P1

## TM-047 --- Achievements

**Priority:** P1

## TM-048 --- Daily Missions

**Priority:** P1

------------------------------------------------------------------------

# Sprint 8 --- Advanced Analytics

## TM-049 --- Key Error Statistics

**Priority:** P1

## TM-050 --- Weak Key Detection

**Priority:** P1

## TM-051 --- Consistency

**Priority:** P1

## TM-052 --- Heatmap

**Priority:** P1

## TM-053 --- Advanced Statistics

**Priority:** P1

------------------------------------------------------------------------

# Sprint 9 --- Release

## TM-054 --- Windows 8 Verification

**Priority:** P0

## TM-055 --- Windows 8.1 Verification

**Priority:** P0

## TM-056 --- Windows 10 Verification

**Priority:** P0

## TM-057 --- Windows 11 Verification

**Priority:** P0

## TM-058 --- PyInstaller Build

**Priority:** P0

## TM-059 --- Portable EXE

**Priority:** P0

## TM-060 --- Installer

**Priority:** P0

## TM-061 --- Backup/Restore

**Priority:** P1

## TM-062 --- Final QA

**Priority:** P0

------------------------------------------------------------------------

# Task Execution Rule

Agents must not skip task dependencies.

Correct sequence:

`TM-001 → TM-002 → TM-003 → TM-004 → ...`

An agent may work on independent tasks in parallel only when the
architecture allows it and no dependency is violated.
