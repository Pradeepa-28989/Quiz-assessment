import time      # For timer functionality
import os        # For clearing the screen
import threading # For running the timer in background

# Import our database functions from database.py
from database import (
    setup_database,
    insert_questions,
    get_all_questions,
    save_result,
    get_leaderboard
)



def clear_screen():
    """Clears the terminal screen for a clean look."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Prints the app header/banner."""
    print("=" * 60)
    print("       🐍 PYTHON QUIZ ASSESSMENT 🐍")
    print("         Test Your Python Knowledge!")
    print("=" * 60)


def print_separator():
    """Prints a divider line."""
    print("-" * 60)


class QuizTimer:
    """
    This class manages our countdown timer.
    We use threading so the timer runs WHILE the user can still type.
    Think of it like a stopwatch running in the background.
    """

    def __init__(self, total_seconds):
        self.total_seconds = total_seconds   # Total time allowed
        self.start_time = None               # When we started
        self.is_running = False              # Is the timer active?

    def start(self):
        """Starts the timer."""
        self.start_time = time.time()
        self.is_running = True

    def stop(self):
        """Stops the timer."""
        self.is_running = False

    def get_elapsed(self):
        """Returns how many seconds have passed."""
        if self.start_time is None:
            return 0
        return int(time.time() - self.start_time)

    def get_remaining(self):
        """Returns how many seconds are left."""
        elapsed = self.get_elapsed()
        remaining = self.total_seconds - elapsed
        return max(0, remaining)  # Never go below 0

    def is_expired(self):
        """Returns True if time is up."""
        return self.get_remaining() <= 0

    def format_time(self, seconds):
        """Converts seconds to MM:SS format like 02:30."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def display(self):
        """Returns a formatted timer string."""
        remaining = self.get_remaining()
        formatted = self.format_time(remaining)

        # Warning colors using text symbols
        if remaining <= 30:
            return f"⚠️  TIME LEFT: {formatted}  ⚠️"
        else:
            return f"⏱️  TIME LEFT: {formatted}"



def display_question(question_data, question_num, total, timer):
    """
    Displays a single question with options.

    question_data is a tuple from the database:
    (id, question, optA, optB, optC, optD, correct_answer, category)
    """
    clear_screen()
    print_banner()

    # Unpack the question tuple
    q_id, question, opt_a, opt_b, opt_c, opt_d, correct, category = question_data

    # Show progress and timer
    print(f"\n  📚 Category: {category}")
    print(f"  Question {question_num} of {total}")
    print(f"  {timer.display()}")
    print_separator()

    # Show the question
    print(f"\n  ❓ {question}\n")

    # Show the 4 options
    print(f"  A) {opt_a}")
    print(f"  B) {opt_b}")
    print(f"  C) {opt_c}")
    print(f"  D) {opt_d}")
    print()


def get_user_answer():
    """
    Gets the user's answer (A, B, C, or D).
    Keeps asking until a valid answer is given.
    """
    valid_answers = ['A', 'B', 'C', 'D']

    while True:
        answer = input("  Your answer (A/B/C/D) or Q to quit: ").strip().upper()

        if answer == 'Q':
            return 'Q'  # Quit signal
        elif answer in valid_answers:
            return answer
        else:
            print("  ❌ Invalid! Please enter A, B, C, or D")



def display_result(player_name, score, total, time_taken, answers_log):
    """Shows the quiz results after it's finished."""
    clear_screen()
    print_banner()

    percentage = (score / total) * 100
    minutes = time_taken // 60
    seconds = time_taken % 60

    print(f"\n  🎉 QUIZ COMPLETE, {player_name}!")
    print_separator()
    print(f"  ✅ Score:      {score} / {total}")
    print(f"  📊 Percentage: {percentage:.1f}%")
    print(f"  ⏱️  Time Taken: {minutes}m {seconds}s")
    print_separator()

    # Show grade based on percentage
    if percentage >= 90:
        grade = "🏆 EXCELLENT! Outstanding performance!"
    elif percentage >= 75:
        grade = "🥈 GREAT JOB! Well done!"
    elif percentage >= 60:
        grade = "🥉 GOOD! Keep practicing!"
    elif percentage >= 40:
        grade = "📖 FAIR. Review the topics and try again!"
    else:
        grade = "💪 KEEP LEARNING! Practice makes perfect!"

    print(f"\n  {grade}")
    print_separator()

    # Show answer review
    print("\n  📋 ANSWER REVIEW:")
    print()
    for i, log in enumerate(answers_log, 1):
        q_text = log['question'][:45] + "..." if len(log['question']) > 45 else log['question']
        if log['is_correct']:
            status = "✅"
        else:
            status = f"❌ (Correct: {log['correct']})"
        print(f"  {i:2}. {status} {q_text}")

    print()


