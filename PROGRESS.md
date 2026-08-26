# Tezyoz (TypeMaster) Project Progress Tracking

This file monitors development advancement, tracking completed sprints, verifying finished deliverables, and listing remaining modules in the backlog.

---

## 📊 Summary Metrics

- **Total Backlog Tasks**: 62
- **Completed Tasks**: 20 (32.3%)
- **Remaining Tasks**: 42 (67.7%)
- **Active Sprint**: Sprint 3 — Results (In Progress)

---

## 🏁 Completed Sprints & Deliverables

### Sprint 0 — Foundation (Completed: 4/4)
- [x] **TM-001 --- Project Initialization**: Modular workspace, `.gitignore`, launcher entry `main.py`, requirements.
- [x] **TM-002 --- Configuration**: Mark constants, window dimensions, typing modes, XP rewards.
- [x] **TM-003 --- SQLite Connection**: Thread-safe database managers, connection wrappers with transactions.
- [x] **TM-004 --- Database Schema**: Relational structures for user data, test scores, stats, and default configs.

### Sprint 1 — Authentication (Completed: 5/5)
- [x] **TM-005 --- Registration UI**: Real-time validated sign-up panels and form screens.
- [x] **TM-006 --- Password Hashing**: Zero-dependency standard library PBKDF2-HMAC-SHA256 password hashing.
- [x] **TM-007 --- Login Service & UI**: Transactional user signups (users + settings) and credentials matching.
- [x] **TM-008 --- Current User Session**: JSON-based persistency auto login active user bypass.
- [x] **TM-009 --- Logout**: Redirect flows, session unlinking, and UI logouts.

### Sprint 2 — Typing Engine (Completed: 11/11)
- [x] **TM-010 --- Text Loader**: Reads space/newline separated typing target vocabularies from files with memory fallbacks.
- [x] **TM-011 --- Test Configuration**: Validates and tracks language options and duration parameters for typing practice.
- [x] **TM-012 --- TypingEngine**: State machine coordinator tracking typing inputs, errors, and real-time accuracy and words per minute calculations.
- [x] **TM-013 --- Keyboard Event Processing**: Validates and filters Tkinter keypress inputs, ignoring control/utility shortcuts and parsing backspace/printable keys.
- [x] **TM-014 --- Character Comparison**: Evaluates typed inputs against target prompt characters, computing correct, incorrect, and untyped state designations.
- [x] **TM-015 --- Timer**: Manages countdown constraints, elapsed margins, and disables keystroke modifications upon test expiration.
- [x] **TM-016 --- WPM Calculator**: Real-time Net Words Per Minute calculator (correct_characters / 5) / elapsed_minutes.
- [x] **TM-017 --- Raw WPM**: Real-time Raw Words Per Minute calculator (total_typed_characters / 5) / elapsed_minutes.
- [x] **TM-018 --- Accuracy**: Real-time Accuracy calculator (correct_characters / total_typed_characters) * 100.
- [x] **TM-019 --- Error Counter**: Logs and increments mistake keystrokes correctly.
- [x] **TM-020 --- Test Completion**: Handles duration bounds, disables edits, and triggers completion callbacks.

---

## 🚀 Active & Remaining Backlog

### Sprint 3 — Results (Remaining: 5)
- [ ] **TM-021 --- Result Screen** (P0) — *Next in Queue*
- [ ] **TM-022 --- Save Test** (P0)
- [ ] **TM-023 --- Personal Best** (P0)
- [ ] **TM-024 --- XP Calculation** (P0)
- [ ] **TM-025 --- Streak Update** (P0)

### Sprint 4 — Dashboard (Remaining: 8)
- [ ] TM-026 --- Today Statistics (P0)
- [ ] TM-027 --- Weekly Statistics (P0)
- [ ] TM-028 --- Monthly Statistics (P0)
- [ ] TM-029 --- Growth Calculation (P0)
- [ ] TM-030 --- WPM Chart (P0)
- [ ] TM-031 --- Accuracy Chart (P0)
- [ ] TM-032 --- Practice Time (P0)
- [ ] TM-033 --- Dashboard Cards (P0)

### Sprint 5 — History (Remaining: 3)
- [ ] TM-034 --- Test History (P0)
- [ ] TM-035 --- History Filters (P0)
- [ ] TM-036 --- Personal Best Page (P0)

### Sprint 6 — UX (Remaining: 6)
- [ ] TM-037 --- Theme System (P0)
- [ ] TM-038 --- Font System (P0)
- [ ] TM-039 --- Keyboard Shortcuts (P0)
- [ ] TM-040 --- DPI Scaling (P0)
- [ ] TM-041 --- Window Resize Behavior (P0)
- [ ] TM-042 --- User-Friendly Error Handling (P0)

### Sprint 7 — Gamification (Remaining: 6)
- [ ] TM-043 --- Level System (P0)
- [ ] TM-044 --- XP Progress Bar (P0)
- [ ] TM-045 --- Streak UI (P0)
- [ ] TM-046 --- Daily Goal (P1)
- [ ] TM-047 --- Achievements (P1)
- [ ] TM-048 --- Daily Missions (P1)

### Sprint 8 — Advanced Analytics (Remaining: 5)
- [ ] TM-049 --- Key Error Statistics (P1)
- [ ] TM-050 --- Weak Key Detection (P1)
- [ ] TM-051 --- Consistency (P1)
- [ ] TM-052 --- Heatmap (P1)
- [ ] TM-053 --- Advanced Statistics (P1)

### Sprint 9 — Release (Remaining: 9)
- [ ] TM-054 to TM-057 --- Windows 8/8.1/10/11 Verification (P0)
- [ ] TM-058 --- PyInstaller Build (P0)
- [ ] TM-059 --- Portable EXE (P0)
- [ ] TM-060 --- Installer (P0)
- [ ] TM-061 --- Backup/Restore (P1)
- [ ] TM-062 --- Final QA (P0)
