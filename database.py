import sqlite3  # sqlite3 comes built-in with Python, no install needed!


def create_connection():
    """Creates a connection to our database file."""
    # This creates 'quiz.db' file in the same folder if it doesn't exist
    conn = sqlite3.connect("quiz.db")
    return conn


def setup_database():
    """Creates all the tables we need."""
    conn = create_connection()
    cursor = conn.cursor()  # cursor lets us run SQL commands

    # TABLE 1: Store the quiz questions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            category TEXT
        )
    """)

    # TABLE 2: Store player results/scores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            time_taken INTEGER NOT NULL,
            date_played TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()  # Save changes
    conn.close()   # Always close the connection!
    print("✅ Database created successfully!")


def insert_questions():
    """Adds 20 Python quiz questions into the database."""
    conn = create_connection()
    cursor = conn.cursor()

    # Check if questions already exist to avoid duplicates
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]

    if count > 0:
        print("✅ Questions already in database, skipping...")
        conn.close()
        return

    # 20 Python Questions: (question, A, B, C, D, correct_answer, category)
    questions = [
        ("What is the output of print(type(10))?",
         "<class 'int'>", "<class 'str'>", "<class 'float'>", "<class 'num'>",
         "A", "Data Types"),

        ("Which keyword is used to define a function in Python?",
         "func", "define", "def", "function",
         "C", "Functions"),

        ("What does len([1, 2, 3]) return?",
         "2", "3", "4", "Error",
         "B", "Lists"),

        ("Which of these is NOT a Python data type?",
         "list", "dictionary", "array", "tuple",
         "C", "Data Types"),

        ("How do you start a comment in Python?",
         "//", "/*", "#", "--",
         "C", "Syntax"),

        ("What is the correct way to create a variable in Python?",
         "int x = 5", "x = 5", "var x = 5", "x := 5",
         "B", "Variables"),

        ("What does the 'append()' method do to a list?",
         "Removes last item", "Adds item to beginning", "Adds item to end", "Sorts the list",
         "C", "Lists"),

        ("Which operator is used for exponentiation in Python?",
         "^", "**", "^^", "exp",
         "B", "Operators"),

        ("What is the output of bool(0)?",
         "True", "False", "0", "None",
         "B", "Boolean"),

        ("How do you create an empty dictionary?",
         "dict = []", "dict = ()", "dict = {}", "dict = <>",
         "C", "Dictionaries"),

        ("Which loop is used when you know the number of iterations?",
         "while loop", "do-while loop", "for loop", "repeat loop",
         "C", "Loops"),

        ("What does 'import' do in Python?",
         "Exports code", "Brings in external code/modules", "Creates a class", "Defines a variable",
         "B", "Modules"),

        ("What is the index of the first item in a Python list?",
         "1", "-1", "0", "None",
         "C", "Lists"),

        ("What keyword is used to exit a loop early?",
         "exit", "stop", "break", "end",
         "C", "Loops"),

        ("What is the output of 10 % 3?",
         "3", "1", "0", "3.33",
         "B", "Operators"),

        ("Which method converts a string to uppercase?",
         ".upper()", ".toUpper()", ".capitalize()", ".UP()",
         "A", "Strings"),

        ("How do you check if a key exists in a dictionary?",
         "key in dict", "dict.has(key)", "dict.contains(key)", "key.exists(dict)",
         "A", "Dictionaries"),

        ("What does 'return' do in a function?",
         "Ends the program", "Sends a value back to the caller", "Prints a value", "Loops back",
         "B", "Functions"),

        ("Which of these is a valid Python list?",
         "(1, 2, 3)", "{1, 2, 3}", "[1, 2, 3]", "<1, 2, 3>",
         "C", "Lists"),

        ("What is the purpose of 'if __name__ == \"__main__\":'?",
         "Imports a module", "Runs code only when file is executed directly", "Defines the main class", "Creates a function",
         "B", "Python Concepts"),
    ]

    # Insert all questions using executemany (efficient batch insert)
    cursor.executemany("""
        INSERT INTO questions (question, option_a, option_b, option_c, option_d, correct_answer, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, questions)

    conn.commit()
    conn.close()
    print(f"✅ {len(questions)} questions added to database!")


def get_all_questions():
    """Fetches all questions from the database."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY RANDOM()")  # Randomize order!
    questions = cursor.fetchall()
    conn.close()
    return questions


def save_result(player_name, score, total, time_taken):
    """Saves a player's quiz result to the database."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO results (player_name, score, total_questions, time_taken)
        VALUES (?, ?, ?, ?)
    """, (player_name, score, total, time_taken))
    conn.commit()
    conn.close()


def get_leaderboard():
    """Gets top 10 scores from the database."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT player_name, score, total_questions, time_taken, date_played
        FROM results
        ORDER BY score DESC, time_taken ASC
        LIMIT 10
    """)
    leaderboard = cursor.fetchall()
    conn.close()
    return leaderboard
