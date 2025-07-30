from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from time import sleep

DEBUG = True
def log(msg):
    if DEBUG:
        print(msg)

def create_driver():
    options = Options()
    #options.add_argument("--headless=new")  headless mode: Turn off the browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("--log-level=3")  # Block the system logs
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  
    options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36" 
    )
    #options.add_experimental_option("detach", True)  
    service = Service(log_path="NUL")  
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver

def scrape_project(link, num):
    driver = create_driver()
    wait = WebDriverWait(driver, 10)
    project = {
        "Development name": None,
        "Address": None,
        "Developer": None,
        "Builder": None,
        "Partner": [],
        "Project commencement": None,
        "Link": link,
    }
    try:
        driver.get(link)
        wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'text-[32px]')]")))
        log(f"Start scraping project {num}")
        # ---------------------- Development name -----------------------------------
        try:
            dev_name = driver.find_element(By.XPATH, "//h1[contains(@class, 'text-[32px] md:text-4xl mb-2')]").text
            project["Development name"] = dev_name
            log(f"-> Scraped Project Name: {dev_name}")
        except:
            log(f"[{num}] Cannot get Development name")
        
        # ---------------------------------- Address -----------------------------------
        try:
            address = driver.find_element(By.XPATH, ".//div[@class='text-sm font-light']").text
            project["Address"] = address
            log(f"-> Scraped Address")
        except:
            log(f"[{num}] Cannot get the address or do not have address")
        
        # ----------------------------------- Developer ----------------------------------
        try:
            developer = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='text-base font-normal']"))
            ).text
            project["Developer"] = developer
            log(f"-> Scraped Developer")
        except:
            project["Developer"] = "None"
            log(f"[{num}] Cannot get the Developer or do not have Developer")
        
        # ------------------------------- Builder / Partner -----------------------------------
        try:
            elems = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[@class='font-light p-2 flex']")
                )
            )
            if len(elems) == 0:
                project["Builder"] = "None"
                project["Partner"] = "None"
            else:
                has_builder = False
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elems[0])
                sleep(3)
                wait.until(EC.element_to_be_clickable(elems[0]))
                for i in range(len(elems)):
                    elems[i].click()
                    sleep(2)

                    if elems[i].text == "Builder":
                        has_builder = True
                        builder = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//a[contains(@class, 'text-base')]")
                            )
                        ).text
                        project["Builder"] = builder if builder else "None"
                        log(f"-> Scraped Builder")
                    else:
                        partner = wait.until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//a[contains(@class, 'text-base')]")
                            )
                        ).text
                        if len(partner) != 0:
                            project["Partner"].append(partner)
                            log(f"-> Scraped Partner")
                        else:
                            project["Partner"] = "None"
                if not has_builder:
                    project["Builder"] = "None"
        except Exception as e:
            log(f"[{num}] Cannot get the Builder/Partner or do not have Builder/Partner")
            project["Builder"] = "None"
            project["Partner"] = "None"

        

        # -------------------------------------- Project commencement ------------------------------
        try:
            project_status = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'mb-4')][.//div[text()[contains(., 'Project Status')]]]/div/div[2]")
                )
            ).text
            project["Project commencement"] = project_status
            log(f"-> Scraped Project Status")
        except:
            log(f"[{num}] Cannot get Project commencement")
        
        log(f"[{num}] => Scraped successfully: {project['Development name']}")
    except Exception as e:
        log(f"[{num}] Cannot scrape project: {e}")
    finally:
        driver.quit()
    return project

def scrape_all_projects(base_url: str, sheet_name = str):
    # Main driver
    main_driver = create_driver()
    main_wait = WebDriverWait(main_driver, 10)
    main_driver.get(base_url)

    try:
        main_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        show_more = main_wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/page/')]"))
        )
    
        # Click show more
        while True:
            try:
                show_more = main_wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/page/')]"))
                )
                main_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(3)
                main_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                show_more.click()
                sleep(3)
            except:
                break
            
    except Exception as e:
        log(f"Couldn't find show more button")

    project_boxes = main_wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class, 'block h-full border border-gray-3 cursor-pointer')]")
        )
    )
    hrefs = []
    for box in project_boxes:
        try:
            a_tag = box.find_element(By.XPATH, ".//span[1]/a")
            href = a_tag.get_attribute("href")
            if href:
                hrefs.append(href)
        except:
            continue

    main_driver.quit()

    log(f"Projects need scraping: {len(hrefs)}")

    # multi-thread to increase speed
    projects = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(scrape_project, hrefs, range(1, len(hrefs)+1))
        for proj in results:
            if proj and proj["Development name"]:
                projects[proj["Development name"]] = proj

    # Save to excel
    df = pd.DataFrame.from_dict(projects, orient="index")
    df["Partner"] = df["Partner"].apply(lambda x: ", ".join(x) if isinstance(x, list) and x else "None")
    # Append sheet to Excel 
    with pd.ExcelWriter("apartments.com.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    log(f"Saved sheet {sheet_name} to apartments.com.xlsx")

if __name__ == "__main__":
   scrape_all_projects()
