# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Sets executable path and initializes a browser
    # With these two lines of code, we are creating an instance of a Splinter browser
    # We're also specifying that we'll be using Chrome as our browser
    # **executable_path is unpacking the dictionary we've stored the path in
    # headless=False means that all of the browser's actions will be displayed in a Chrome window so we can see them
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    # This line of code tells Python that we'll be using our mars_news function to pull this data
    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "mars_hemispheres": mars_hemisphere(browser), 
      "last_modified": dt.datetime.now()
    }
   # Stop webdriver and return data
    browser.quit()
    return data    
    
# Making a scraping function
def mars_news(browser):
    
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title` (scrapes article title)
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    
    except AttributeError:
        return None, None

    # Instead of having our title and paragraph printed within the function, we want to return them from the function so they can be used outside of it
    return news_title, news_p


# ### Featured Images

# Picture function
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    # With the index chained, we're specifying to click the 2nd button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')


    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# Mars facts function
def mars_facts():
    # Add try/except for error handling
    try:
        # Creating a new dataframe, using read_html that pulls HTML tables (index 0 to pull first table)
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    #Here, we assign columns to the new DataFrame for additional clarity.
    df.columns=['description', 'Mars', 'Earth']

    # turning the Description column into the DataFrame's index
    # inplace=True means that the updated index will remain in place, without having to reassign the DataFrame to a new variable
    df.set_index('description', inplace=True)

    # Drop top row 
    df.drop('Mars - Earth Comparison', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(index_names=False)

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

# Mars hemisphere function
def mars_hemisphere(browser):
    # Visit URL
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles
    hemisphere_image_urls = []

    # Parse the resulting html with soup
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # List of all possible images
    hemisphere_list = news_soup.find_all('div', class_ = 'item')
    # For Loop
    for hemisphere in hemisphere_list:
        # Get link stem 
        link = hemisphere.find('a',class_='itemLink product-item').get('href')
        # Go to inner page
        browser.visit(f'{url}{link}')
        # Inner page parse
        inner_page = browser.html
        inner_page_soup= soup(inner_page, 'html.parser')
        # Get title
        try:
            title = inner_page_soup.find('h2', class_='title').get_text()
        
        except AttributeError:
            return None
    
    # Get image URL
        try:
            li = inner_page_soup.find('li')
            image_stem = li.find('a').get('href')
        
        except AttributeError:
            return None
            
        image_link =f'{url}{image_stem}'

        # Add to list
        hemisphere_image_urls.append({'img_url': image_link, 'title':title})
        # Go back 1 level
        browser.back()

    return hemisphere_image_urls

