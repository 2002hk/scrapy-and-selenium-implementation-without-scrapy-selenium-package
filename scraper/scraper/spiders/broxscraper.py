import scrapy,logging,time,datetime,os
from scrapy.spiders.init import InitSpider
from scrapy.utils.log import configure_logging
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser
from scraper.items import BroxbourneItem
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
#from pyvirtualdisplay import Display
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.common.action_chains import ActionChains
from scraper.items import SearchDocItem
import undetected_chromedriver as uc
from selenium_stealth import stealth

def wait_milli_second(milliseconds):
    seconds=milliseconds/1000.0
    time.sleep(seconds)

class BroxscraperSpider(scrapy.Spider):
    name = "broxscraper"
    allowed_domains = ["https://planning.broxbourne.gov.uk/"]
    start_urls = ["https://planning.broxbourne.gov.uk/Planning/lg/plansearch.page?org.apache.shale.dialog.DIALOG_NAME=gfplanningsearch&Param=lg.Planning"]
    start_date = '01/01/2020'
    end_date = '01/12/2021'
    run_headless = 'NO'
    config=None
    driver=None
    debug='False'
    PAUSE_TIME=None
    PAUSE_TIME_SMALL=None

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )

    def __init__(self,start_date=None,end_date=None,debug=None,*args,**kwargs):
        InitSpider.__init__(self)
        if start_date:
            self.log('##### command start_date: %s ####' % start_date)
            self.validate(start_date)
            self.start_date=start_date
        else:
            self.log('### command start date; %s ###' % self.start_date)
        if end_date:
            self.log('### Command end date: %s ###' % end_date)
            self.validate(end_date)
            self.end_date = end_date
        else:
            self.log('### Command end date: %s ###' % self.end_date)

        if debug:
            self.log('### Command debug: %s ###' % debug)
            self.debug = debug
        else:
            self.log('### Command debug: %s ###' % self.debug)

        self.PAUSE_TIME = 5
        self.PAUSE_TIME_SMALL = 2
            
        ### create manually driver
        browser_executable_path=ChromeDriverManager().install()
        if self.run_headless == 'NO':
            print('Running Selenium with head')
            options = webdriver.ChromeOptions()

            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-notifications')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-infobars')
            #options.add_argument('--auto-open-devtools-for-tabs')
            
            options.add_argument('--blink-settings=imagesEnabled=false')

            #load fast
            options.add_argument('--disable-extensions')  # Disable extensions
            options.add_argument('--disable-dev-shm-usage')

            #service = Service(ChromeDriverManager().install())
            #self.driver = webdriver.Chrome(service=service, options=options)

            #none trackable driver 
            self.driver = uc.Chrome(options=options, executable_path=browser_executable_path)

            stealth(self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                )

            self.driver.implicitly_wait(60)
        else:
            options = webdriver.ChromeOptions()

            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')
            options.headless = True

            # chrome://inspect/#devices for inspect
            # options.add_argument('--remote-debugging-port=9222')  # Open DevTools port
            # options.add_argument('--remote-allow-origins=*')  # Allow all remote origins
            # options.debugger_address = "127.0.0.1:9222"

            #options.add_argument("--window-size=1920,1080")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-notifications')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-infobars')

            options.add_argument('--blink-settings=imagesEnabled=false')

            #load fast
            # options.add_argument('--disable-extensions')  # Disable extensions
            options.add_argument('--disable-dev-shm-usage')

            #service = Service(ChromeDriverManager().install())
            #self.driver = webdriver.Chrome(service=service, options=options)

            self.driver = uc.Chrome(options=options, executable_path=browser_executable_path)

            stealth(self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                )

            self.driver.implicitly_wait(60)

        #inject driver js code
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
            }
        )
    def validate(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%d/%m/%Y')
        except ValueError:
            raise ValueError("Incorrect data format, should be DD/MM/YYYY")    

    def search_event(self):
        self.log('#### do advance search####')
        self.driver.implicitly_wait(120)
        self.driver.get(self.start_urls[0])
        self.log("opened %s...." % self.start_urls[0] )
        time.sleep(self.PAUSE_TIME)
        wait_milli_second(1500)

        try:
            self.log("wait until a specific element is present")
            cookiesbtn=WebDriverWait(self.driver,10).until(
                EC.presence_of_element_located((By.XPATH,'//a[text()="Accept all cookies"]'))
            )
            wait_milli_second(900)
            self.driver.execute_script("arguments[0].scrollIntoView();",cookiesbtn)
            cookiesbtn.click()

        except Exception as e:
            print(f"Error: {e}")

        wait_milli_second(500)

        search_adv_btn = self.driver.find_element(By.XPATH,'//a[contains(text(),"Advanced search")]')
        self.driver.execute_script("arguments[0].scrollIntoView();", search_adv_btn)
        search_adv_btn.click()

        wait_milli_second(500)
        time.sleep(self.PAUSE_TIME)

        self.driver.find_element(By.XPATH,'//select/option[@value="F"]').click()

        received_dateFrom_rdio_btn = self.driver.find_element(By.ID,'AdvanceSearch_ReceivedBetween')
        self.driver.execute_script("arguments[0].scrollIntoView();", received_dateFrom_rdio_btn)
        wait_milli_second(500)
        received_dateFrom_rdio_btn.click()

        input_received_start = self.driver.find_element(By.XPATH,'//input[@name="AdvanceSearch.ReceivedFromDate"]')
        self.driver.execute_script("arguments[0].scrollIntoView();", input_received_start)
        wait_milli_second(500)
        input_received_start.send_keys(self.start_date)

        input_received_end = self.driver.find_element(By.XPATH,'//input[@name="AdvanceSearch.ReceivedToDate"]')
        self.driver.execute_script("arguments[0].scrollIntoView();", input_received_end)
        wait_milli_second(500)
        input_received_end.send_keys(self.end_date)
        
        wait_milli_second(500)
        search_btn = self.driver.find_element(By.XPATH,'//a[text()="Search"]')
        self.driver.execute_script("arguments[0].scrollIntoView();", search_btn)
        wait_milli_second(500)
        search_btn.click()



    def parse(self,response):

        self.search_event()
        current_reponse=response.replace(body=self.driver.page_source)
        

        while True:
           

            self.original_window=self.driver.current_window_handle
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            app_links_ele=self.driver.find_elements(By.XPATH,"//a[span[text()='Full']]")
            #app_links_ele=response.xpath("//a[span[text()='Full']]/@data-redirect-url")
            print(app_links_ele)
            print(len(app_links_ele))
          
            app_links=[]


            for ele in app_links_ele:
                app_links.append(ele.get_attribute('data-redirect-url'))


            for link in app_links:
                item = BroxbourneItem()
                main_url='https://planning.broxbourne.gov.uk/'
                relative_url=main_url+link

               
                ###open another tab
                self.driver.execute_script("window.open('');")

                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.get(relative_url)
                time.sleep(5)
                det_response = response.replace(body=self.driver.page_source)

                item['appNo']=det_response.xpath('//span[@id="spnApplicationId"]/text()').get()
                item['address']=det_response.xpath('//label[@id="applicationDisplayAddress"]/text()').get()
                item['proposal']=det_response.xpath("//td[label[text()='Proposal']]/following-sibling::td/label/text()").get()
                item['applicant']=det_response.xpath("//td[label[text()='Applicant']]/following-sibling::td/label/text()").get()
                item['agent']=det_response.xpath("//td[label[text()='Agent']]/following-sibling::td/label/text()").get()
                item['planOff']=det_response.xpath("//td[label[text()='Planning officer']]/following-sibling::td/label/text()").get()
                item['ward']=det_response.xpath("//td[label[text()='Ward']]/following-sibling::td/label/text()").get()
                item['co_ords']=det_response.xpath("//td[label[text()='Co-ordinates']]/following-sibling::td/label/text()").get()
                item['validated']=det_response.xpath("//td[label[text()='Validated']]/following-sibling::td/label/text()").get()
                item['consultation']=det_response.xpath("//td[label[text()='Consultation Period']]/following-sibling::td/label/text()").get()
                item['neighNotifd']=det_response.xpath(" //td[label[text()='Neighbours notified']]/following-sibling::td/label/text()").get()
                item['consultNotifd']=det_response.xpath("//td[label[text()='Consultees notified']]/following-sibling::td/label/text()").get()
                item['decided']=det_response.xpath("//td[label[text()='Decided']]/following-sibling::td/label/text()").get()
                item['appealSub']=det_response.xpath("//td[label[text()='Appeal submitted?']]/following-sibling::td/label/text()").get()

                records=self.driver.find_element(By.XPATH,'//a[@role="tab" and @data-toggle="tab" and contains(@href, "#tabDocuments")]//span[@id="spanDocumentCount"]').text
                self.driver.find_element(By.XPATH,'//li[@id="Documents_tab"]').click()
        
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)


                docpage=response.replace(body=self.driver.page_source)


                ### Find out the total number of records
                print(records)
                print('******type**',type(records))

                number = int(records.strip("[]"))

                print('the total number of records',number)

                if number%10==0:
                    pages=number//10
                else:
                    pages=(number//10)+1

                print('the total number of pages',pages)

                if number==0:
                ## if no documents close tab
                    pass
                
                elif number>0:
            
                    ## if document present
                    #### this yield statement is for the first document which is already open

                    item2=SearchDocItem()
                    i=1
                    while i<=pages:
                        ### if i<pages the while loop will end 
                        #### finding out the xpath which is not present takes a lot of time for driver to realize hence takes lot of time to break loop
                        ### that is why avoided using click on the element which is not present to increase speed


                        rows=docpage.xpath('//div[@class="row btspace"]')
                        for j in range(1,len(rows)):

                            item2['date']=rows[j].xpath('.//div[@class="col-xs-2"]/text()').get()
                            item2['doclink']=rows[j].xpath('.//div[@class="col-xs-3"]/a/@href').get()
                            item2['doctype']=rows[j].xpath('.//div[@class="col-xs-4"]/text()').get()
                            item2['appNo']=response.xpath('//span[@id="spnApplicationId"]/text()').get()

            
                        yield item2
                        if i==pages:
                            print('done pagination')
                            break
                        Xpath=f'//a[@class="btn-primary" and text()="{i+1}"]'
                

                
                        self.driver.find_element(By.XPATH,Xpath).click()
                
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(6)
                

                        
                        i=i+1

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                
                time.sleep(self.PAUSE_TIME)
    

                yield item


            

            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.driver.find_element(By.XPATH,'//a[@class="btn-primary" and text()="Next"]').click()
               
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print('****************** Next page clicked***********************')
                time.sleep(50)

            except Exception:
                print("All pages Scraped")
                break
        

        self.driver.quit() 