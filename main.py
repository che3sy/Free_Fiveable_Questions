from getSlug import refresh_slugs, load_slugs
from getUnitId import get_subject_navigation
from getQuestions import get_practice_questions, save_questions_to_csv

# --- State Management ---
# The output filename now defaults to "questions.csv"
CONFIG = {
    "slug": None,
    "unit_id": None,
    "topic_id": None,
    "limit": None,
    "filename": "questions.csv",
}
CACHE = {
    "slugs": [],
    "navigation": {},
    "unit_name": None,
    "topic_name": None,
}

def print_status():
    """Prints a table of the current parameter configuration."""
    print("\n" + "="*40)
    print(" " * 10 + "CURRENT CONFIGURATION")
    print("="*40)
    print(f"  1. Subject Slug : {CONFIG['slug'] or 'Not Set'}")
    print(f"  2. Unit         : {CACHE['unit_name'] or 'Not Set'}")
    print(f"  3. Topic        : {CACHE['topic_name'] or 'Not Set'}")
    print(f"  4. Question #   : {CONFIG['limit'] or 'Not Set'}")
    print(f"  5. Output File  : {CONFIG['filename'] or 'Not Set'}")
    print("="*40)
    
    # Check if all parameters except filename (which has a default) are set
    ready = all(val is not None for key, val in CONFIG.items())
    if not ready:
        print("--> To fetch questions, please set all parameters.")
        print("--> Type 'explain' for a step-by-step guide or 'help' for commands.")
    else:
        print("--> Configuration complete. Type 'run' to fetch and save questions.")
    print("-" * 40)

def print_help():
    """Prints the help menu."""
    print("\n--- Available Commands ---")
    print("  explain          - Show a detailed guide on how to use the tool.")
    print("  search <query>   - Search for a subject (e.g., 'search calc').")
    print("  units            - List and select a unit for the chosen subject.")
    print("  topics           - List and select a topic for the chosen unit.")
    print("  limit <1-40>     - Set the number of questions to fetch.")
    print("  output <name.csv>- Set a custom filename for the output CSV (default is questions.csv).")
    print("  run              - Fetch questions with the current configuration.")
    print("  refresh          - Manually refresh the local subject list from the server.")
    print("  help             - Show this help message.")
    print("  exit             - Exit the application.")

def print_explain():
    """Prints a detailed explanation of the workflow."""
    print("\n--- How to Use This Tool ---")
    print("The goal is to set the first 4 parameters to fetch practice questions.")
    print("Follow these steps in order:")
    print("\n1. Find your Subject:")
    print("   - Use 'search <keyword>' to find your subject (e.g., 'search biology').")
    print("   - Select the subject from the list. This sets the 'Subject Slug'.")
    print("\n2. Select a Unit:")
    print("   - Use the 'units' command to see all units for your subject.")
    print("   - Select a unit from the list. This sets the 'Unit'.")
    print("\n3. Select a Topic:")
    print("   - Use the 'topics' command to see all topics for your unit.")
    print("   - Select a topic from the list. This sets the 'Topic'.")
    print("\n4. Set Question Count:")
    print("   - Use 'limit <number>' to set how many questions you want (1-40).")
    print("\n(Optional) 5. Set Output File:")
    print("   - The file will save as 'questions.csv' by default.")
    print("   - To change it, use 'output <filename.csv>'.")
    print("\n6. Fetch Questions:")
    print("   - Once parameters 1-4 are set, use the 'run' command.")
    print("   - The questions will be saved to your CSV file.")
    print("\nAt any time, type 'help' for the command list or 'exit' to quit.")

def handle_search(query):
    """Searches for and selects a subject slug."""
    if not query:
        print("--> ERROR: Please provide a search term. Usage: search <query>")
        return
    
    matches = [s for s in CACHE['slugs'] if query in s]
    if not matches:
        print(f"--> No subjects found matching '{query}'.")
        return

    print("--- Found Subjects ---")
    for i, slug in enumerate(matches):
        print(f"  [{i+1}] {slug}")
    
    try:
        choice = int(input("Select a number: ")) - 1
        if 0 <= choice < len(matches):
            selected_slug = matches[choice]
            print(f"--> Selecting '{selected_slug}'...")
            CONFIG['slug'] = selected_slug
            CONFIG.update({"unit_id": None, "topic_id": None})
            CACHE.update({"unit_name": None, "topic_name": None})
            CACHE['navigation'] = get_subject_navigation(selected_slug)
            if not CACHE['navigation']:
                print("--> ERROR: Could not fetch unit data for this subject.")
                CONFIG['slug'] = None
        else:
            print("--> Invalid selection.")
    except (ValueError, IndexError):
        print("--> Invalid input. Please enter a valid number from the list.")

