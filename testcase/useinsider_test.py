import time
import os
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UseInsiderInterviewTest(unittest.TestCase):

    def setUp(self):
        opts = webdriver.FirefoxOptions()
        opts.add_argument('-headless')

        hub_url = os.getenv("SE_HUB_URL") or 'http://127.0.0.1:4444'

        driver = webdriver.Remote(
            command_executor=f'{hub_url}/wd/hub',
            options=opts
        )

        driver.set_window_size(1600, 1000)

        self.driver = driver

    def tearDown(self):
        self.driver.quit()

    def test_homepage_visible(self):
        '''
        Visit https://useinsider.com/ and check Insider home page is opened or not
        '''

        ## arrange
        url = "https://useinsider.com/"
        expected_title = "#1 Leader in Individualized, Cross-Channel CX — Insider"

        ## act
        self.driver.get(url)

        ## assert
        self.assertEqual(self.driver.title, expected_title, f"Expected: {expected_title}, Got: {self.driver.title}")

    def test_careers_page(self):
        '''
        Select “Company” menu in navigation bar, select “Careers” and check Career page,
        its Locations, Teams and Life at Insider blocks are opened or not
        '''

        ## arrange
        url = 'https://useinsider.com/'
        timeout = 10

        expected_title = 'Ready to disrupt? | Insider Careers'
        company_elem_xpath = '//*[@id="navbarNavDropdown"]/ul[1]/li[6]'
        careers_elem_xpath = '//*[@id="navbarNavDropdown"]/ul[1]/li[6]/div/div[2]/a[2]'
        locations_slider_id = 'location-slider'
        sales_team_image_xpath = '//*[@id="career-find-our-calling"]/div/div/div[2]/div[2]/div[1]/a/img'
        see_all_teams_btn_xpath = '//*[@id="career-find-our-calling"]/div/div/a'
        life_at_insider_title_xpath = '/html/body/div[1]/section[4]/div/div/div/div[1]/div/h2'
        life_at_insider_text = 'Life at Insider'

        ## act
        self.driver.get(url)
        self.driver.find_element(By.XPATH, company_elem_xpath).click()
        self.driver.find_element(By.XPATH, careers_elem_xpath).click()

        locations_elem_present = self._check_element_present(By.ID, locations_slider_id, timeout)
        locations_elem_visible = self._check_element_visible(By.ID, locations_slider_id, timeout)

        sales_team_image_present = self._check_element_present(By.XPATH, sales_team_image_xpath, timeout)
        see_all_teams_btn_present = self._check_element_present(By.XPATH, see_all_teams_btn_xpath, timeout)
        see_all_teams_btn_visible = self._check_element_visible(By.XPATH, see_all_teams_btn_xpath, timeout)

        life_at_insider_title = self.driver.find_element(By.XPATH, life_at_insider_title_xpath)

        ## assert
        self.assertTrue(self.driver.title == expected_title, f"Expected: {expected_title}, Got: {self.driver.title}")

        self.assertTrue(locations_elem_present, "Locations element is not present")
        self.assertTrue(locations_elem_visible, "Locations element is not visible")

        self.assertTrue(sales_team_image_present, "Sales Team image is not present")
        self.assertTrue(see_all_teams_btn_present, "See All Teams button is not present")
        self.assertTrue(see_all_teams_btn_visible, "See All Teams button is not visible")

        self.assertTrue(life_at_insider_title.text == life_at_insider_text, "Life at Insider block is not present")

    def test_qa_jobs_in_careers_page(self):
        '''
        1. Go to https://useinsider.com/careers/quality-assurance/, click “See all QA jobs”,
        filter jobs by Location -  Istanbul, Turkey and department - Quality Assurance, check presence of jobs list
        2. Check that all jobs Position contains “Quality Assurance”, 
        Department contains “Quality Assurance”, Location contains  “Istanbul, Turkey”
        3. Click “View Role” button and check that this action redirects us to Lever Application form page
        '''

        ## arrange
        url = 'https://useinsider.com/careers/quality-assurance/'
        timeout = 30
        see_all_qa_jobs_btn_xpath = '//*[@id="page-head"]/div/div/div[1]/div/div/a'
        filter_by_location_btn_xpath = '//*[@id="top-filter-form"]/div[1]/span/span[1]/span/span[2]'
        location_istanbul_turkiye_xpath = '//li[contains(@class, "select2-results__option") and text()="Istanbul, Turkiye"]'
        jobs_list_div_id = 'jobs-list'
        job_position_class = 'position-title'
        job_location_class = 'position-location'
        job_department_class = 'position-department'
        job_position_expected = 'Quality Assurance'
        job_location_expected = 'Istanbul, Turkiye'
        job_department_expected = 'Quality Assurance'
        job_url_prefix = "https://jobs.lever.co/useinsider"

        ## act
        self.driver.get(url)
        self.driver.find_element(By.XPATH, see_all_qa_jobs_btn_xpath).click()

        filter_by_location = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, filter_by_location_btn_xpath)))

        # wait until elements are loaded
        for i in range(10):
            filter_by_location.click()

            try:
                self.driver.find_element(By.XPATH, location_istanbul_turkiye_xpath)
                filter_by_location.click()
                break
            except Exception as e:
                print(f"waiting until elements are loaded. {i}")

            filter_by_location.click()
            time.sleep(2)

        filter_by_location.click()

        # click on Istanbul, Turkiye
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, location_istanbul_turkiye_xpath))).click()

        # TODO: find a way to let animation finish before accessing elements
        time.sleep(3)

        jobs_list_div = self.driver.find_element(By.ID, jobs_list_div_id)
        jobs = jobs_list_div.find_elements(By.CLASS_NAME, "position-list-item")

        ## assert
        self.assertTrue(len(jobs) > 0, "No jobs found")

        for job in jobs:
            job_position = job.find_element(By.CLASS_NAME, job_position_class).text
            self.assertIn(job_position_expected, job_position, f"Job position does not match. Expected: {job_position_expected}, Got: {job_position}")

            job_department = job.find_element(By.CLASS_NAME, job_department_class).text
            self.assertEqual(job_department, job_department_expected, f"Job department does not match. Expected: {job_department_expected}, Got: {job_department}")

            job_location = job.find_element(By.CLASS_NAME, job_location_class).text
            self.assertEqual(job_location, job_location_expected, f"Job location does not match. Expected: {job_location_expected}, Got: {job_location}")

            # check if URL matches expected format(contains jobs.lever.co)
            view_role_btn = job.find_element(By.TAG_NAME, 'a')
            self.assertIn(job_url_prefix, view_role_btn.get_attribute("href"))

    def _check_element_present(self, by, value, timeout) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
            return True
        except:
            return False

    def _check_element_visible(self, by, value, timeout) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, value)))
            return True
        except:
            return False


def run_testcase(testcase):
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    runner.run(testcase)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(UseInsiderInterviewTest)
    test_count = suite.countTestCases()

    futures = []
    with ThreadPoolExecutor(max_workers=test_count) as executor:
        for testcase in suite:
            future = executor.submit(run_testcase, testcase)
            futures.append(future)
