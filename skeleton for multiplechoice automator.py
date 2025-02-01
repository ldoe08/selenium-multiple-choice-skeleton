import undetected_chromedriver.v2 as uc
import openai
import random
import time
import requests
import logging
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# configure logging to file
logging.basicConfig(
    filename="script_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# openai api key
openai.api_key = "your_openai_api_key"

# settings
total_questions = 20  # number of questions to answer
correct_answers = 15  # number of correct answers
incorrect_answers = total_questions - correct_answers  # incorrect answers count

# track progress
answered_correctly = 0
answered_incorrectly = 0

def generate_answer(question, options):
    prompt = f"""
    Question: {question}
    Options: {', '.join(options)}
    Pick the best option from the list of answers and only return the option text.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    return response["choices"][0]["text"].strip()

def adaptive_delay(action_type="default"):
    delay_times = {
        "click": (0.5, 1.5),
        "typing": (1.5, 3),
        "captcha": (3, 5),
        "default": (1, 2)
    }
    min_time, max_time = delay_times.get(action_type, (1, 2))
    delay = random.uniform(min_time, max_time)
    logging.info(f"Delaying for {delay:.2f} seconds ({action_type})")
    time.sleep(delay)

def setup_browser():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)
    logging.info("Browser launched in headless mode.")
    return driver

def navigate_and_answer(driver):
    global answered_correctly, answered_incorrectly
    driver.get("https://example.com/login")
    logging.info("Opened login page.")

    # login
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.ID, "login-button")
    username.send_keys("your_username")
    adaptive_delay("typing")
    password.send_keys("your_password")
    adaptive_delay("typing")
    login_button.click()
    adaptive_delay("click")
    logging.info("Logged in successfully.")

    for _ in range(total_questions):
        try:
            question_text = driver.find_element(By.CLASS_NAME, "question-text-class").text
            option_elements = driver.find_elements(By.CLASS_NAME, "option-class")
            options = [option.text for option in option_elements]

            if answered_correctly < correct_answers:
                selected_answer = generate_answer(question_text, options)
                answered_correctly += 1
            else:
                incorrect_options = [opt for opt in options if opt != generate_answer(question_text, options)]
                selected_answer = random.choice(incorrect_options)
                answered_incorrectly += 1

            for option_element in option_elements:
                if option_element.text.strip() == selected_answer:
                    option_element.click()
                    adaptive_delay("click")
                    break

            submit_button = driver.find_element(By.CLASS_NAME, "submit-button-class")
            submit_button.click()
            adaptive_delay("click")

            # verify answer submission
            result_text = driver.find_element(By.CLASS_NAME, "result-class").text
            if "correct" in result_text.lower():
                logging.info(f"Question answered correctly: {question_text}")
            else:
                logging.info(f"Question answered incorrectly: {question_text}")

            # handle multi-page navigation
            try:
                next_button = driver.find_element(By.CLASS_NAME, "next-page-class")
                next_button.click()
                adaptive_delay("click")
                logging.info("Navigated to next page.")
            except:
                logging.info("No next page button found.")
        except Exception as e:
            logging.error(f"Error answering question: {e}")

    logging.info(f"Quiz completed! Correct: {answered_correctly}, Incorrect: {answered_incorrectly}")
    driver.quit()

# parallel execution using threading
def start_parallel_sessions(session_count=2):
    threads = []
    for _ in range(session_count):
        driver = setup_browser()
        thread = threading.Thread(target=navigate_and_answer, args=(driver,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    start_parallel_sessions(session_count=2)
