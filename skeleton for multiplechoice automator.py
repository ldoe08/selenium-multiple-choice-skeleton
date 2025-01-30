import undetected_chromedriver.v2 as uc
import openai
import random
import time
import requests
import logging
from selenium.webdriver.common.by import By

# configure logging to file
logging.basicConfig(
    filename="script_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# openai api key
openai.api_key = "your_openai_api_key"

# captcha-solving service api key
CAPTCHA_API_KEY = "your_2captcha_api_key"  # replace with your 2captcha API key

# settings
TOTAL_QUESTIONS = 20  # number of questions to answer
CORRECT_ANSWERS = 15  # number of correct answers
INCORRECT_ANSWERS = TOTAL_QUESTIONS - CORRECT_ANSWERS  # incorrect answers count

# track progress
answered_correctly = 0
answered_incorrectly = 0

# generate the correct answer using openai
def generate_answer(question, options):
    prompt = f"""
    question: {question}
    options: {', '.join(options)}
    pick the best option from the list of answers and only return the option text.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    return response["choices"][0]["text"].strip()

# adaptive delay based on action type
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

# captcha-solving function
def solve_captcha(captcha_image_url):
    logging.info("Sending CAPTCHA to 2Captcha...")
    response = requests.post(
        "http://2captcha.com/in.php",
        data={"key": CAPTCHA_API_KEY, "method": "base64", "body": captcha_image_url, "json": 1}
    ).json()

    if response.get("status") != 1:
        logging.error(f"Error submitting CAPTCHA: {response}")
        return None

    captcha_id = response.get("request")
    logging.info("Waiting for CAPTCHA solution...")

    for _ in range(30):
        time.sleep(5)
        result = requests.get(f"http://2captcha.com/res.php?key={CAPTCHA_API_KEY}&action=get&id={captcha_id}&json=1").json()

        if result.get("status") == 1:
            logging.info("CAPTCHA solved successfully.")
            return result.get("request")

    logging.error("CAPTCHA solving timed out.")
    return None

# set up the browser (headless mode enabled)
options = uc.ChromeOptions()
options.add_argument("--headless")  # run in headless mode (no UI)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")  # improves performance
options.add_argument("--no-sandbox")  # helps prevent crashes
options.add_argument("--disable-dev-shm-usage")  # prevents issues in containers
options.add_argument("start-maximized")

driver = uc.Chrome(options=options)

logging.info("Browser launched in headless mode.")

# open the login page
driver.get("https://example.com/login")  # replace with actual URL
logging.info("Opened login page.")

# check for captcha on the login page
try:
    captcha_element = driver.find_element(By.CLASS_NAME, "captcha-image-class")  # replace with actual class name
    captcha_image_url = captcha_element.get_attribute("src")

    captcha_solution = solve_captcha(captcha_image_url)
    if captcha_solution:
        captcha_input = driver.find_element(By.CLASS_NAME, "captcha-input-class")  # replace with actual class name
        captcha_input.send_keys(captcha_solution)
        adaptive_delay("captcha")
    else:
        logging.error("Could not solve CAPTCHA, exiting.")
        driver.quit()
        exit()
except Exception as e:
    logging.info(f"No CAPTCHA found: {e}")

# log in
username = driver.find_element(By.ID, "username")  # replace with actual id
password = driver.find_element(By.ID, "password")  # replace with actual id
login_button = driver.find_element(By.ID, "login-button")  # replace with actual id

username.send_keys("your_username")
adaptive_delay("typing")
password.send_keys("your_password")
adaptive_delay("typing")
login_button.click()
adaptive_delay("click")

logging.info("Logged in successfully.")

# start answering questions
question_containers = driver.find_elements(By.CLASS_NAME, "question-container-class")  # replace with actual class

for question_index, question_container in enumerate(question_containers[:TOTAL_QUESTIONS]):
    logging.info(f"Answering question {question_index + 1} of {TOTAL_QUESTIONS}.")

    question_text = question_container.find_element(By.CLASS_NAME, "question-text-class").text  # replace with actual class

    options = []
    option_elements = question_container.find_elements(By.CLASS_NAME, "option-class")  # replace with actual class
    for option_element in option_elements:
        options.append(option_element.text)

    # determine if answering correctly or incorrectly
    if answered_correctly < CORRECT_ANSWERS:
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

    submit_button = question_container.find_element(By.CLASS_NAME, "submit-button-class")  # replace with actual class
    submit_button.click()
    adaptive_delay("click")

    logging.info(f"Progress: {answered_correctly} correct, {answered_incorrectly} incorrect.")

# final report
logging.info("\nQuiz completed!")
logging.info(f"Total questions answered: {TOTAL_QUESTIONS}")
logging.info(f"Correct answers: {answered_correctly}")
logging.info(f"Incorrect answers: {answered_incorrectly}")

# close the browser
driver.quit()
logging.info("Browser closed.")