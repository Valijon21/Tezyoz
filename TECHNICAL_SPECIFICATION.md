# TypeMaster v1.0 --- Technical Specification

**Document status:** Approved baseline\
**Version:** 1.0\
**Product:** TypeMaster\
**Target:** Windows 8 / 8.1 / 10 / 11\
**Mode:** 100% Offline

------------------------------------------------------------------------

## 1. Product Objective

TypeMaster foydalanuvchiga klaviaturada tez, aniq va barqaror yozishni
o'rganish imkonini beradigan desktop application.

Dastur faqat test natijasini emas, foydalanuvchining vaqt davomida
rivojlanishini ko'rsatadi:

-   WPM
-   Raw WPM
-   Accuracy
-   Errors
-   Practice time
-   Test count
-   Personal Best
-   Daily / Weekly / Monthly growth
-   XP
-   Level
-   Streak

Keyingi versiyalarda:

-   Achievements
-   Daily Missions
-   Weak Key Analysis
-   Heatmap
-   Learning Mode
-   Adaptive Difficulty

------------------------------------------------------------------------

## 2. Product Requirements

### P0 --- V1.0 Must Have

-   Registration
-   Login / Logout
-   SQLite local database
-   Typing test
-   15 / 30 / 60 / 120 second modes
-   WPM
-   Raw WPM
-   Accuracy
-   Error count
-   Result screen
-   Test history
-   Personal Best
-   Dashboard
-   Daily statistics
-   Weekly statistics
-   Monthly statistics
-   Growth calculation
-   XP
-   Level
-   Streak
-   Settings
-   Offline operation
-   Windows compatibility

### P1 --- V1.1

-   Achievements
-   Daily Missions
-   Heatmap
-   Key error statistics
-   Weak Key Analysis
-   Consistency analysis
-   Quotes
-   Custom Text
-   Russian language
-   Uzbek language

### P2 --- V2+

-   Learning Mode
-   Adaptive Difficulty
-   Smart recommendations
-   Cloud Sync
-   Online Leaderboard
-   Multiple profiles
-   Plugin architecture

------------------------------------------------------------------------

## 3. Functional Screens

### 3.1 Login

Fields:

-   Username
-   Password

Actions:

-   Login
-   Open Registration

Requirements:

-   Empty-field validation
-   Invalid credentials message
-   No plaintext password storage

### 3.2 Registration

Fields:

-   Username
-   Display Name
-   Password
-   Confirm Password

Validation:

-   Username required
-   Username unique
-   Password minimum length
-   Password confirmation must match
-   Password stored only as secure hash

### 3.3 Home

Must show:

-   User name
-   Current streak
-   Level
-   XP
-   Today's WPM
-   Today's accuracy
-   Today's test count
-   Today's practice time
-   Start Test action

### 3.4 Typing Test

Modes:

-   Time: 15s
-   Time: 30s
-   Time: 60s
-   Time: 120s

Live data:

-   WPM
-   Accuracy
-   Time
-   Typed progress

Behavior:

-   Timer starts on first valid typing event
-   Keyboard input is processed in memory
-   Database is not written on every keypress
-   Restart cancels current session
-   Completed test is saved once

### 3.5 Result

Show:

-   WPM
-   Raw WPM
-   Accuracy
-   Errors
-   Characters
-   Duration
-   XP earned
-   Personal Best status

Actions:

-   Retry
-   Dashboard

### 3.6 Dashboard

Periods:

-   Today
-   Week
-   Month
-   All Time

Metrics:

-   Average WPM
-   Best WPM
-   Average Accuracy
-   Best Accuracy
-   Tests
-   Practice Time
-   XP
-   Growth

Charts:

-   WPM trend
-   Accuracy trend
-   Practice activity
-   Future: heatmap

### 3.7 History

Columns:

-   Date
-   Mode
-   Duration
-   WPM
-   Accuracy
-   Errors
-   XP

Filters:

-   Today
-   Week
-   Month
-   All Time

### 3.8 Settings

P0:

-   Theme
-   Font family
-   Font size
-   Language
-   Sound enabled
-   Show live WPM
-   Show accuracy
-   Caret style

------------------------------------------------------------------------

## 4. Typing Engine

The typing engine is a domain component independent from the UI.

Lifecycle:

`IDLE → READY → RUNNING → COMPLETED`

or:

`RUNNING → ABORTED`

Responsibilities:

-   Load text
-   Start session
-   Receive key events
-   Compare expected and typed characters
-   Count correct characters
-   Count incorrect characters
-   Track elapsed time
-   Produce final raw statistics

