import requests
import json
import csv

def get_practice_questions(subject_slug: str, unit_id: str, topic_id: str, limit: int = 1, question_type: str = None) -> list:
    """
    Fetches practice questions from the Fiveable API.

    Args:
        subject_slug: The slug for the subject (e.g., "ap-calc").
        unit_id: The ID of the unit.
        topic_id: The ID of the topic.
        limit: The number of questions to fetch (1-40).
        question_type: Optional. Can be "CLAUDE_3_7", "SINGLE_ANSWER", etc.

    Returns:
        A list of dictionaries, each containing a question, answers, the correct answer, and an explanation.
    """
    base_url = "https://library.fiveable.me/api/practice-questions"
    params = {
        "subjectId": subject_slug,
        "unitId": unit_id,
        "topicId": topic_id,
        "limit": limit
    }
    if question_type:
        params["type"] = question_type
    
    processed_questions = []
    try:
        response = requests.get(base_url, params=params,  timeout=15)
        response.raise_for_status()
        data = response.json()

        questions_list = data.get("data", {}).get("practiceQuestionsByTopic", [])
        
        for q_data in questions_list:
            correct_answer = ""
            all_answers = []
            for ans in q_data.get("answers", []):
                all_answers.append(ans.get("answer"))
                if ans.get("type") == "CORRECT":
                    correct_answer = ans.get("answer")
            
            processed_questions.append({
                "question": q_data.get("question"),
                "answers": all_answers,
                "correct_answer": correct_answer,
                "explanation": q_data.get("explanation")
            })

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching questions: {e}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response for questions.")
        
    return processed_questions

def save_questions_to_csv(questions: list, filename: str):
    """Saves a list of questions to a CSV file with A, B, C, D columns."""
    if not questions:
        print("--> No questions to save.")
        return

    fieldnames = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation']

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for q in questions:
                answers = q.get('answers', [])
                row = {
                    'question': q.get('question'),
                    'option_a': answers[0] if len(answers) > 0 else "",
                    'option_b': answers[1] if len(answers) > 1 else "",
                    'option_c': answers[2] if len(answers) > 2 else "",
                    'option_d': answers[3] if len(answers) > 3 else "",
                    'correct_answer': q.get('correct_answer'),
                    'explanation': q.get('explanation')
                }
                writer.writerow(row)
        print(f"--> Successfully saved {len(questions)} questions to '{filename}'")
    except IOError as e:
        print(f"--> ERROR writing to file '{filename}': {e}")