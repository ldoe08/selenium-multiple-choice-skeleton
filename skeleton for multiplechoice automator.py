import undetected_chromedriver.v2 as uc
import openai
import google.generativeai as genai
import random
import time
import requests
import logging
import threading
import tkinter as tk
from tkinter import ttk
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# configure logging to file
logging.basicConfig(
    filename="script_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# api keys
openai.api_key = "your_openai_api_key"
genai.configure(api_key="your_gemini_api_key")

# settings
total_questions = 20
correct_answers = 15
incorrect_answers = total_questions - correct_answers
use_openai = True

# track progress
answered_correctly = 0
answered_incorrectly = 0
question_memory = set()

# tkinter feedback variables
progress_var = None
feedback_label = None


def generate_answer_openai(question, options, confidence=0.8):
    prompt = f"""
    Question: {question}
    Options: {', '.join(options)}
    Pick the best option from the list of answers and only return the option text.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful AI answering multiple-choice questions. It will be multiple choice, and as such you should only choose one of the options. Any answers such as I don't know should be ignored. "},
                  {"role": "user", "content": prompt}]
    )
    correct_answer = response["choices"][0]["message"]["content"].strip()

    if random.random() > confidence:
        incorrect_options = [opt for opt in options if opt != correct_answer]
        return random.choice(incorrect_options) if incorrect_options else correct_answer
    return correct_answer


def generate_answer_gemini(question, options, confidence=0.8):
    prompt = f"""
    Question: {question}
    Options: {', '.join(options)}
    Pick the best option from the list of answers and only return the option text.
    """
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt)
    correct_answer = response.text.strip()

    if random.random() > confidence:
        incorrect_options = [opt for opt in options if opt != correct_answer]
        return random.choice(incorrect_options) if incorrect_options else correct_answer
    return correct_answer


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


def update_dashboard():
    progress = f"Correct: {answered_correctly} | Incorrect: {answered_incorrectly}"
    if progress_var:
        progress_var.set(progress)


def safe_find(driver, by, value, retries=3, delay=2):
    for _ in range(retries):
        try:
            return driver.find_element(by, value)
        except NoSuchElementException:
            time.sleep(delay)
    return None


def safe_find_all(driver, by, value, retries=3, delay=2):
    for _ in range(retries):
        try:
            elements = driver.find_elements(by, value)
            if elements:
                return elements
        except WebDriverException:
            time.sleep(delay)
    return []


def navigate_and_answer(driver):
    global answered_correctly, answered_incorrectly
    driver.get("https://example.com/login")
    logging.info("Opened login page.")

    for _ in range(total_questions):
        try:
            question_element = safe_find(driver, By.CLASS_NAME, "question-text-class")
            if not question_element:
                logging.warning("Question element not found. Skipping.")
                continue

            question_text = question_element.text
            if question_text in question_memory:
                logging.info("Duplicate question detected. Skipping.")
                continue

            option_elements = safe_find_all(driver, By.CLASS_NAME, "option-class")
            options = [option.text for option in option_elements]

            selected_answer = generate_answer_openai(question_text, options) if use_openai else generate_answer_gemini(question_text, options)

            # mark question as seen
            question_memory.add(question_text)

            # display feedback in gui
            if feedback_label:
                feedback_label.config(text=f"AI selected: {selected_answer}")

            for option_element in option_elements:
                if option_element.text.strip() == selected_answer:
                    option_element.click()
                    adaptive_delay("click")
                    break

            submit_button = safe_find(driver, By.CLASS_NAME, "submit-button-class")
            if submit_button:
                submit_button.click()
                adaptive_delay("click")

            # update counters
            if selected_answer in question_text:  # dummy check, replace with actual verification if needed
                answered_correctly += 1
            else:
                answered_incorrectly += 1

            update_dashboard()
            logging.info(f"Answered: {question_text}")

        except Exception as e:
            logging.error(f"Error answering question: {e}")
    driver.quit()


def start_script():
    global total_questions, correct_answers, incorrect_answers, use_openai, answered_correctly, answered_incorrectly
    total_questions = int(entry_questions.get())
    correct_answers = int(entry_correct.get())
    incorrect_answers = total_questions - correct_answers
    use_openai = api_var.get() == "OpenAI"
    answered_correctly = 0
    answered_incorrectly = 0
    threading.Thread(target=navigate_and_answer, args=(setup_browser(),)).start()

# tkinter gui
root = tk.Tk()
root.title("Quiz Bot Configurator")

tk.Label(root, text="Total Questions:").grid(row=0, column=0)
entry_questions = tk.Entry(root)
entry_questions.grid(row=0, column=1)
entry_questions.insert(0, "20")

tk.Label(root, text="Correct Answers:").grid(row=1, column=0)
entry_correct = tk.Entry(root)
entry_correct.grid(row=1, column=1)
entry_correct.insert(0, "15")

api_var = tk.StringVar(value="OpenAI")
openai_radio = ttk.Radiobutton(root, text="OpenAI", variable=api_var, value="OpenAI")
gemini_radio = ttk.Radiobutton(root, text="Gemini", variable=api_var, value="Gemini")
openai_radio.grid(row=2, column=0)
gemini_radio.grid(row=2, column=1)

tk.Button(root, text="Start", command=start_script).grid(row=3, columnspan=2)

progress_var = tk.StringVar()
feedback_label = tk.Label(root, textvariable=progress_var)
feedback_label.grid(row=4, columnspan=2)

feedback_label = tk.Label(root, text="AI answer will appear here")
feedback_label.grid(row=5, columnspan=2)

root.mainloop()
