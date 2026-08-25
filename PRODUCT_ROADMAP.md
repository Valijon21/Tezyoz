# TypeMaster --- Product Roadmap

## Product Vision

TypeMaster should become an offline typing coach, not merely a typing
benchmark.

The user should be able to answer:

> Am I faster than last week?\
> Am I making fewer mistakes?\
> Which keys are weak?\
> Am I practicing consistently?\
> What should I practice today?

------------------------------------------------------------------------

# Phase 0 --- Foundation

**Priority:** P0

Objective: stable technical foundation.

Deliverables:

-   project structure
-   configuration
-   SQLite
-   schema
-   repository pattern
-   logging
-   test framework
-   initial application shell

Exit criteria:

-   application starts
-   database initializes
-   no unnecessary dependencies
-   architecture boundaries are established

------------------------------------------------------------------------

# Phase 1 --- Authentication

**Priority:** P0

Features:

-   Registration
-   Login
-   Logout
-   Current user session
-   Secure password hashing
-   Validation

Exit criteria:

-   user can register
-   user can close/reopen app
-   user can log in
-   password is never stored as plaintext

------------------------------------------------------------------------

# Phase 2 --- Typing Core

**Priority:** P0

Features:

-   text generator
-   15/30/60/120 second modes
-   keyboard event handling
-   timer
-   WPM
-   Raw WPM
-   Accuracy
-   Errors
-   completion state
-   restart

Exit criteria:

-   typing feels immediate
-   timer is accurate enough for product use
-   no UI freeze
-   results are deterministic for known inputs

------------------------------------------------------------------------

# Phase 3 --- Results and Persistence

**Priority:** P0

Features:

-   result screen
-   save completed test
-   history
-   Personal Best
-   XP
-   streak

Exit criteria:

-   every completed test is persisted
-   aborted tests are not incorrectly counted
-   PB detection works
-   streak logic works

------------------------------------------------------------------------

# Phase 4 --- Analytics Dashboard

**Priority:** P0

Features:

-   Today
-   Week
-   Month
-   All Time
-   average WPM
-   best WPM
-   accuracy
-   test count
-   practice time
-   growth
-   WPM chart
-   accuracy chart

Exit criteria:

-   dashboard values match database
-   date boundaries work correctly
-   empty periods do not crash
-   growth does not divide by zero

------------------------------------------------------------------------

# Phase 5 --- Gamification

**Priority:** P0/P1

V1:

-   XP
-   Level
-   Streak
-   Daily Goal

V1.1:

-   Achievements
-   Missions
-   badges

Goal:

Make progress visible and encourage healthy daily practice.

------------------------------------------------------------------------

# Phase 6 --- Learning Analytics

**Priority:** P1

Features:

-   key error tracking
-   weak key detection
-   consistency
-   slow-word detection
-   practice recommendations

Example:

``` text
Your weak keys:
G — 18 errors
D — 14 errors
P — 9 errors

Recommended practice:
G D G P D G P
```

------------------------------------------------------------------------

# Phase 7 --- Localization and Content

**Priority:** P1

Add:

-   English
-   Russian
-   Uzbek

Content:

-   1K words
-   5K words
-   quotes
-   custom text

All content remains local.

------------------------------------------------------------------------

# Phase 8 --- Release Engineering

**Priority:** P0

Targets:

-   Windows 8
-   Windows 8.1
-   Windows 10
-   Windows 11

Deliverables:

-   portable EXE
-   installer
-   clean installation test
-   upgrade test
-   database migration strategy
-   crash logging
-   backup/restore

------------------------------------------------------------------------

# Phase 9 --- Future Product

**Priority:** P2

Potential features:

-   Adaptive Learning
-   Cloud Sync
-   Online leaderboard
-   Multi-device sync
-   Multiple profiles
-   advanced recommendations
-   optional online account

These are explicitly outside V1.0 scope.

------------------------------------------------------------------------

# Success Metrics

Product metrics:

-   daily active practice
-   average session duration
-   tests per user
-   7-day streak retention
-   WPM improvement
-   accuracy improvement
-   weekly practice consistency

Technical metrics:

-   crash-free sessions
-   startup time
-   UI responsiveness
-   database integrity
-   Windows compatibility
