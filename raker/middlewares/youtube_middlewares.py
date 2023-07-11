from selenium.webdriver.support.ui import WebDriverWait

from scrapy.http import HtmlResponse

from scrapy_selenium import SeleniumRequest, SeleniumMiddleware

import time


class YouTubeMiddleware(SeleniumMiddleware):
    """
    Inherit from the scrapy_selenium.SeleniumMiddleware class to handling the requests using the selenium d
    river
    for The YouTube page
    """

    def process_request(self, request, spider):
        """Process a request using the selenium driver if applicable"""

        if not isinstance(request, SeleniumRequest):
            return None

        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie(
                {
                    'name': cookie_name,
                    'value': cookie_value
                }
            )

        if request.wait_until:
            WebDriverWait(self.driver, request.wait_time).until(
                request.wait_until
            )

        scroll_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(3.0)
            # Calculate new scroll height and compare with last scroll height
            new_scroll_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_scroll_height == scroll_height:
                break
            scroll_height = new_scroll_height

        if request.screenshot:
            request.meta['screenshot'] = self.driver.get_screenshot_as_png()

        if request.script:
            self.driver.execute_script(request.script)

        body = str.encode(self.driver.page_source)

        # Expose the driver via the "meta" attribute
        request.meta.update({'driver': self.driver})

        return HtmlResponse(
            self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request
        )
