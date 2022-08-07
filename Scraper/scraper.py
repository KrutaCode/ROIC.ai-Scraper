# For operating system interactions
import os

# For number storage and manipulation
import pandas as pd

# For time operations
import time

# Database access
import Database_Writer.database

# For web interactions
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from Scraper.scraper_utils import ScraperUtilities

# URL for website. Final URL will look like: https://roic.ai/financials/AAPL
url = "https://roic.ai/company/"


''' -- Chromedriver creation -- '''
# Step back one folder
os.chdir("..")
# Gets the current directory where the chromedriver is stored
cwd = os.getcwd()
chrome_driver = cwd + "\\ROIC\\chromedriver.exe"


''' -- Chromedriver options -- '''
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--headless')

class ROIC_Scraper(ScraperUtilities):
    def __init__(self, ticker: str):
        # Store ticker
        self.ticker = ticker.upper()



        # Track the number of years on each page. This is so we do not have to fetch the years every field.
        self.summary_page_col_labels = []
        self.financial_page_col_labels = []

        # Track the page data
        self.summary_page_data = []
        self.income_statement_data = []
        self.balance_sheet_data = []
        self.cash_flow_data = []

        # Track the row labels on each page.
        self.summary_page_row_labels = []
        self.income_statement_row_labels = []
        self.balance_sheet_row_labels = []
        self.cash_flow_row_labels = []

        # Create database object
        self.db = Database_Writer.database.AssetDatabase(self.ticker)

        # Tracks if a database table exists
        self.exists_summary = self.db.check_if_table_exists("summary")
        self.exists_income_statement = self.db.check_if_table_exists("income_statement")
        self.exists_balance_sheet = self.db.check_if_table_exists("balance_sheet")
        self.exists_cash_flow = self.db.check_if_table_exists("cash_flow")

        # If any of the tables do not exist then we need to create a browser object. If all the tables exist
        # then we do not need a browser object. We can just use the data in the database.
        if not self.exists_summary or not self.exists_income_statement or not self.exists_balance_sheet or not self.exists_cash_flow:
            # Create browser object
            self.browser = webdriver.Chrome(chrome_driver, options=options)
        else:
            self.browser = None

        # Keeps track of URLs within ROIC.ai
        self.summary_page_url = "https://roic.ai/company/" + self.ticker
        self.financial_page_url = "https://roic.ai/financials" + self.ticker

        super().__init__(self.browser)

    ################################################################################################################
    ################################################################################################################
    #                                                   Column Labels
    '-------------------------------------------------------'
    def set_summary_page_col_labels(self):
        # If the list is empty. If there is already data, we do not want to append to it.
        if not self.summary_page_col_labels:
            # Loop control
            running = True
            i = 1
            while running:
                try:
                    xpath = f"/html/body/div/div/main/div[3]/div/div[1]/div/div[2]/div[2]/div[{i}]"
                    col_label = self.read_data(xpath)
                    self.summary_page_col_labels.append(col_label)
                    i += 1
                except NoSuchElementException:
                    running = False
            if "- -" in self.summary_page_col_labels:
                bad_col_count = 0
                real_num = 0
                for i in self.summary_page_col_labels:
                    print(f"I: {i}")
                    if i == "- -":
                        bad_col_count += 1
                    else:
                        real_num = i
                        break
                final_num = int(real_num) - bad_col_count
                for j in range(len(self.summary_page_col_labels)):
                    if j == 0:
                        self.summary_page_col_labels[j] = final_num
                    else:
                        final_num += 1
                        self.summary_page_col_labels[j] = final_num

                print(f"ReaL: {real_num}")


    '-------------------------------------------------------'
    def set_financial_page_col_labels(self):
        # If the list is empty. If there is already data, we do not want to append to it.
        if not self.financial_page_col_labels:
            # Loop control
            running = True
            i = 1
            while running:
                try:
                    xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[3]/div/div[2]/div[{i}]"
                    col_label = self.read_data(xpath)
                    self.financial_page_col_labels.append(col_label)
                    i += 1
                except NoSuchElementException:
                    running = False
            if "- -" in self.financial_page_col_labels:
                bad_col_count = 0
                real_num = 0
                for i in self.financial_page_col_labels:
                    print(f"I: {i}")
                    if i == "- -":
                        bad_col_count += 1
                    else:
                        real_num = i
                        break
                final_num = int(real_num) - bad_col_count
                for j in range(len(self.financial_page_col_labels)):
                    if j == 0:
                        self.financial_page_col_labels[j] = final_num
                    else:
                        final_num += 1
                        self.financial_page_col_labels[j] = final_num

    '-------------------------------------------------------'
    def get_summary_page_col_labels(self) -> list:
        if not self.summary_page_col_labels:
            self.set_summary_page_col_labels()
        return self.summary_page_col_labels
    '-------------------------------------------------------'
    def get_financial_page_col_labels(self) -> list:
        if not self.financial_page_col_labels:
            self.set_financial_page_col_labels()
        return self.financial_page_col_labels
    '-------------------------------------------------------'
    ################################################################################################################
    ################################################################################################################
    #                                                   Page Scrapers
    '-------------------------------------------------------'
    def set_summary_page_data(self):
        '''
        - Gets all of the data from the summary page and stores it in a list.
        :param create_df: If True, the data collected will automatically be turned into a dataframe.
                          If False, then the normal 2-d list will be returned.
        :return: list or pd.Dataframe
        '''
        table = "summary"
        if not self.exists_summary:
            # Check if we are at the page within the website that we should be at.
            if self.browser.current_url != self.summary_page_url:
                self.goto_page_name("summary_page",self.ticker)

            # Keeps track of the index for the row.
            row_index = 3
            element_index = 3
            # List to hold data
            data_storage = []
            print("--------------------------------------------------------\n\n")
            for x in range(25):
                try:
                    i = 1
                    data = []
                    running = True
                    # Get the row label
                    row_xpath = f"/html/body/div/div/main/div[3]/div/div[1]/div/div[{row_index}]/div[1]/span"
                    row = self.read_data(row_xpath)
                    print(f"[Collected] -    {row}")

                    while running:
                        try:
                            # Get the data from the xpath
                            xpath = f"/html/body/div/div/main/div[3]/div/div[1]/div/div[{element_index}]/div[2]/div[{i}]"
                            d = self.read_data(xpath)
                            data.append(d)
                            i += 1
                        except NoSuchElementException:
                            running = False
                    self.summary_page_row_labels.append(row)
                    row_index += 1
                    element_index += 1
                    data_storage.append(data)
                except NoSuchElementException:
                    break

            self.summary_page_data = data_storage
        else:
            print(f"\n[Table Found]  - '{table}' was detected '{self.db.db_filename}'. Fetching data from database.\n")
            self.summary_page_data = self.db.get_data_from_table("summary")

    '-------------------------------------------------------'
    def get_summary_page_data(self) -> list:
        '''
        - Gets the data collected from the summary page.
        :return: list
        '''
        return self.summary_page_data

    '-------------------------------------------------------'
    def set_income_statement_data(self):
        '''
        - Gets all of the data from the income statement and stores it in a list.
        :param create_df: If True, the data collected will automatically be turned into a dataframe.
                          If False, then the normal 2-d list will be returned.
        :return: list or pd.Dataframe
        '''
        table = "income_statement"

        if not self.exists_income_statement:
            # Check if we are at the page within the website that we should be at.
            if self.browser.current_url != self.financial_page_url:
                self.goto_page_name("financial_page",self.ticker)

            main_run = True
            # Keeps track of the index for the row.
            row_index = 2
            element_index = 2
            # List to hold data
            data_storage = []
            print("--------------------------------------------------------\n\n")
            while main_run:
                i = 1
                data = []
                running = True
                # Get the row label
                row_xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{row_index}]/div[1]/span"
                row = self.read_data(row_xpath)
                if row == "SEC Link":
                    main_run = False
                    break
                else:
                    print(f"[Collected] -    {row}")
                    while running:
                        try:
                            # Get the data from the xpath
                            xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{element_index}]/div[3]/div[{i}]"
                            d = self.read_data(xpath)
                            data.append(d)
                            i += 1
                        except NoSuchElementException:
                            running = False
                    self.income_statement_row_labels.append(row)
                    row_index += 1
                    element_index += 1
                    data_storage.append(data)
            self.income_statement_data = data_storage
        else:
            print(f"\n[Table Found]  - '{table}' was detected '{self.db.db_filename}'. Fetching data from database.\n")
            self.income_statement_data = self.db.get_data_from_table("income_statement")

    '-------------------------------------------------------'
    def get_income_statement_data(self) -> list:
        '''
        - Returns the data collected from the income statement.
        :return: list
        '''
        return self.income_statement_data
    '-------------------------------------------------------'
    def set_balance_sheet_data(self):
        '''
        - Gets all of the data from the balance sheet and stores it in a list.
        :param create_df: If True, the data collected will automatically be turned i8nto a dataframe
                          If False, then the normal 2-d list will be returned.
        :return: list or pd.Dataframe
        '''
        table = "balance_sheet"
        if not self.exists_balance_sheet:
            # Check if we are at the page within the website that we should be at.
            if self.browser.current_url != self.financial_page_url:
                self.goto_page_name("financial_page",self.ticker)

            main_run = True
            # Keeps track of the index for the row.
            row_index = 32
            element_index = 32
            # List to hold data
            data_storage = []
            print("--------------------------------------------------------\n\n")
            while main_run:
                i = 1
                data = []
                running = True
                # Get the row label
                row_xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{row_index}]/div[1]/span"
                row = self.read_data(row_xpath)
                if row == "SEC Link":
                    main_run = False
                else:
                    print(f"[Collected] -    {row}")
                    while running:
                        try:
                            # Get the data from the xpath
                            xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{element_index}]/div[3]/div[{i}]"
                            d = self.read_data(xpath)
                            data.append(d)
                            i += 1
                        except NoSuchElementException:
                            running = False
                    self.balance_sheet_row_labels.append(row)
                    row_index += 1
                    element_index += 1
                    data_storage.append(data)

            self.balance_sheet_data = data_storage
        else:
            print(f"\n[Table Found]  - '{table}' was detected '{self.db.db_filename}'. Fetching data from database.\n")
            self.balance_sheet_data = self.db.get_data_from_table("balance_sheet")

    '-------------------------------------------------------'
    def get_balance_sheet_data(self) -> list:
        '''
        - Returns the data collected from the balance sheet.
        :return: list
        '''
        return self.balance_sheet_data

    '-------------------------------------------------------'
    def set_cash_flow_data(self):
        table = "cash_flow"
        if not self.exists_cash_flow:
            # Check if we are at the page within the website that we should be at.
            if self.browser.current_url != self.financial_page_url:
                self.goto_page_name("financial_page", self.ticker)

            main_run = True
            # Keeps track of the index for the row.
            row_index = 74
            element_index = 74
            # List to hold data
            data_storage = []
            print("--------------------------------------------------------\n\n")
            while main_run:
                i = 1
                data = []
                running = True
                # Get the row label
                row_xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{row_index}]/div[1]/span"
                row = self.read_data(row_xpath)
                if row == "SEC Link":
                    main_run = False
                else:
                    print(f"[Collected] -    {row}")
                    while running:
                        try:
                            # Get the data from the xpath
                            xpath = f"/html/body/div/div/main/div[3]/div/div/div/div[4]/div[{element_index}]/div[3]/div[{i}]"
                            d = self.read_data(xpath)
                            data.append(d)
                            i += 1
                        except NoSuchElementException:
                            running = False
                    self.cash_flow_row_labels.append(row)
                    row_index += 1
                    element_index += 1
                    data_storage.append(data)

            self.cash_flow_data = data_storage
        else:
            print(f"\n[Table Found]  - '{table}' was detected '{self.db.db_filename}'. Fetching data from database.\n")
            self.cash_flow_data = self.db.get_data_from_table("cash_flow")

    '-------------------------------------------------------'
    def get_cash_flow_data(self) -> list:
        '''
        - Gets the cash flow data.
        :return: list
        '''
        return self.cash_flow_data
    '-------------------------------------------------------'
    ################################################################################################################
    ################################################################################################################
    #                                                   Dataframe Creation
    '-------------------------------------------------------'
    def create_summary_page_df(self) -> pd.DataFrame:
        if not self.exists_summary:
            # Checks if there is data in the dataframe
            if not self.summary_page_data:
                self.set_summary_page_data()
            summary_page_data = self.get_summary_page_data()
            print("\n[Summary] Data gathered from scraper.\n")
            # Create a dictionary for us to insert into a dataframe.
            d = {}
            for i in range(len(summary_page_data)):
                d[self.summary_page_row_labels[i]] = summary_page_data[i]

            # Get the column labels
            col_labels = self.get_summary_page_col_labels()

            # Dataframe creation
            df = pd.DataFrame(d)
            df = df.transpose()

            # Insert the column labels
            df.columns = col_labels
            return df
        else:
            print("\n[Summary] Data gathered from database.\n")
            return self.db.get_data_from_table("summary")

    '-------------------------------------------------------'
    def create_income_statement_df(self) -> pd.DataFrame:
        if not self.exists_income_statement:
            # Checks if there is data in the dataframe
            if not self.income_statement_data:
                self.set_income_statement_data()

            income_statement_data = self.get_income_statement_data()

            print("\n[Income Statement] Data gathered from scraper.\n")
            # Create a dictionary for us to insert into a dataframe
            d = {}
            for i in range(len(income_statement_data)):
                d[self.income_statement_row_labels[i]] = income_statement_data[i]

            # Get the column label
            col_labels = self.get_financial_page_col_labels()

            # Dataframe creation
            df = pd.DataFrame(d)
            df = df.transpose()

            # Insert the column labels
            df.columns = col_labels
            return df
        else:
            print("\n[Income Statement] Data gathered from database.\n")
            return self.db.get_data_from_table("income_statement")


    '-------------------------------------------------------'
    def create_balance_sheet_df(self) -> pd.DataFrame:
        if not self.exists_balance_sheet:
            if not self.balance_sheet_data:
                self.set_balance_sheet_data()
            print("\n[Balance Sheet] Data gathered from scraper.\n")
            balance_sheet_data = self.get_balance_sheet_data()

            # Create a dictionary for us to insert into a dataframe
            d = {}
            for i in range(len(balance_sheet_data)):
                d[self.balance_sheet_row_labels[i]] = balance_sheet_data[i]

            # Get the columns label
            col_labels = self.get_financial_page_col_labels()

            # Dataframe creation
            df = pd.DataFrame(d)
            df = df.transpose()

            # Insert the column labels
            df.columns = col_labels
            return df
        else:
            print(f"\n[Balance Sheet] Data gathered from database.\n")
            return self.db.get_data_from_table("balance_sheet")

    '-------------------------------------------------------'
    def create_cash_flow_df(self) -> pd.DataFrame:
        if not self.exists_cash_flow:
            if not self.cash_flow_data:
                self.set_cash_flow_data()
            cash_flow_data = self.get_cash_flow_data()
            print("\n[Cash Flow] Data gathered from scraper.\n")
            # Create a dictionary for us to insert into a dataframe
            d = {}
            for i in range(len(cash_flow_data)):
                d[self.cash_flow_row_labels[i]] = cash_flow_data[i]

            # Get the columns label
            col_labels = self.get_financial_page_col_labels()

            # Dataframe creation
            df = pd.DataFrame(d)
            df = df.transpose()

            # Insert the column labels
            df.columns = col_labels
            return df
        else:
            print("\n[Cash Flow] Data gathered from database.\n")
            return self.db.get_data_from_table("cash_flow")
