import undetected_chromedriver.v2 as uc
import openai
import random
import time
from selenium.webdriver.common.by import By

# insert your personal openai api key
openai.api_key = "your_openai_api_key"

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

# creates delay to fool bot detectors
def human_delay(min_time=1, max_time=3):
    """Pause execution for a random time between min_time and max_time seconds, replace as needed."""
    delay = random.uniform(min_time, max_time)
    print(f"Delaying for {delay:.2f} seconds to simulate human behavior...")
    time.sleep(delay)

# initialize undetected Chrome driver (should dodge any anti-driver web-browser detection)
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
driver = uc.Chrome(options=options)

# open website login page in the browser
driver.get("https://example.com")  # replace with the actual website URL

# log in to website being used
username = driver.find_element(By.ID, "username")  # Replace 'username' with the actual ID
password = driver.find_element(By.ID, "password")  # Replace 'password' with the actual ID
login_button = driver.find_element(By.ID, "login-button")  # Replace 'login-button' with the actual ID

username.send_keys("your_username")  # replace with username
human_delay()  

password.send_keys("your_password")  # replace with password
human_delay()  

login_button.click()
human_delay()  

# Step 2: Answer questions
max_questions = 20  # Number of questions to answer
question_containers = driver.find_elements(By.CLASS_NAME, "question-container-class")  # replace 'question-container-class'

for question_index, question_container in enumerate(question_containers[:max_questions]):
    # Extract the question text
    question_text = question_container.find_element(By.CLASS_NAME, "question-text-class").text  # replace 'question-text-class'

    # Extract all answer options
    options = []
    option_elements = question_container.find_elements(By.CLASS_NAME, "option-class")  # replace 'option-class'
    for option_element in option_elements:
        options.append(option_element.text)

    # generate the correct answer using openai api key
    correct_answer = generate_answer(question_text, options)

    # find the correct option and click it
    for option_element in option_elements:
        if option_element.text.strip() == correct_answer:
            option_element.click()  # Click the correct answer
            human_delay()  # Pause after clicking the option
            break

    # submit the answer (if required by website being used)
    submit_button = question_container.find_element(By.CLASS_NAME, "submit-button-class")  # replace 'submit-button-class'
    submit_button.click()
    human_delay()  

# close browser
driver.quit()
