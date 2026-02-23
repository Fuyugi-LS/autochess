import random
import subprocess
import os

STOCKFISH_PROCESS = None
HINT_STOCKFISH_PROCESS = None
MAIA_PROCESS = None

CURRENT_ENGINE_NAME = "Stockfish"
CURRENT_ELO = 1320 # Default
CURRENT_SKILL_LEVEL = 0
BEGINNER_RANDOM_CHANCE = 0.0

MAIA_TARGET_ELO = None
MAIA_LICHESS_NAME = None

def initialize_engines():
    global STOCKFISH_PROCESS, HINT_STOCKFISH_PROCESS, MAIA_PROCESS, CURRENT_ENGINE_NAME, MAIA_TARGET_ELO, MAIA_LICHESS_NAME
    
    # 0 = Stockfish, 1 = Maia, 2 = Beginner Bot
    engine_choice = random.randint(0, 2)
        
    stockfish_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stockfish", "stockfish-windows-x86-64-avx2.exe")
    lc0_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lc0-v0.32.1-windows-cpu-dnnl", "lc0.exe")
    maia_weights_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "maia-chess", "maia_weights")

    try:
        if engine_choice == 0:
            CURRENT_ENGINE_NAME = "Stockfish"
            STOCKFISH_PROCESS = subprocess.Popen(
                [stockfish_path],
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1
            )
            
            # Initialize UCIs for Opponent
            _send_command("uci")
            while True:
                line = STOCKFISH_PROCESS.stdout.readline().strip()
                if line == "uciok":
                    break
        elif engine_choice == 2:
            CURRENT_ENGINE_NAME = "Beginner Bot"
            STOCKFISH_PROCESS = subprocess.Popen(
                [stockfish_path],
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1
            )
            
            # Initialize UCIs for Opponent
            _send_command("uci")
            while True:
                line = STOCKFISH_PROCESS.stdout.readline().strip()
                if line == "uciok":
                    break
        else:
            CURRENT_ENGINE_NAME = "Maia"
            # Pick a random maia weight
            available_weights = [f for f in os.listdir(maia_weights_dir) if f.endswith('.pb.gz')]
            chosen_weight = random.choice(available_weights)
            
            # Parse maia-1100.pb.gz into 1100
            elo_str = chosen_weight.replace('maia-', '').replace('.pb.gz', '')
            MAIA_TARGET_ELO = elo_str
            
            # Map ELO to maia bot name (e.g. 1100 -> maia1, 1500 -> maia5, 1900 -> maia9)
            # We map the hundreds digit if it perfectly aligns, else default to maia1
            elo_int = int(elo_str)
            if elo_int == 1100: MAIA_LICHESS_NAME = "maia1"
            elif elo_int == 1500: MAIA_LICHESS_NAME = "maia5"
            elif elo_int == 1900: MAIA_LICHESS_NAME = "maia9"
            else: MAIA_LICHESS_NAME = f"maia{elo_str[:2]}" # Just use first two digits as fallback
            
            weight_path = os.path.join(maia_weights_dir, chosen_weight)
            
            MAIA_PROCESS = subprocess.Popen(
                [lc0_path, f"--weights={weight_path}"],
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1
            )
            
            _send_maia_command("uci")
            while True:
                line = MAIA_PROCESS.stdout.readline().strip()
                if line == "uciok":
                    break
                
        # Start Hint Stockfish
        HINT_STOCKFISH_PROCESS = subprocess.Popen(
            [stockfish_path],
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1
        )
        
        _send_hint_command("uci")
        while True:
            line = HINT_STOCKFISH_PROCESS.stdout.readline().strip()
            if line == "uciok":
                break
                
        # Force Hint Stockfish to absolute maximum
        _send_hint_command("setoption name UCI_LimitStrength value true")
        _send_hint_command("setoption name UCI_Elo value 3190")
        _send_hint_command("setoption name Skill Level value 20")
        
    except Exception as e:
        print(f"Failed to start engine subprocesses: {e}")

def set_elo(elo):
    global CURRENT_ELO, CURRENT_SKILL_LEVEL, BEGINNER_RANDOM_CHANCE
    CURRENT_ELO = elo
    
    if CURRENT_ENGINE_NAME == "Beginner Bot":
        # Beginner bot uses maximum randomness scaled inversely by Elo
        BEGINNER_RANDOM_CHANCE = max(0, (1000 - elo) / 1000)
        # Lock its stockfish fallback to essentially absolute worst 
        CURRENT_SKILL_LEVEL = 0
        _send_command("setoption name UCI_LimitStrength value true")
        _send_command(f"setoption name UCI_Elo value 1320")
        _send_command(f"setoption name Skill Level value 0")

    elif CURRENT_ENGINE_NAME == "Stockfish":
        # Stockfish 16+ uses UCI_LimitStrength and UCI_Elo
        _send_command("setoption name UCI_LimitStrength value true")
        _send_command(f"setoption name UCI_Elo value {elo}")
        
        # As a fallback for older stockfish or just to be sure, map elo to Skill Level (0-20)
        # 1320 -> 0, 3190 -> 20
        skill_level = int(max(0, min(20, (elo - 1320) / ((3190 - 1320) / 20))))
        CURRENT_SKILL_LEVEL = skill_level
        _send_command(f"setoption name Skill Level value {skill_level}")
    
