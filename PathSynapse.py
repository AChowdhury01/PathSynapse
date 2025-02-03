import tkinter as tk
from tkinter import messagebox
import json
import os

class NumberGridGame:
    SAVE_FILE = "game_save.json"

    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Number Grid Game")
        
        # Constants
        self.GRID_SIZE = 7
        self.INNER_GRID_START = 1
        self.INNER_GRID_END = 6
        self.TOTAL_NUMBERS = 25
        
        # Game state
        self.buttons = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.grid_values = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.current_number = 1
        self.level = 1
        self.move_history = []
        self.username = ""

        # Show start screen
        self.show_start_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_start_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Welcome to Number Grid Game!", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Start Game", command=self.ask_username).pack(pady=10)
        tk.Button(self.root, text="Load Game", command=self.load_game).pack(pady=10)
        tk.Button(self.root, text="View Rules", command=self.show_rules).pack(pady=10)

    def show_rules(self):
        rules_window = tk.Toplevel(self.root)
        rules_window.title("Game Rules")
        rules_window.geometry("500x300")
        tk.Label(rules_window, text="Game Rules", font=("Arial", 16, "bold"), pady=10).pack()
        rules_text = (
            "Level 1:\n"
            "1. Place numbers 2-25 in adjacent cells in ascending order\n"
            "2. Use only the inner 5x5 grid\n\n"
            "Level 2:\n"
            "1. Place numbers in outer grid cells\n"
            "2. Must match row/column ends or diagonal rules\n\n"
            "Level 3:\n"
            "1. Return to inner grid with outer numbers intact\n"
            "2. Numbers must match with outer blue cells in same row/column\n"
            "3. Must be adjacent to previous number"
        )
        tk.Label(rules_window, text=rules_text, font=("Arial", 12), justify="left").pack(padx=20, pady=10)
        tk.Button(rules_window, text="Close", command=rules_window.destroy).pack(pady=10)

    def ask_username(self):
        self.clear_screen()
        tk.Label(self.root, text="Enter your name to start the game:", font=("Arial", 14)).pack(pady=20)
        entry = tk.Entry(self.root, font=("Arial", 14))
        entry.pack(pady=10)
        tk.Button(self.root, text="Start", command=lambda: self.start_game(entry.get())).pack(pady=10)

    def start_game(self, username):
        if not username.strip():
            messagebox.showerror("Error", "Name cannot be empty")
            return
        self.username = username
        self.create_game_interface()
        self.set_starting_position()

    def create_game_interface(self):
        self.clear_screen()
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                color = self.get_cell_color(row, col)
                button = tk.Button(
                    self.root,
                    text="",
                    width=5,
                    height=2,
                    bg=color,
                    command=lambda r=row, c=col: self.handle_cell_click(r, c)
                )
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

        # Control buttons
        control_frame = tk.Frame(self.root)
        control_frame.grid(row=self.GRID_SIZE, column=0, columnspan=self.GRID_SIZE, pady=10)
        
        tk.Button(control_frame, text="Rollback", command=self.rollback_move).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Save Game", command=self.save_game).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Reset Game", command=self.reset_game).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Main Menu", command=self.show_start_screen).pack(side=tk.LEFT, padx=5)

    def get_cell_color(self, row, col):
        if (row == 0 or row == self.GRID_SIZE - 1) and (col == 0 or col == self.GRID_SIZE - 1):
            return 'yellow'
        elif (row < self.INNER_GRID_START or row >= self.INNER_GRID_END or 
              col < self.INNER_GRID_START or col >= self.INNER_GRID_END):
            return 'lightblue'
        return 'lightgray'

    def set_starting_position(self):
        start_row, start_col = 4, 2
        self.grid_values[start_row][start_col] = 1
        self.buttons[start_row][start_col].config(text="1", fg="red")
        self.move_history.append((start_row, start_col, 1))
        self.current_number = 2

    def handle_cell_click(self, row, col):
        if self.level == 1:
            self.handle_level1_move(row, col)
        elif self.level == 2:
            self.handle_level2_move(row, col)
        else:  # level 3
            self.handle_level3_move(row, col)

    def handle_level1_move(self, row, col):
        if not self.is_inner_grid(row, col):
            messagebox.showerror("Error", "Must place numbers in the inner grid during Level 1")
            return
            
        if self.grid_values[row][col] != 0:
            messagebox.showerror("Error", "Cell already occupied")
            return
            
        if not self.is_adjacent_to_last_number(row, col):
            messagebox.showerror("Error", "Must place number adjacent to the previous number")
            return
            
        self.place_number(row, col)
        
        if self.current_number > self.TOTAL_NUMBERS:
            messagebox.showinfo("Level Complete", "Level 1 Complete! Moving to Level 2")
            self.level = 2
            self.current_number = 2

    def handle_level2_move(self, row, col):
        if not self.is_valid_level2_position(row, col):
            messagebox.showerror("Error", "Invalid position for Level 2")
            return
            
        if not self.is_valid_level2_placement(row, col):
            messagebox.showerror("Error", "Number must be placed at row/column ends or valid diagonal corners")
            return
            
        self.place_number(row, col)
        
        if self.current_number > self.TOTAL_NUMBERS:
            messagebox.showinfo("Level Complete", "Level 2 Complete! Moving to Level 3")
            self.level = 3
            self.prepare_level3()

    def handle_level3_move(self, row, col):
        if not self.is_inner_grid(row, col):
            messagebox.showerror("Error", "Must place numbers in the inner grid during Level 3")
            return
            
        if self.grid_values[row][col] != 0:
            messagebox.showerror("Error", "Cell already occupied")
            return
            
        if not self.is_adjacent_to_last_number(row, col):
            messagebox.showerror("Error", "Must place number adjacent to the previous number")
            return
            
        if not self.is_valid_level3_placement(row, col):
            messagebox.showerror("Error", "Number must be placed in a row/column with matching end number")
            return
            
        self.place_number(row, col)
        
        if self.current_number > self.TOTAL_NUMBERS:
            messagebox.showinfo("Congratulations", "Game Complete! You've finished all levels!")

    def is_inner_grid(self, row, col):
        return (self.INNER_GRID_START <= row < self.INNER_GRID_END and 
                self.INNER_GRID_START <= col < self.INNER_GRID_END)

    def is_adjacent_to_last_number(self, row, col):
        last_row, last_col = None, None
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                if self.grid_values[r][c] == self.current_number - 1:
                    last_row, last_col = r, c
                    break
        if last_row is None:
            return False
        return abs(row - last_row) <= 1 and abs(col - last_col) <= 1

    def is_valid_level2_position(self, row, col):
        return (row == 0 or row == self.GRID_SIZE - 1 or 
                col == 0 or col == self.GRID_SIZE - 1)

    def is_valid_level2_placement(self, row, col):
        inner_row, inner_col = None, None
        for r in range(self.INNER_GRID_START, self.INNER_GRID_END):
            for c in range(self.INNER_GRID_START, self.INNER_GRID_END):
                if self.grid_values[r][c] == self.current_number:
                    inner_row, inner_col = r, c
                    break
        
        if inner_row is None:
            return False

        is_on_main_diagonal = (inner_row - self.INNER_GRID_START == 
                             inner_col - self.INNER_GRID_START)
        is_on_anti_diagonal = (inner_row - self.INNER_GRID_START + 
                             inner_col - self.INNER_GRID_START == 4)
        
        if ((row == 0 and col == 0) or (row == self.GRID_SIZE-1 and col == self.GRID_SIZE-1)):
            return is_on_main_diagonal
        if ((row == 0 and col == self.GRID_SIZE-1) or (row == self.GRID_SIZE-1 and col == 0)):
            return is_on_anti_diagonal
            
        relative_row = inner_row - self.INNER_GRID_START
        relative_col = inner_col - self.INNER_GRID_START
        
        if row == 0 or row == self.GRID_SIZE-1:
            return col == relative_col + self.INNER_GRID_START
        if col == 0 or col == self.GRID_SIZE-1:
            return row == relative_row + self.INNER_GRID_START
            
        return False

    def is_valid_level3_placement(self, row, col):
        number_to_place = self.current_number
        
        # Check blue cells in this column
        if (self.grid_values[0][col] == number_to_place or 
            self.grid_values[self.GRID_SIZE-1][col] == number_to_place):
            return True
        
        # Check blue cells in this row
        if (self.grid_values[row][0] == number_to_place or 
            self.grid_values[row][self.GRID_SIZE-1] == number_to_place):
            return True
                
        # Check diagonal rule
        if self.is_on_diagonal(row, col) and self.has_matching_diagonal_end(row, col, number_to_place):
            return True
                
        return False
                
        # Check diagonal rule
        if self.is_on_diagonal(row, col) and self.has_matching_diagonal_end(row, col, number_to_place):
            return True
                
        return False

    def is_on_diagonal(self, row, col):
        # Adjust coordinates to inner grid reference
        inner_row = row - self.INNER_GRID_START
        inner_col = col - self.INNER_GRID_START
        
        # Check if on main diagonal
        if inner_row == inner_col:
            return True
            
        # Check if on anti-diagonal
        if inner_row + inner_col == 4:  # 4 is the size of inner grid - 1
            return True
            
        return False

    def has_matching_diagonal_end(self, row, col, number):
        # If on main diagonal, check top-left and bottom-right corners
        if (row - self.INNER_GRID_START) == (col - self.INNER_GRID_START):
            if (self.grid_values[0][0] == number or 
                self.grid_values[self.GRID_SIZE-1][self.GRID_SIZE-1] == number):
                return True
                
        # If on anti-diagonal, check top-right and bottom-left corners
        if (row - self.INNER_GRID_START) + (col - self.INNER_GRID_START) == 4:
            if (self.grid_values[0][self.GRID_SIZE-1] == number or 
                self.grid_values[self.GRID_SIZE-1][0] == number):
                return True
                
        return False

    def prepare_level3(self):
        # Clear inner grid except for number 1
        for row in range(self.INNER_GRID_START, self.INNER_GRID_END):
            for col in range(self.INNER_GRID_START, self.INNER_GRID_END):
                if self.grid_values[row][col] != 1:
                    self.grid_values[row][col] = 0
                    self.buttons[row][col].config(text="")
        
        self.current_number = 2

    def place_number(self, row, col):
        self.grid_values[row][col] = self.current_number
        self.buttons[row][col].config(text=str(self.current_number))
        self.move_history.append((row, col, self.current_number))
        self.current_number += 1

    def rollback_move(self):
        if not self.move_history:
            messagebox.showinfo("Info", "No moves to rollback")
            return
            
        row, col, number = self.move_history.pop()
        self.grid_values[row][col] = 0
        self.buttons[row][col].config(text="")
        self.current_number = number
        
        if self.level == 2 and self.current_number == 2:
            self.level = 1
            self.current_number = self.TOTAL_NUMBERS
        elif self.level == 3 and self.current_number == 2:
            self.level = 2
            self.current_number = self.TOTAL_NUMBERS

    def reset_game(self):
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                self.grid_values[row][col] = 0
                self.buttons[row][col].config(text="")
        
        self.level = 1
        self.move_history.clear()
        self.set_starting_position()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def save_game(self):
        data = {
            "username": self.username,
            "grid_values": self.grid_values,
            "current_number": self.current_number,
            "level": self.level,
            "move_history": self.move_history
        }
        with open(self.SAVE_FILE, "w") as file:
            json.dump(data, file)
        messagebox.showinfo("Success", "Game Successfully Saved!")

    def load_game(self):
        if not os.path.exists(self.SAVE_FILE):
            messagebox.showerror("Error", "No saved game found!")
            return

        try:
            with open(self.SAVE_FILE, "r") as f:
                save_data = json.load(f)

            # Ask for username
            input_username = self.ask_username_input("Enter your username to load game:")
            if not input_username:
                return
                
            if input_username != save_data.get("username"):
                messagebox.showerror("Error", "No saved game found for this username!")
                return

            # Load the saved data
            self.username = save_data["username"]
            self.grid_values = save_data["grid_values"]
            self.current_number = save_data["current_number"]
            self.level = save_data["level"]
            self.move_history = save_data["move_history"]

            # Create game interface and restore the state
            self.create_game_interface()
            self.restore_game_state()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading game: {str(e)}")

    def ask_username_input(self, prompt):
        username = None
        
        def on_submit():
            nonlocal username
            username = entry.get()
            popup.destroy()
            
        popup = tk.Toplevel(self.root)
        popup.title("Load Game")
        popup.grab_set()  # Make the popup modal
        
        tk.Label(popup, text=prompt).pack(pady=10)
        entry = tk.Entry(popup)
        entry.pack(pady=5)
        tk.Button(popup, text="Submit", command=on_submit).pack(pady=10)
        
        # Center the popup
        popup.geometry("300x150")
        popup.transient(self.root)
        self.root.wait_window(popup)
        
        return username

    def restore_game_state(self):
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                value = self.grid_values[row][col]
                if value != 0:
                    self.buttons[row][col].config(text=str(value))

# Create and run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGridGame(root)
    root.mainloop()