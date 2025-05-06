import random
import requests
import time
import tkinter as tk
from tkinter import messagebox
# from celeb import celebration  # Uncomment if you have a celebration module

# -----------------------------
# Original game logic functions
# -----------------------------

def choose_word():
    words = ["python", "hangman", "developer","science", "analyst", "programmer"]
    return random.choice(words)

def hint(word):
    try:
        response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
        data = response.json()
        meaning = data[0]['meanings'][0]['definitions'][0]['definition']
    except Exception as e:
        meaning = "No hint available."
    return meaning

def display_word(word, guessed_letters):
    return " ".join([letter if letter in guessed_letters else "_" for letter in word])

# ASCII art for hangman pictures
hangman_pics = [
    """
    -------
          |
          |
          |
          |
          |
    =========
    """,
    """
    -------
     |    |
          |
          |
          |
          |
    =========
    """,
    """ 
    -------
     |    |
     O    |
          |
          |
          |
    =========
    """,
    """ 
    -------
     |    |
     O    |
     |    |
          |
          |
    =========
    """,
    """ 
    -------
     |    |
     O    |
    /|    |
          |
          |
    =========
    """,
    """ 
    -------
     |    |
     O    |
    /|\   |
          |
          |
    =========
    """,
    """ 
    -------
     |    |
     O    |
    /|\   |
     |    |
          |
    =========
    """,
    """ 
    -------
     |    |
     O    |
    /|\   |
     |    |
    /     |
    =========
    """,
    """ 
    -------
     |    |
     O    |
    /|\   |
     |    |
    / \   |
    =========
    """ 
]

def animation(idx):
    """Return the ASCII art for the current hangman stage."""
    if idx < len(hangman_pics):
        return hangman_pics[idx]
    else:
        return hangman_pics[-1]

# ASCII art frames for loss animation
loss_moves = [
    """ 
    -------
     |    |
     O    |
    /|\   |
     |    |
    / \   |
    =========
    """,
    """ 
    -------
          |
     O    |
    /|\   |
     |    |
    / \   |
    =========
    """,
    """ 
    -------
          |
          |
          |
    O\|/  |
    /|\|  |
    =========
    """
]

# ASCII art frames for win animation (man moves his hands up and down)
win_moves = [
    """
     -----
     |    |
     O    |
    /|\   |
     |    |
    / \   |
     =========
     """,
    """
     -----
     |    |
    _O_   |
     |    |
     |    |
    / \   |
     =========
     """,
    """
     -----
     |    |
    \O/   |
     |    |
     |    |
    / \   |
     =========
     """,
     """
     -----
  🎉🎊🥳    
    \O/   
     |    
     |    
    / \    
     =========
     """
]

# -----------------------------
# Tkinter GUI Implementation
# -----------------------------

class HangmanGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Hangman Game")
        # Set the overall background color for the window
        self.master.configure(bg="#34495e")  # Dark blue-gray background
        self.total_score = 0  # Accumulates score over multiple games

        # Initialize game state variables
        self.word = ""
        self.guessed_letters = []
        self.attempts = 8
        self.score = 80
        self.idx = 0
        self.game_over = False

        # Create and place GUI widgets with improved styling
        self.hangman_label = tk.Label(master, text="", font=("Courier", 16),
                                      justify="left", bg="#34495e", fg="#ecf0f1")
        self.hangman_label.pack(pady=10)

        self.word_label = tk.Label(master, text="", font=("Helvetica", 20, "bold"),
                                   bg="#34495e", fg="#ecf0f1")
        self.word_label.pack(pady=10)

        self.info_label = tk.Label(master, text="", font=("Helvetica", 14),
                                   bg="#34495e", fg="#ecf0f1")
        self.info_label.pack(pady=5)

        self.score_label = tk.Label(master, text="Score: 0", font=("Helvetica", 14),
                                    bg="#34495e", fg="#ecf0f1")
        self.score_label.pack(pady=5)

        self.attempts_label = tk.Label(master, text="Attempts left: 8", font=("Helvetica", 14),
                                       bg="#34495e", fg="#ecf0f1")
        self.attempts_label.pack(pady=5)

        self.hint_label = tk.Label(master, text="", font=("Helvetica", 12),
                           bg="#34495e", fg="#f1c40f")  # Yellow color for hints
        self.hint_label.pack(pady=5)

        self.message_label = tk.Label(master, text="", font=("Helvetica", 12),
                                      bg="#34495e", fg="#e74c3c")  # Red for error/info messages
        self.message_label.pack(pady=5)

        self.input_frame = tk.Frame(master, bg="#34495e")
        self.input_frame.pack(pady=10)

        self.guess_entry = tk.Entry(self.input_frame, font=("Helvetica", 16),
                                    bg="#ecf0f1", fg="#2c3e50", relief="flat")
        self.guess_entry.pack(side="left", padx=5)

        self.guess_button = tk.Button(self.input_frame, text="Guess", command=self.guess_letter,
                                      font=("Helvetica", 14), bg="#2980b9", fg="white",
                                      activebackground="#3498db", activeforeground="white", relief="flat")
        self.guess_button.pack(side="left", padx=5)

        self.play_again_button = tk.Button(master, text="Play Again", command=self.new_game,
                                           font=("Helvetica", 14), bg="#27ae60", fg="white",
                                           activebackground="#2ecc71", activeforeground="white", relief="flat")
        self.play_again_button.pack(pady=10)
        self.play_again_button.config(state="disabled")

        self.quit_button = tk.Button(master, text="Quit", command=self.quit_game,
                                     font=("Helvetica", 14), bg="#c0392b", fg="white",
                                     activebackground="#e74c3c", activeforeground="white", relief="flat")
        self.quit_button.pack(pady=5)

        # Start the first game
        self.new_game()

    def new_game(self):
        """Reset the game state for a new game."""
        self.word = choose_word()
        self.guessed_letters = []
        self.attempts = 8
        self.score = 80
        self.idx = 0
        self.game_over = False
        self.hint_label.config(text="")
        self.message_label.config(text="")
        self.guess_entry.config(state="normal")
        self.guess_button.config(state="normal")
        self.play_again_button.config(state="disabled")
        self.update_display()

    def update_display(self):
        """Update all game-related displays in the GUI."""
        # Update the hangman ASCII art display
        self.hangman_label.config(text=animation(self.idx))
        # Update the word display (with guessed letters revealed)
        self.word_label.config(text=display_word(self.word, self.guessed_letters))
        # Update the attempts and score labels
        self.attempts_label.config(text=f"Attempts left: {self.attempts}")
        self.score_label.config(text=f"Score: {self.score} | Total Score: {self.total_score}")
        # Clear the entry field for the next guess
        self.guess_entry.delete(0, tk.END)

    def guess_letter(self):
        """Process the player's guessed letter."""
        if self.game_over:
            return

        guess = self.guess_entry.get().lower()
        if len(guess) != 1 or not guess.isalpha():
            self.message_label.config(text="Please enter a single valid letter.")
            self.guess_entry.delete(0, tk.END)
            return

        if guess in self.guessed_letters:
            self.message_label.config(text="You already guessed that letter.")
            self.guess_entry.delete(0, tk.END)
            return

        self.guessed_letters.append(guess)
        self.message_label.config(text="")

        if guess not in self.word:
            # Wrong guess: update attempts, score, and hangman image index
            self.attempts -= 1
            self.score -= 10
            self.idx += 1
            self.message_label.config(text="Wrong guess!")
            self.update_display()
            # Prompt for a hint
            if messagebox.askyesno("Hint", "Do you require a hint?"):
                hint_text = hint(self.word)
                self.hint_label.config(text=f"Hint: {hint_text}")
            else:
                self.hint_label.config(text="")
        else:
            self.message_label.config(text="Good guess!")
            self.update_display()

        # Check for win: all unique letters in the word have been guessed
        if set(self.word) <= set(self.guessed_letters):
            self.message_label.config(text=f"Congratulations! You guessed the word: {self.word}")
            self.total_score += self.score
            # celebration("Win", display_time=1000)  # Uncomment if using the celebration module
            self.score_label.config(text=f"Score: {self.score} | Total Score: {self.total_score}")
            self.game_over = True
            self.end_game(win=True)
            return

        # Check for loss: no more attempts left
        if self.attempts == 0:
            self.message_label.config(text=f"Game Over! The word was: {self.word}")
            self.total_score += 0  # Losing yields 0 score (as in the original logic)
            self.game_over = True
            self.end_game(win=False)
            return

    def end_game(self, win):
        """Handle end-of-game tasks: disable input, run animations, and enable new game."""
        # Disable further guessing
        self.guess_entry.config(state="disabled")
        self.guess_button.config(state="disabled")
        # Update final score display
        self.score_label.config(text=f"Score: {self.score} | Total Score: {self.total_score}")
        if win:
            self.animate_win_gui(0)
        else:
            self.animate_loss_gui(0)
        # Enable the Play Again button so the user can start a new game
        self.play_again_button.config(state="normal")

    def animate_loss_gui(self, frame_index):
        """Animate the loss sequence by updating the hangman display."""
        if frame_index < len(loss_moves):
            self.hangman_label.config(text=loss_moves[frame_index])
            self.master.after(700, lambda: self.animate_loss_gui(frame_index + 1))
        else:
            # After animation, display the final hangman picture
            self.hangman_label.config(text=animation(len(hangman_pics) - 1))
            
    def animate_win_gui(self, frame_index):
        """Animate the win sequence by updating the hangman display with celebratory moves."""
        if frame_index < len(win_moves):
            self.hangman_label.config(text=win_moves[frame_index])
            self.master.after(700, lambda: self.animate_win_gui(frame_index + 1))
        else:
            # After animation, display the final win picture
            self.hangman_label.config(text=win_moves[-1])
            
    def quit_game(self):
        """Show a thank you message with total score and quit the game."""
        messagebox.showinfo("Goodbye", f"Thank you for playing!\nYour Total Score: {self.total_score}")
        self.master.quit()

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGUI(root)
    root.mainloop()
