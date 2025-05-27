import random
import time
import logging
from unittest.mock import MagicMock, patch

# Configure logging to file
logging.basicConfig(
    filename="mock_script_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Mock API keys (not real)
MOCK_OPENAI_API_KEY = "mock_openai_api_key_for_testing"
MOCK_CAPTCHA_API_KEY = "mock_2captcha_api_key_for_testing"

# Settings
TOTAL_QUESTIONS = 5  # Reduced for testing
CORRECT_ANSWERS = 3  # Number of correct answers
INCORRECT_ANSWERS = TOTAL_QUESTIONS - CORRECT_ANSWERS  # Incorrect answers count

# Track progress
answered_correctly = 0
answered_incorrectly = 0

# Mock data for testing
mock_questions = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct_answer": "Paris"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct_answer": "Mars"
    },
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "correct_answer": "4"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        "correct_answer": "William Shakespeare"
    },
    {
        "question": "What is the chemical symbol for water?",
        "options": ["H2O", "CO2", "O2", "N2"],
        "correct_answer": "H2O"
    }
]

# Mock generate answer function (simulates OpenAI API)
def generate_answer(question, options):
    logging.info(f"Generating answer for question: {question}")
    
    # Find the matching question in our mock data
    for q in mock_questions:
        if question in q["question"]:
            logging.info(f"Found matching question, correct answer is: {q['correct_answer']}")
            return q["correct_answer"]
    
    # If no match found, return a random option (fallback)
    logging.warning(f"No matching question found, returning random answer")
    return random.choice(options)

# Adaptive delay based on action type
def adaptive_delay(action_type="default"):
    delay_times = {
        "click": (0.2, 0.5),  # Reduced for testing
        "typing": (0.3, 0.7),  # Reduced for testing
        "captcha": (0.5, 1.0),  # Reduced for testing
        "default": (0.2, 0.5)   # Reduced for testing
    }
    min_time, max_time = delay_times.get(action_type, (0.2, 0.5))
    delay = random.uniform(min_time, max_time)
    
    logging.info(f"Delaying for {delay:.2f} seconds ({action_type})")
    time.sleep(delay)

# Mock captcha-solving function
def solve_captcha(captcha_image_url):
    logging.info("Mock: Sending CAPTCHA to 2Captcha...")
    logging.info(f"Mock: Using API key: {MOCK_CAPTCHA_API_KEY}")
    
    # Simulate API delay
    time.sleep(1)
    
    # Simulate successful CAPTCHA solution
    logging.info("Mock: CAPTCHA solved successfully.")
    return "mock_captcha_solution"

def main():
    logging.info("Starting mock test of selenium-multiple-choice-skeleton")
    logging.info(f"Using mock OpenAI API key: {MOCK_OPENAI_API_KEY}")
    
    # Mock browser setup
    logging.info("Mock: Setting up Chrome browser with undetected-chromedriver")
    logging.info("Mock: Browser launched in headless mode.")
    
    # Mock opening login page
    logging.info("Mock: Opening login page at 'https://example.com/login'")
    
    # Mock CAPTCHA handling
    try:
        logging.info("Mock: Checking for CAPTCHA on login page")
        captcha_solution = solve_captcha("mock_captcha_image_url")
        if captcha_solution:
            logging.info(f"Mock: Entering CAPTCHA solution: {captcha_solution}")
            adaptive_delay("captcha")
    except Exception as e:
        logging.info(f"Mock: No CAPTCHA found or error occurred: {e}")
    
    # Mock login
    logging.info("Mock: Entering username: 'test_user'")
    adaptive_delay("typing")
    logging.info("Mock: Entering password: '********'")
    adaptive_delay("typing")
    logging.info("Mock: Clicking login button")
    adaptive_delay("click")
    logging.info("Mock: Logged in successfully.")
    
    # Mock answering questions
    logging.info(f"Mock: Found {len(mock_questions)} questions to answer")
    
    for question_index, question_data in enumerate(mock_questions[:TOTAL_QUESTIONS]):
        logging.info(f"Answering question {question_index + 1} of {TOTAL_QUESTIONS}.")
        
        question_text = question_data["question"]
        options = question_data["options"]
        
        logging.info(f"Question: {question_text}")
        logging.info(f"Options: {', '.join(options)}")
        
        # Determine if answering correctly or incorrectly
        if answered_correctly < CORRECT_ANSWERS:
            selected_answer = generate_answer(question_text, options)
            answered_correctly += 1
            logging.info(f"Answering CORRECTLY with: {selected_answer}")
        else:
            correct_answer = generate_answer(question_text, options)
            incorrect_options = [opt for opt in options if opt != correct_answer]
            selected_answer = random.choice(incorrect_options)
            answered_incorrectly += 1
            logging.info(f"Answering INCORRECTLY with: {selected_answer} (correct was: {correct_answer})")
        
        logging.info(f"Mock: Clicking on option: {selected_answer}")
        adaptive_delay("click")
        
        logging.info("Mock: Clicking submit button")
        adaptive_delay("click")
        
        logging.info(f"Progress: {answered_correctly} correct, {answered_incorrectly} incorrect.")
    
    # Final report
    logging.info("\nQuiz completed!")
    logging.info(f"Total questions answered: {TOTAL_QUESTIONS}")
    logging.info(f"Correct answers: {answered_correctly}")
    logging.info(f"Incorrect answers: {answered_incorrectly}")
    
    # Close the browser
    logging.info("Mock: Browser closed.")
    
    return {
        "total_questions": TOTAL_QUESTIONS,
        "correct_answers": answered_correctly,
        "incorrect_answers": answered_incorrectly,
        "success": True
    }

if __name__ == "__main__":
    result = main()
    print("\nTest Results:")
    print(f"Total questions: {result['total_questions']}")
    print(f"Correct answers: {result['correct_answers']}")
    print(f"Incorrect answers: {result['incorrect_answers']}")
    print(f"Test successful: {result['success']}")