def get_current_engine_stats():
    return {
        "name": CURRENT_ENGINE_NAME,
        "stockfish_elo": CURRENT_ELO,
        "stockfish_level": CURRENT_SKILL_LEVEL,
        "maia_elo": MAIA_TARGET_ELO,
        "maia_name": MAIA_LICHESS_NAME,
        "beginner_random_chance": BEGINNER_RANDOM_CHANCE
    }
    
def get_elo():
    return CURRENT_ELO

def get_skill_level():
    return CURRENT_SKILL_LEVEL

def _send_command(command):
    if STOCKFISH_PROCESS and STOCKFISH_PROCESS.poll() is None:
        STOCKFISH_PROCESS.stdin.write(command + "\n")
        STOCKFISH_PROCESS.stdin.flush()

def _send_maia_command(command):
    if MAIA_PROCESS and MAIA_PROCESS.poll() is None:
        MAIA_PROCESS.stdin.write(command + "\n")
        MAIA_PROCESS.stdin.flush()

def _send_hint_command(command):
    if HINT_STOCKFISH_PROCESS and HINT_STOCKFISH_PROCESS.poll() is None:
        HINT_STOCKFISH_PROCESS.stdin.write(command + "\n")
        HINT_STOCKFISH_PROCESS.stdin.flush()

def quit_stockfish():
    global STOCKFISH_PROCESS, HINT_STOCKFISH_PROCESS, MAIA_PROCESS
    if STOCKFISH_PROCESS:
        _send_command("quit")
        STOCKFISH_PROCESS.terminate()
        STOCKFISH_PROCESS = None
    if MAIA_PROCESS:
        _send_maia_command("quit")
        MAIA_PROCESS.terminate()
        MAIA_PROCESS = None
    if HINT_STOCKFISH_PROCESS:
        _send_hint_command("quit")
        HINT_STOCKFISH_PROCESS.terminate()
        HINT_STOCKFISH_PROCESS = None

def findRandomMoves(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMove(gs, validMoves, returnQueue):
    active_process = MAIA_PROCESS if CURRENT_ENGINE_NAME == "Maia" else STOCKFISH_PROCESS
    
    if active_process is None:
        returnQueue.put(findRandomMoves(validMoves))
        return

    if CURRENT_ENGINE_NAME == "Beginner Bot":
        # Check if we should make a totally random move
        if random.random() < BEGINNER_RANDOM_CHANCE:
            print("Beginner bot is feeling confused...")
            returnQueue.put(findRandomMoves(validMoves))
            return

    # Build the UCI move history to give to Stockfish
    move_history = []
    for move in gs.moveLog:
        move_history.append(move.getUCINotation())
        
    position_cmd = "position startpos"
    if len(move_history) > 0:
         position_cmd += " moves " + " ".join(move_history)
         
    if CURRENT_ENGINE_NAME == "Maia":
        _send_maia_command(position_cmd)
        _send_maia_command("go nodes 1") # Maia specific search command
    else:
        _send_command(position_cmd)
        _send_command("go movetime 1000") # Calculate for 1 second max
    
    best_move_str = None
    while True:
        try:
            line = active_process.stdout.readline().strip()
            if not line: # Process closed or EOF
                break
            if line.startswith("bestmove"):
                parts = line.split()
                if len(parts) >= 2:
                    best_move_str = parts[1]
                break
        except Exception:
            break
            
    # Match the stockfish move string to our validMoves objects
    best_move_obj = None
    if best_move_str and best_move_str != "(none)":
        for move in validMoves:
            if move.getUCINotation() == best_move_str:
                best_move_obj = move
                break
                
    if best_move_obj is None:
        # Fallback if there's any mismatch
        if len(validMoves) > 0:
             best_move_obj = validMoves[0]
             
    returnQueue.put(best_move_obj)

def findOptimalMove(gs, validMoves, returnQueue):
    active_process = HINT_STOCKFISH_PROCESS
    if active_process is None:
        returnQueue.put(findRandomMoves(validMoves))
        return

    # Build the UCI move history to give to Stockfish
    move_history = []
    for move in gs.moveLog:
        move_history.append(move.getUCINotation())
        
    position_cmd = "position startpos"
    if len(move_history) > 0:
         position_cmd += " moves " + " ".join(move_history)
         
    _send_hint_command(position_cmd)
    _send_hint_command("go movetime 1000") # Calculate for 1 second max
    
    best_move_str = None
    while True:
        try:
            line = active_process.stdout.readline().strip()
            if not line: # Process closed or EOF
                break
            if line.startswith("bestmove"):
                parts = line.split()
                if len(parts) >= 2:
                    best_move_str = parts[1]
                break
        except Exception:
            break
            
    # Match the stockfish move string to our validMoves objects
    best_move_obj = None
    if best_move_str and best_move_str != "(none)":
        for move in validMoves:
            if move.getUCINotation() == best_move_str:
                best_move_obj = move
                break
                
    if best_move_obj is None:
        # Fallback if there's any mismatch
        if len(validMoves) > 0:
             best_move_obj = validMoves[0]
             
    returnQueue.put(best_move_obj)
