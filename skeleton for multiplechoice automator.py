import undetected_chromedriver.v2 as uc
import openai
import random
import time
import requests
from selenium.webdriver.common.by import By

# openai api key
openai.api_key = "your_openai_api_key"

# captcha-solving service api key
CAPTCHA_API_KEY = "your_2captcha_api_key"  # replace with your 2captcha API key

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
    if action_type == "click":
        min_time, max_time = 0.5, 1.5  # clicking is typically faster
    elif action_type == "typing":
        min_time, max_time = 1.5, 3  # typing is slower
    elif action_type == "captcha":
        min_time, max_time = 3, 5  # solving captchas takes longer
    else:
        min_time, max_time = 1, 2  # default delay

    delay = random.uniform(min_time, max_time)
    print(f"delaying for {delay:.2f} seconds for {action_type}...")
    time.sleep(delay)

# captcha-solving function
def solve_captcha(captcha_image_url):
    print("sending captcha to 2captcha...")
    response = requests.post(
        "http://2captcha.com/in.php",
        data={
            "key": CAPTCHA_API_KEY,
            "method": "base64",
            "body": captcha_image_url,
            "json": 1
        }
    ).json()

    if response.get("status") != 1:
        print("error submitting captcha:", response)
        return None

    captcha_id = response.get("request")
    print("waiting for captcha to be solved...")

    # check the result
    for _ in range(30):  # retry for up to ~30 seconds
        time.sleep(5)
        result = requests.get(
            f"http://2captcha.com/res.php?key={CAPTCHA_API_KEY}&action=get&id={captcha_id}&json=1"
        ).json()

        if result.get("status") == 1:
            print("captcha solved successfully.")
            return result.get("request")

    print("captcha solving timed out.")
    return None

# set up the browser
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
driver = uc.Chrome(options=options)

# open the login page
driver.get("https://example.com/login")  # replace with the actual url

# check for captcha on the login page
try:
    captcha_element = driver.find_element(By.CLASS_NAME, "captcha-image-class")  # replace with actual class name
    captcha_image_url = captcha_element.get_attribute("src")  # get the captcha image URL

    # solve the captcha
    captcha_solution = solve_captcha(captcha_image_url)
    if captcha_solution:
        captcha_input = driver.find_element(By.CLASS_NAME, "captcha-input-class")  # replace with actual class name
        captcha_input.send_keys(captcha_solution)
        adaptive_delay("captcha")
    else:
        print("could not solve captcha, exiting.")
        driver.quit()
        exit()
except Exception as e:
    print("no captcha found:", e)

# log in to the website
username = driver.find_element(By.ID, "username")  # replace with actual id
password = driver.find_element(By.ID, "password")  # replace with actual id
login_button = driver.find_element(By.ID, "login-button")  # replace with actual id

username.send_keys("your_username")  # replace with your username
adaptive_delay("typing")

password.send_keys("your_password")  # replace with your password
adaptive_delay("typing")

login_button.click()
adaptive_delay("click")

# rest of your question-answering script...

# find questions on the page
question_containers = driver.find_elements(By.CLASS_NAME, "question-container-class")  # replace with actual class

for question_index, question_container in enumerate(question_containers[:20]):  # change number of questions as needed
    # get the question text
    question_text = question_container.find_element(By.CLASS_NAME, "question-text-class").text  # replace with actual class

    # get the answer options
    options = []
    option_elements = question_container.find_elements(By.CLASS_NAME, "option-class")  # replace with actual class
    for option_element in option_elements:
        options.append(option_element.text)

    # answer correctly
    correct_answer = generate_answer(question_text, options)

    for option_element in option_elements:
        if option_element.text.strip() == correct_answer:
            option_element.click()
            adaptive_delay("click")
            break

    # submit the answer
    submit_button = question_container.find_element(By.CLASS_NAME, "submit-button-class")  # replace with actual class
    submit_button.click()
    adaptive_delay("click")

# close the browser
driver.quit()