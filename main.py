import numpy as np
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Function to print Sudoku board (for debugging)
@app.route('/board', methods=['GET'])
def Print_Board(board):
    for i in range(9):
        for j in range(9):
            if j == 0:
                print("|", end='')
            if j != 8:
                print(board[i, j], end=' ')
            else:
                print(board[i, j], end='')
            if (j + 1) % 3 == 0:
                print("|", end='')
        if (i + 1) % 3 == 0:
            print("\n---------------------", end='')
        print()

# Function to find the first empty cell
def Find_Empty_Cell(board):
    for i in range(9):
        for j in range(9):
            if board[i, j] == 0:
                return i, j
    return -1, -1

# Function to check validity of a number placement in the Sudoku grid
def Check_Validity(board, row, col, num):
    row_start = (row // 3) * 3
    col_start = (col // 3) * 3
    if num in board[:, col] or num in board[row, :]:
        return False
    if num in board[row_start:row_start + 3, col_start:col_start + 3]:
        return False
    return True

# Function to solve Sudoku using backtracking
def Solve_Sudoku(board):
    row, col = Find_Empty_Cell(board)
    if row == -1:  # No empty cells, puzzle is solved
        return True

    for num in range(1, 10):
        if Check_Validity(board, row, col, num):
            board[row, col] = num
            if Solve_Sudoku(board):
                return True
            board[row, col] = 0  # Backtrack

    return False  # No valid solution

# Route to select difficulty
@app.route('/', methods=['GET', 'POST'])
def select_difficulty():
    if request.method == 'POST':
        difficulty = request.form['difficulty']
        return redirect(url_for('Generate_Unsolved_Puzzle', difficulty=difficulty))
    return render_template('select_difficulty.html')

# Route to generate the unsolved Sudoku puzzle based on difficulty
@app.route('/generate', methods=['GET'])
def Generate_Unsolved_Puzzle():
    difficulty = request.args.get('difficulty', default='Easy', type=str)
    board = np.zeros((9, 9), dtype=int)
    solved_board = np.zeros((9, 9), dtype=int)
    count, done = 0, False
    
    # Define the upper limits based on difficulty
    if difficulty == "Easy":
        upper_limit = 35
    elif difficulty == "Medium":
        upper_limit = 41
    else:
        upper_limit = 47

    # Step 1: Generate a completely solved Sudoku puzzle
    while not Solve_Sudoku(board):
        board = np.zeros((9, 9), dtype=int)  # Reset if not solvable

    solved_board = board.copy()

    # Step 2: Shuffle the row blocks (groups of 3 rows)
    row_blocks = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # List of all rows in blocks
    blocks = [row_blocks[0:3], row_blocks[3:6], row_blocks[6:9]]  # Group rows into blocks
    random.shuffle(blocks)  # Shuffle the blocks
    
    # Step 3: Rearrange the board based on shuffled row blocks
    shuffled_board = np.zeros((9, 9), dtype=int)
    
    # Assign shuffled blocks back to the shuffled_board
    shuffled_board[0:3] = solved_board[blocks[0][0]:blocks[0][2] + 1]
    shuffled_board[3:6] = solved_board[blocks[1][0]:blocks[1][2] + 1]
    shuffled_board[6:9] = solved_board[blocks[2][0]:blocks[2][2] + 1]

    # Step 4: Remove numbers from the solved puzzle to create the unsolved puzzle
    while count < upper_limit:
        i, j = random.randint(0, 8), random.randint(0, 8)
        
        if shuffled_board[i, j] != 0:
            backup = shuffled_board[i, j]  # Backup the number
            shuffled_board[i, j] = 0  # Remove the number temporarily
            
            # Check if the puzzle is still solvable
            board_copy = shuffled_board.copy()
            if Solve_Sudoku(board_copy):
                count += 1  # Increment count if puzzle remains solvable
            else:
                shuffled_board[i, j] = backup  # Restore the number if not solvable

    return render_template('index.html', board=shuffled_board.tolist(), difficulty=difficulty)

# Main function to run Flask app
if __name__ == "__main__":
    app.run(debug=True)
