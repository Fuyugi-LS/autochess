# Chess

A specialized chess game implemented in Python using the Pygame library. This is not just a standard chess game; it features a unique **"Guess the Move"** mechanic where the human player is tested against Stockfish Level 20. It also includes an advanced, randomized **3-Engine AI opponent system**.

![Untitled video - Made with Clipchamp](https://github.com/anuragjain-git/chess/assets/98457054/bfdea7e5-502b-4852-a2c9-115ea32e45da)

## Introduction

This is a customized implementation of a chess game with a graphical user interface. The game challenges players not only to beat an AI opponent but to play the absolute *best* moves possible. 

## Features

- **"Guess the Move" Human Constraints:**
  - Before a human player can make a move, a dedicated background Stockfish process calculates the optimal engine move at Skill Level 20. If the player attempts any move other than the optimal one, they are penalized with an "invalid move" message and must try again until they find the best move.

- **Dynamic 3-Engine AI Opponents:**
  - At the start of a match against the AI, the game randomly selects between 1 of 3 distinct engines:
    - **Stockfish:** A classic brute-force engine, randomly assigning an Elo between 1320 and 3190.
    - **Maia-Chess (Lc0):** A neural network engine trained on human games to play more like a human, randomly selecting a targeted ranking (e.g., maia1100, maia1500).
    - **Beginner Bot:** A customized Stockfish Level 0 engine (200-900 Elo) that has a high percentage chance of ignoring engine lines and playing completely random valid moves to simulate a confused beginner.

- **Graphical User Interface & Homepage:**
  - The game features a user-friendly graphical interface developed using the Pygame library, including a functional Homepage to select your side (White, Black, or Pass & Play).

- **Move Log & Engine Stats:**
  - Easily track the game's PGN in the UI, alongside real-time statistics regarding your current AI opponent's name, Elo, and specific engine parameters.

- **Checkmate, Stalemate, and Legal Moves:**
  - The game checks for conditions such as checkmate, stalemate, and legal moves, ensuring a fair and rule-compliant gameplay experience.

- **Advanced Chess Mechanics:**
  - Supports advanced chess mechanics, including pawn promotion, en passant, and castling for a more strategic and engaging experience.

- **Undo and Reset Board:**
  - Press Z for undo, R for reset

- **Variety of Chess Boards:**
  - Enjoy playing on different chess board colors, adding a personalized touch to your gaming experience.

- **Immersive Sounds and Images:**
  - Enhance your gaming experience with multiple piece move or capture sounds.

## Controls

- **Selecting/Moving:** Click on your piece, then click a valid highlighted square.
- **Undo:** Press `Z`
- **Reset:** Press `R`
- **"Guess the Move":** If you select a valid move but it is *not* the absolute best move according to Stockfish Level 20, the UI will visibly reject your move with an "invalid move" warning, and you must guess again.

## Application Setup

### Prerequisites:
- **Python 3.10+**
- **Stockfish Executable:** Placed inside `./stockfish/stockfish-windows-x86-64-avx2.exe`
- **Lc0 Engine:** Placed inside `./lc0-v0.32.1-windows-cpu-dnnl/lc0.exe`
- **Maia Weights:** Placed inside `./maia-chess/maia_weights/maia-xxxx.pb.gz`

1. Clone the repository:
   ```bash
   git clone https://github.com/Fuyugi-LS/chess-ai.git
   ```
2. Navigate to the project directory:
   ```bash
   cd chess-ai
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the game:
   ```bash
   python .\chess\main.py
   ```

## Configuration & Gameplay Loop

The gameplay loop is heavily driven by the new homepage UI. When starting `main.py`, you will be greeted with a homepage menu.
- Select **Play as White** to play the white pieces against a randomized AI opponent.
- Select **Play as Black** to play the black pieces against a randomized AI opponent.
- Select **Pass & Play** to play local multiplayer. *Note: the "Guess the Move" constraints apply to both players in this mode!*

### The 3-Engine System
Once a game starts against the AI, it will dynamically choose 1 of 3 engines to challenge you:
- **Stockfish:** Will select a random Elo between 1320 and 3190.
- **Maia-Chess:** Will load a random Lc0 network trained on human games (e.g., maia1100, maia1500).
- **Beginner Bot:** Will load Stockfish at Skill Level 0, but randomly assign an Elo between 200-900. It scales a "Randomness" percentage based on its Elo, meaning it has a high chance of completely ignoring Stockfish calculations and playing a randomly selected valid move instead, simulating a confused beginner.

## Acknowledgments & Fork Origin

This project is a customized fork originally based on the repository:
```bash
git clone https://github.com/anuragjain-git/chess-bot.git
```

Special thanks to the Pygame library for providing a straightforward and effective means to develop the graphical interface, and to the Stockfish & Leela Chess Zero (Lc0/Maia) communities for their incredible open-source chess engines that power the randomized AI system.

**Contributions and Feedback:**
This repository is currently **not available for direct contribution**. If you wish to work with this code, develop new features, or suggest improvements, please simply fork the repository!
