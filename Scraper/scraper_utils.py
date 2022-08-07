

class ScraperUtilities:
    def __init__(self, browser):
        self.browser = browser
    '''-----------------------------------'''
    def click_button(self, xpath: str):
        '''
        :param browser: Browser object of the scraper.
        :param xpath: Xpath to object that will be clicked.
        :return: None
        '''
        try:
            # Clicks button at xpath.
            self.browser.find_element_by_xpath(xpath).click()
        except Exception:
            print(f'-- Element could not be found.')

    '''-----------------------------------'''
    def submit_data(self, xpath: str, data):
        '''
        :param xpath: Xpath to object that data will be submitted to.
        :param data: Data to enter in the field.
        :return: None
        '''
        #try:
        # Sends data to field.
        self.browser.find_element_by_xpath(xpath).send_keys(data)
        #except NoSuchElementException:
          #  print(f' -- Element could not be found.')

    '''-----------------------------------'''
    def read_data(self, xpath:str):
        '''
        :param browser: Selenium browser object.
        :return: None
        '''
        data = self.browser.find_element_by_xpath(xpath).text
        return data
    '''-----------------------------------'''
    def goto_page(self,url: str):
        '''
        - Will take the browser to a page according to the URL.
        :param url:
        :return: None
        '''
        self.browser.get(url)
    '''-----------------------------------'''
    def create_browser(self, url, ticker=None):
        '''
        :param url: The website to visit.
        :return: None
        '''
        if ticker == None:
            self.browser.get(url)
        else:
            url += ticker
            self.browser.get(url)

    '''-----------------------------------'''
    def goto_page_name(self,page_name,ticker):
        '''
        - Will go to the summary page within ROIC.ai.
        :param page_name: Name of the page to navigate to.
        :param ticker: Company to navigate to.
        :return: None
        '''
        dict = {"summary_page": f"https://roic.ai/company/{ticker}",
                "financial_page": f"https://roic.ai/financials/{ticker}"}
        self.create_browser(dict[page_name])

    '''-----------------------------------'''
    def format_col_labels(self, cols) -> list:
        '''
        - Will keep cut the list at "TTM". Example: [0,1,2,TTM,3,4,5,6] -> [0,1,2,TTM]
        :param cols: The list of columns.
        :return: list
        '''
        l = []
        for c in cols:
            l.append(c)
            if c == "TTM":
                break
        return l
