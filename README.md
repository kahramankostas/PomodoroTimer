# Pomodoro Timer

A powerful and feature-rich Pomodoro timer application built with Python and Tkinter (ttkbootstrap). It helps you manage your time effectively using the Pomodoro Technique.

## Features

-   **Full Control:** Custom settings for Work, Short Break, and Long Break durations to fit your workflow.
-   **Audio Alarm Support:**
    -   Plays MP3/WAV files when the timer ends.
    -   Toggle sound ON/OFF.
    -   Includes a default system beep if no file is selected or pygame is missing.
-   **Tabbed Interface:**
    -   **Timer & Settings:** Main timer, control buttons (Start, Pause, Skip, Reset), and configuration.
    -   **History:** View a log of your completed sessions with date, mode, duration, and notes.
    -   **Statistics:** Track your daily and total progress (sessions count and total time).
-   **Session Notes:** Quickly add notes about what you are working on during or after a session.
-   **Visual Themes:** distinct visual styles for "Work" (Red/Danger) and "Break" (Green/Success) modes.

## Prerequisites

-   Python 3.x
-   `ttkbootstrap` library for the modern UI.
-   `pygame` library for playing audio files (optional but recommended).

## Installation

1.  **Clone or Download** this repository.
2.  **Install Dependencies:**
    Open your terminal or command prompt and run:

    ```bash
    pip install ttkbootstrap pygame
    ```

## Usage

1.  **Run the Application:**
    Navigate to the project directory and run the script:

    ```bash
    python timer.pyw
    ```
    *(On Windows, you can simply double-click `timer.pyw` if Python is associated with `.pyw` files)*

2.  **Using the Timer:**
    -   Set your desired durations for Work, Short Break, and Long Break.
    -   Click **START** to begin the timer.
    -   Use **PAUSE** to temporarily stop and **SKIP** to move to the next interval immediately.
    -   **RESET** will restart the entire cycle sequence.

3.  **Sound Settings:**
    -   Go to the "Sound Alarm Settings" section.
    -   Check "Enable sound alarm when timer ends".
    -   Click "Select Sound" to choose a custom `.mp3` or `.wav` file (e.g., the included `alarm.mp3`).
    -   Click "Test" to verify the sound.

4.  **Tracking Progress:**
    -   Switch to the **History** tab to see past sessions.
    -   Switch to the **Statistics** tab to see your daily and all-time logs.

## Files

-   `timer.pyw`: The main application script.
-   `alarm.mp3`: A sample alarm sound file.
-   `README.md`: This documentation file.

## Data Storage

-   **History Log:** Saved to `~/pomodoro_records.csv` (in your user home directory).
-   **Settings:** Saved to `~/pomodoro_settings.txt` (in your user home directory).

## License

This project is open-source and free to use.
