# A Simple Text-Based Game with Typing Effect ⌨️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 About This Project

This is my very first programming project: a simple **text-based adventure game** built using **Python**. The game features a classic choose-your-own-adventure style narrative with branching choices that influence the story's progression. A key visual element is the **typewriter effect** that simulates text being typed out in real-time, enhancing the nostalgic feel of old-school text adventures.

The primary goal of this project was to learn foundational Python concepts, understand basic game logic, and get hands-on experience with external libraries like `Pygame` for specific effects (such as playing sounds for typing). It also serves as my introduction to Git and GitHub for version control and project sharing.

---

## ✨ Features

* **Interactive Storyline:** Make choices that lead to different paths and endings.
* **Typewriter Text Effect:** Characters appear one by one, mimicking an old typewriter.
* **Immersive Sound:** A subtle keyboard typing sound plays along with the typewriter effect (using `mixkit-fast-laptop-keyboard-typing-1392.wav`).
* **Simple Game Loop:** Demonstrates fundamental game structure in Python.
* **Modular Design:** Basic separation of concerns for game logic and assets.

---

## 🚀 How to Run the Game

To play this game locally on your machine, follow these simple steps:

### Prerequisites

Make sure you have [Python 3.x](https://www.python.org/downloads/) installed on your system.

### Installation

1.  **Clone the repository:**
    Open your terminal or Command Prompt and run:
    ```bash
    git clone [https://github.com/Demolisher-hero/A-simple-text-based-game-with-typing-writing-effect.git](https://github.com/Demolisher-hero/A-simple-text-based-game-with-typing-writing-effect.git)
    ```
2.  **Navigate into the project directory:**
    ```bash
    cd A-simple-text-based-game-with-typing-writing-effect
    ```
3.  **Create and activate a virtual environment (recommended):**
    A virtual environment isolates your project dependencies from your global Python installation.
    ```bash
    python -m venv venv
    ```
    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
    source venv/bin/activate
        ```
    You should see `(venv)` at the beginning of your terminal prompt, indicating the environment is active.
4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Game

With the virtual environment active and dependencies installed, run the main game file:

```bash
python main.py