The engine must not directly execute SQL queries.

------------------------------------------------------------------------

## 5. Metrics

### 5.1 WPM

Standard formula:

`WPM = (correct_characters / 5) / elapsed_minutes`

### 5.2 Raw WPM

`Raw WPM = (total_typed_characters / 5) / elapsed_minutes`

### 5.3 Accuracy

`Accuracy = correct_characters / total_typed_characters × 100`

If `total_typed_characters == 0`, accuracy is `0`.

### 5.4 Errors

Every incorrect character increments the error counter.

Future P1 data model may additionally capture:

-   Expected character
-   Typed character
-   Position
-   Timestamp

### 5.5 Growth

`Growth % = (current_period_average - previous_period_average) / previous_period_average × 100`

If the previous period is zero, growth must be handled explicitly and
must not divide by zero.

------------------------------------------------------------------------

## 6. Streak

A day counts as active when the user completes at least one test.

Rules:

-   If last active date is today: do not increment again.
-   If last active date is yesterday: increment streak.
-   Otherwise: start streak at 1.
-   Store longest streak separately.

------------------------------------------------------------------------

## 7. XP

Initial balancing:

  Event                   XP
  ------------------- ------
  Completed test         +50
  Accuracy \>= 95%       +20
  Accuracy \>= 98%       +40
  New Personal Best     +100
  Daily goal            +100

XP rules must prevent trivial farming. A final balancing pass is
required before release.

------------------------------------------------------------------------

## 8. Database

Database file:

`data/typemaster.db`

P0 tables:

-   `users`
-   `tests`
-   `daily_stats`
-   `personal_bests`
-   `user_settings`

P1 tables:

-   `achievements`
-   `user_achievements`
-   `daily_missions`
-   `user_missions`
-   `key_statistics`

------------------------------------------------------------------------

## 9. Database Schema

### users

``` text
id
username UNIQUE
display_name
password_hash
created_at
xp
level
current_streak
longest_streak
last_active_date
```

### tests

``` text
id
user_id
started_at
completed_at
mode
duration
language
difficulty
wpm
raw_wpm
accuracy
characters
correct_characters
incorrect_characters
xp_earned
is_personal_best
```

### daily_stats

``` text
id
user_id
date
tests_count
practice_seconds
average_wpm
best_wpm
average_accuracy
best_accuracy
total_characters
total_errors
xp_earned
```

### personal_bests

``` text
id
user_id
mode
duration
best_wpm
best_accuracy
achieved_at
```

### user_settings

``` text
id
user_id
theme
font_family
font_size
language
sound_enabled
show_live_wpm
show_accuracy
caret_style
```

------------------------------------------------------------------------

## 10. Data Integrity

A completed test should be committed transactionally.

Conceptual transaction:

`BEGIN → save test → update daily stats → update XP → update streak → update PB → COMMIT`

Any failure must result in rollback.

------------------------------------------------------------------------

## 11. Performance Requirements

Targets:

-   No network dependency
-   No database write per keypress
-   UI must remain responsive during typing
-   Timer must not use blocking `sleep()` on the Tkinter main thread
-   Use `after()` for UI scheduling
-   Keep dependencies minimal
-   Target startup under approximately 2 seconds where practical
-   Target low idle CPU usage
-   Avoid unnecessary background processes

These are engineering targets, not absolute guarantees until tested on
target hardware.

------------------------------------------------------------------------

## 12. Security

Even though the application is offline:

-   Passwords must never be stored in plaintext.
-   Use a secure password hashing scheme.
-   Use parameterized SQL.
-   Validate file paths.
-   Validate imported data.
-   Never expose raw tracebacks to normal users.
-   Write developer diagnostics to logs.

------------------------------------------------------------------------

## 13. Compatibility

Target operating systems:

-   Windows 8
-   Windows 8.1
-   Windows 10
-   Windows 11

Compatibility must be verified using the selected Python runtime, Tk
stack and PyInstaller version. Do not assume a current Python release
supports every target OS.

------------------------------------------------------------------------

## 14. Packaging

Release artifacts:

-   Portable EXE
-   Installer

Potential tools:

-   PyInstaller
-   Inno Setup

The final build must be tested on clean Windows installations.

------------------------------------------------------------------------

## 15. Definition of Done

A feature is Done only when:

-   Implemented
-   Unit tested where applicable
-   Integration tested where applicable
-   No traceback during normal use
-   No visible UI freeze
-   Database integrity verified
-   Error handling implemented
-   Code is placed in the correct architectural layer
-   No unnecessary dependency introduced
-   Documentation updated if behavior changed
