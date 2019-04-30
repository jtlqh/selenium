from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db import Review, Product
import time, datetime
import re



def date_mapper(input_value, input_key):
    ''' convert months, years to days '''
    key = input_key.lower().strip('s')
    names = ['year', 'month']
    values = [365, 30]
    try:
        idx = names.index(key)
        return 'days', values[idx] * float(input_value)
    except:
        return key + 's', float(input_value)
    

# Windows users need to specify the path to chrome driver you just downloaded.
# You need to unzip the zipfile first and move the .exe file to any folder you want.
# driver = webdriver.Chrome(r'path\to\where\you\download\the\chromedriver.exe')
driver = webdriver.Chrome(r'C:\chromedriver.exe')

driver.get("https://www.verizonwireless.com/smartphones")

product_size = driver.find_element_by_xpath('//div[@ class="pad12 noLeftPad"]').text
product_size = int(re.findall('\d+',product_size)[0])

products = [''] * product_size
for n in range(product_size):
        products[n] = driver.find_element_by_xpath('//div[@class="tile-outer  displayFlex rowWrap"]/div[{}]'.format(n+1)).get_attribute('id')


for i in range(product_size):
#for i in range(1):
    #print(products[i])    
    wait_event = WebDriverWait(driver, 10)
    product_button = wait_event.until(EC.element_to_be_clickable((By.ID, products[i])))    
    product_button.click()


    #wait_event = WebDriverWait(driver, 10)
    strings = wait_event.until(EC.presence_of_all_elements_located((By.XPATH,
        '//li[@class="listStyleTypeNone displayInlineBlock"]')))
    brand = strings[2].find_element_by_xpath('./a/span').text
    print(brand)

    # some phones do not have any reivews, skip review and go back to smartphone page
    try:
        num_reviews = driver.find_element_by_xpath('//span[@class="padLeft6 cursorPointer"]').text
        num_reviews = int(re.findall('\d+', num_reviews)[0])
        print('total reviews {}'.format(num_reviews))
    except:
        driver.get("https://www.verizonwireless.com/smartphones")
        continue

    product_name = driver.find_element_by_xpath('//*[@id="tile_container"]/div[1]/div[1]/h1').text
    product_name = product_name.replace(r'®','')
    print(product_name)


    skuId = driver.find_element_by_xpath('//span[@class="marginLeftAuto  color_000 NHaasDS55Rg fontSize_10"]').text
    skuId = skuId.split()[1]
    print(skuId)

    # colors
    #wait_event = WebDriverWait(driver, 10)
    color_list = wait_event.until(EC.presence_of_all_elements_located((By.XPATH,
        '//div[@class="col-xs-3 colorSection textAlignCenter noSidePad radioGroup positionRelative"]')))
    colors = ''
    for color in color_list:
        colors += color.find_element_by_xpath('./label').text + ', '

    # storage
    try:
        #wait_event = WebDriverWait(driver, 10)
        storage_list = wait_event.until(EC.presence_of_all_elements_located((By.XPATH,
            '//div[@class="grow1basis0 priceSelectorColumn radioGroup positionRelative"]')))

        storages = [''] * len(storage_list) 
        prices = [0] * len(storage_list)
    
        for i, storage in enumerate(storage_list):
            storages[i] = storage.find_element_by_xpath('./input').get_attribute('id')

            # price is based on storage size, click storage tab, related price changed
            storage.click()
            wait_event = WebDriverWait(driver, 10)
            # 0: monthly price for 24 months, 1: retail price
            price_list = wait_event.until(EC.presence_of_all_elements_located((By.XPATH,
                    '//div[@class="col-sm-12 noSidePad fontSize_16 fontDSStd-75Bd textAlignLeft contractDetail"]')))
            price = price_list[-1].find_element_by_xpath('./span').text
            prices[i] = float(re.findall('[\d.]+',price)[0])
    except:
            # if no storage option
            #wait_event = WebDriverWait(driver, 10)
            price_list = wait_event.until(EC.presence_of_all_elements_located((By.XPATH,
                    '//div[@class="col-sm-12 noSidePad fontSize_16 fontDSStd-75Bd textAlignLeft contractDetail"]')))

            storages = [''] 
            prices = [0] 
            price_list = wait_event.until(EC.presence_of_all_elements_located((By.XPATH,
                    '//div[@class="col-sm-12 noSidePad fontSize_16 fontDSStd-75Bd textAlignLeft contractDetail"]')))
            price = price_list[-1].find_element_by_xpath('./span').text
            prices[0] = float(re.findall('[\d.]+',price)[0])
 


    spec_button = driver.find_element_by_id('specsLink')
    spec_button.click()

   
    #wait_event = WebDriverWait(driver, 10)
    specs_names = wait_event.until(EC.presence_of_all_elements_located((By.XPATH,
            '//div[@class="col-sm-3 col-xs-4 specListTitle pad10 noLeftPad"]')))
    
    specs_names = [n.text for n in specs_names]
        
    #wait_event = WebDriverWait(driver, 10)
    spec_values = wait_event.until(EC.presence_of_all_elements_located((By.XPATH,
        '//div[@class="specListItem col-sm-9  col-xs-8  pad10 "]')))
    
    spec_values = [v.text for v in spec_values]
    
    
    for stog_cnt in range(len(storages)):
        for spc_cnt in range(len(specs_names)):
            item = Product(
                store         = 'verizon',
                product_name  = product_name,
                skuId         = skuId,
                brand         = brand,
                color         = colors,
                storage       = storages[stog_cnt],
                price         = prices[stog_cnt],
                spec_name     = specs_names[spc_cnt],
                spec_value    = spec_values[spc_cnt],
                )                
            item.save()
            

    # Click review button to go to the review section
    review_button = driver.find_element_by_id('reviewsLink')
    review_button.click()

       
    for page in range(num_reviews//10 + 1):  # 10 reviews per page, exampe 83 reviews needs 9 pages
    #for page in range(1):
        try:
            print("Scraping Page number " + str(page + 1))
            
            # Find all the reviews. The find_elements function will return a list of selenium select elements.
            # Check the documentation here: http://selenium-python.readthedocs.io/locating-elements.html
            #wait_event = WebDriverWait(driver, 10)
            reviews = wait_event.until(EC.presence_of_all_elements_located((By.XPATH, 
                        '//div[@class="row border_grayThree onlyTopBorder noSideMargin"]')))
            # Iterate through the list and find the details of each review.
            #print('reviews{}'.format(len(reviews)))
            for review in reviews:
                   
                # Initialize an empty dictionary for each review

                
                # Use try and except to skip the review elements that are empty. 
                # Use relative xpath to locate the title.
                # Once you locate the element, you can use 'element.text' to return its string.
                # To get the attribute instead of the text of each element, use 'element.get_attribute()'
                try:
                    title = review.find_element_by_xpath('.//div[@class="NHaasDS75Bd fontSize_12 wrapText"]').text   
                except:
                    continue
                #print('title = {}'.format(title))

                # Use relative xpath to locate text, username, date_published, rating.
                # Your code here
                
                text = review.find_element_by_xpath('.//span[@class="pad6 onlyRightPad"]').text
                #    print('text = {}'.format(text))
                username = review.find_element_by_xpath(
                    './/span[@class="padLeft6 NHaasDS55Rg fontSize_12 pad3 noBottomPad padTop2"]').text
                #    print('username = {}'.format(username))
                date_published = review.find_element_by_xpath(
                    './/span[@class="NHaasDS55Rg fontSize_12  pad3 noBottomPad padTop2"]').text
                # convert date from 'days ago', 'months ago', 'years ago' to 'month/day/year' format
                parsed_s = [date_published.split()[:2]]
                time_dict = dict(date_mapper(amount, unit) for amount, unit in parsed_s)            
                dt = datetime.timedelta(**time_dict)
                date_published = datetime.datetime.now() - dt
                #    print('date_published = {}'.format(date_published))
                rating = review.find_element_by_xpath(
                    './/span[@class="positionAbsolute top0 left0 overflowHidden color_000"]').get_attribute('style')
                rating = int(re.findall('\d+', rating)[0])/20
                #    print('rating = {}'.format(rating))

                # some reviews do not have recommending check box, trying to access the element will got an exception
                try:
                    recommending = review.find_element_by_xpath('.//span[@class="padTop3 padLeft6"]').text
                    recommending = (recommending.split(',')[0].lower() == 'yes')
                except:
                    recommending =''
                helpful = review.find_element_by_xpath(
                    './/button[@class="border_grayThree NHaasDS55Rg fontSize_12 height48 width100p positiveReviewFeedBack"]/span').text
                helpful = int(re.findall('\d+', helpful)[0])
                unhelpful = review.find_element_by_xpath(
                    './/button[@class="border_grayThree NHaasDS55Rg fontSize_12 height48 width100p negativeReviewFeedBack"]/span').text
                unhelpful = int(re.findall('\d+', unhelpful)[0])
                # if saving data to mysql triggers exception error, skip this data row
                try:
                    current = Review(
                        store          = 'verizon',
                        skuId          = skuId,
                        username       = username,
                        text           = text,
                        title          = title,
                        date_published = date_published,
                        rating         = rating,
                        recommending   = recommending,
                        helpful        = helpful,
                        unhelpful      = unhelpful
                        )
                    current.save()
                    
                except:
                    continue

            # end of for loop
            

            
            # Locate the next button element on the page and then call `button.click()` to click it.
            button = wait_event.until(EC.element_to_be_clickable((By.XPATH, 
                    '//li[@class="nextClick displayInlineBlock padLeft5 "]')))
            button.click()
            #time.sleep(2)

        except Exception as e:
            print(e)
            break
            
    # end of while loop

    # go back to the main page
    driver.get("https://www.verizonwireless.com/smartphones/")
    time.sleep(1)
                    
    
        
print('closing driver and file')
driver.close()
        
        