def display_leaderboard():
    """Shows the top 10 scores."""
    clear_screen()
    print_banner()
    print("\n  🏆 LEADERBOARD - TOP 10 SCORES\n")
    print_separator()

    leaderboard = get_leaderboard()

    if not leaderboard:
        print("  No scores yet! Be the first to play!")
    else:
        print(f"  {'#':<4} {'Name':<15} {'Score':<10} {'%':<8} {'Time':<10} {'Date'}")
        print_separator()
        for i, row in enumerate(leaderboard, 1):
            name, score, total, time_taken, date = row
            pct = (score / total) * 100
            mins = time_taken // 60
            secs = time_taken % 60
            date_short = date[:10]  # Just the date part
            print(f"  {i:<4} {name:<15} {score}/{total:<7} {pct:<7.1f}% {mins}m{secs:02d}s    {date_short}")

    print()



def run_quiz():
    """The main function that runs the entire quiz."""

    clear_screen()
    print_banner()

    # --- GET PLAYER NAME ---
    print("\n  Welcome to the Python Quiz Assessment!")
    print("  You will answer 20 questions.")
    print("  You have 10 MINUTES total.")
    print()
    player_name = input("  Enter your name: ").strip()

    if not player_name:
        player_name = "Anonymous"

    # --- CONFIRM START ---
    print(f"\n  Hello, {player_name}! Ready to start?")
    print("  Press ENTER to begin or Q to go back to menu...")
    choice = input("  ").strip().upper()

    if choice == 'Q':
        return  # Go back to main menu

    # --- LOAD QUESTIONS ---
    questions = get_all_questions()

    if not questions:
        print("  ❌ No questions found in database! Run setup first.")
        time.sleep(2)
        return

    # --- SETUP TIMER: 10 minutes = 600 seconds ---
    QUIZ_TIME = 600  # seconds
    timer = QuizTimer(QUIZ_TIME)
    timer.start()

    # --- QUIZ VARIABLES ---
    score = 0
    answers_log = []  # Track each answer for review
    total = len(questions)

    for i, question_data in enumerate(questions, 1):

        # Check if time is up BEFORE showing each question
        if timer.is_expired():
            clear_screen()
            print_banner()
            print(f"\n  ⏰ TIME'S UP, {player_name}!")
            print(f"  You completed {i-1} of {total} questions.")
            time.sleep(2)
            break

        # Display the question
        display_question(question_data, i, total, timer)

        # Get the user's answer
        user_answer = get_user_answer()

        # Handle quit
        if user_answer == 'Q':
            print("\n  Quiz ended early.")
            time.sleep(1)
            break

        # Check if time expired WHILE answering
        if timer.is_expired():
            print("\n  ⏰ TIME'S UP!")
            time.sleep(1)
            break

        # Unpack question data for checking
        q_id, question, opt_a, opt_b, opt_c, opt_d, correct, category = question_data

        # Check the answer
        is_correct = (user_answer == correct)

        if is_correct:
            score += 1
            print("  ✅ Correct!")
        else:
            # Show what the correct answer text was
            options = {'A': opt_a, 'B': opt_b, 'C': opt_c, 'D': opt_d}
            print(f"  ❌ Wrong! Correct answer: {correct}) {options[correct]}")

        # Log this answer for the review section
        answers_log.append({
            'question': question,
            'your_answer': user_answer,
            'correct': correct,
            'is_correct': is_correct
        })

        time.sleep(1)  # Brief pause so user sees if they were right

    # --- STOP TIMER ---
    timer.stop()
    time_taken = timer.get_elapsed()

    # --- SAVE RESULT TO DATABASE ---
    save_result(player_name, score, total, time_taken)
    print(f"\n  💾 Result saved to database!")
    time.sleep(1)

    # --- SHOW RESULTS ---
    display_result(player_name, score, total, time_taken, answers_log)

    input("  Press ENTER to return to menu...")



def main_menu():
    """Shows the main menu and handles navigation."""
    while True:
        clear_screen()
        print_banner()
        print()
        print("  📋 MAIN MENU")
        print_separator()
        print("  1) Start Quiz")
        print("  2) View Leaderboard")
        print("  3) Exit")
        print_separator()

        choice = input("\n  Enter your choice (1-3): ").strip()

        if choice == '1':
            run_quiz()
        elif choice == '2':
            display_leaderboard()
            input("  Press ENTER to go back...")
        elif choice == '3':
            clear_screen()
            print("\n  👋 Thanks for playing! Keep learning Python!\n")
            break
        else:
            print("  ❌ Invalid choice. Please enter 1, 2, or 3.")
            time.sleep(1)



if __name__ == "__main__":
    # This runs only when you execute: python quiz.py

    print("🔧 Setting up database...")

    # Step 1: Create tables if they don't exist
    setup_database()

    # Step 2: Insert questions if not already there
    insert_questions()

    print("✅ Setup complete! Starting quiz...\n")
    time.sleep(1)

    # Step 3: Launch the main menu
    main_menu()
