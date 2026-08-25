# TypeMaster

**TypeMaster** --- Windows uchun 100% offline ishlaydigan professional
typing-training desktop dastur.

Loyiha Monkeytype'dagi tezkor va minimal typing UX konsepsiyasidan
ilhomlanadi, lekin mustaqil mahsulot sifatida ishlab chiqiladi. Asosiy
farq: foydalanuvchining uzoq muddatli rivojlanishini kuzatish, analytics
va gamification.

## Product Vision

> Foydalanuvchini har kuni 5--15 daqiqa mashq qilishga undaydigan,
> tezlik va aniqlikni o'lchaydigan hamda real rivojlanishni
> ko'rsatadigan offline typing platforma.

## Core Stack

-   Python
-   Tkinter + ttk
-   SQLite
-   Tkinter Canvas charts
-   Python Standard Library imkon qadar ustuvor
-   PyInstaller
-   Windows 8 / 8.1 / 10 / 11

## Non-Goals for V1.0

-   Cloud backend
-   Online account synchronization
-   Online leaderboard
-   Browser application
-   AI/LLM dependency
-   Server-side API

## Documentation

  -----------------------------------------------------------------------
  File                                Purpose
  ----------------------------------- -----------------------------------
  `README.md`                         Project overview and agent entry
                                      point

  `TECHNICAL_SPECIFICATION.md`        Functional and technical
                                      requirements

  `ARCHITECTURE.md`                   System architecture and coding
                                      boundaries

  `PRODUCT_ROADMAP.md`                Product phases and release strategy

  `TASK_BACKLOG.md`                   Development tasks with P0/P1/P2
                                      priorities

  `AGENT_RULES.md`                    Coding, testing and delivery rules
                                      for coding agents
  -----------------------------------------------------------------------

## Development Principle

Kod yozishdan oldin architecture va contract aniqlanadi. Har bir task:

`TASK → DESIGN → IMPLEMENT → TEST → VERIFY → DONE`

ketma-ketligida bajariladi.

## Current Starting Point

**TM-001 --- Project Initialization**

Keyingi ishlar shu task backlog tartibida bajariladi.

## Development Setup

### System Compatibility
* Target compatibility: Windows 8 / 8.1 / 10 / 11. Compatibility verification is part of the release phase.
* Python requirement: Python 3.8+ recommended.

### Step-by-Step Installation

1. **Clone/open the workspace directory**:
   ```powershell
   cd d:\Proyekt\typing
   ```

2. **Initialize a virtual environment**:
   ```powershell
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   * On Windows PowerShell:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   * On Windows Command Prompt:
     ```cmd
     .venv\Scripts\activate.bat
     ```

4. **Install dependencies**:
   This project relies on the Python Standard Library and standard `tkinter` modules. No third-party dependencies are required for base features.
   ```powershell
   pip install -r requirements.txt
   ```

### Running the Application
Launch the Tkinter application container:
```powershell
python main.py
```

### Running Tests
Execute the smoke testing verification suite:
```powershell
python -m unittest discover -s tests
```