def handle_units():
    """Lists and selects a unit."""
    if not CONFIG['slug']:
        print("--> ERROR: Please select a subject first using the 'search' command.")
        return

    units = CACHE['navigation']
    if not units:
        print("--> No units found for this subject.")
        return

    unit_ids = list(units.keys())
    print("--- Available Units ---")
    for i, unit_id in enumerate(unit_ids):
        print(f"  [{i+1}] {units[unit_id]['name']}")

    try:
        choice = int(input("Select a number: ")) - 1
        if 0 <= choice < len(unit_ids):
            selected_id = unit_ids[choice]
            CONFIG['unit_id'] = selected_id
            CACHE['unit_name'] = units[selected_id]['name']
            CONFIG['topic_id'] = None
            CACHE['topic_name'] = None
            print(f"--> Unit '{CACHE['unit_name']}' selected.")
        else:
            print("--> Invalid selection.")
    except (ValueError, IndexError):
        print("--> Invalid input. Please enter a valid number from the list.")

def handle_topics():
    """Lists and selects a topic."""
    if not CONFIG['unit_id']:
        print("--> ERROR: Please select a unit first using the 'units' command.")
        return

    topics = CACHE['navigation'][CONFIG['unit_id']]['topics']
    if not topics:
        print("--> No topics found for this unit.")
        return

    print("--- Available Topics ---")
    for i, topic in enumerate(topics):
        print(f"  [{i+1}] {topic['name']}")

    try:
        choice = int(input("Select a number: ")) - 1
        if 0 <= choice < len(topics):
            selected_topic = topics[choice]
            CONFIG['topic_id'] = selected_topic['id']
            CACHE['topic_name'] = selected_topic['name']
            print(f"--> Topic '{CACHE['topic_name']}' selected.")
        else:
            print("--> Invalid selection.")
    except (ValueError, IndexError):
        print("--> Invalid input. Please enter a valid number from the list.")

def handle_limit(num_str):
    """Sets the question limit."""
    try:
        limit = int(num_str)
        if 1 <= limit <= 40:
            CONFIG['limit'] = limit
            print(f"--> Question limit set to {limit}.")
        else:
            print("--> ERROR: Limit must be a number between 1 and 40.")
    except ValueError:
        print("--> ERROR: Invalid number. Usage: limit <number>")

def handle_output(filename):
    """Sets the output filename."""
    if filename and filename.endswith(".csv"):
        CONFIG['filename'] = filename
        print(f"--> Output file set to '{filename}'.")
    else:
        print("--> ERROR: Filename must be provided and end with .csv")

def handle_run():
    """Runs the main process to fetch and save questions."""
    if not all(CONFIG.values()):
        print("--> ERROR: Configuration is incomplete. Please set all parameters before running.")
        return

    print("\nFetching questions from the server...")
    questions = get_practice_questions(
        subject_slug=CONFIG['slug'],
        unit_id=CONFIG['unit_id'],
        topic_id=CONFIG['topic_id'],
        limit=CONFIG['limit']
    )

    if questions:
        save_questions_to_csv(questions, CONFIG['filename'])
    else:
        print("--> No questions were returned from the server for the selected topic.")

def main():
    """Main application loop."""
    print("--- Fiveable Question Fetcher ---")
    # Refresh slugs from the server on every startup
    refresh_slugs()
    CACHE['slugs'] = load_slugs()
    print("--> Subject list is up-to-date.")

    while True:
        print_status()
        try:
            user_input = input("> ").strip()
            if not user_input: continue

            parts = user_input.split(' ', 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "help": print_help()
            elif command == "explain": print_explain()
            elif command == "search": handle_search(args)
            elif command == "units": handle_units()
            elif command == "topics": handle_topics()
            elif command == "limit": handle_limit(args)
            elif command == "output": handle_output(args)
            elif command == "run": handle_run()
            elif command == "refresh":
                print("--> Refreshing slug list from server...")
                refresh_slugs()
                CACHE['slugs'] = load_slugs()
                print("--> Slug list updated.")
            elif command == "exit":
                print("Exiting.")
                break
            else:
                print(f"--> Unknown command: '{command}'. Type 'help' for options.")

        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()