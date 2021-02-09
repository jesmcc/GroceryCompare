import requests
import json
from bs4 import BeautifulSoup


foodStuffsURL = {'NEWWORLD': {'URL': 'https://www.ishopnewworld.co.nz', 'ID': '60928d93-06fa-4d8f-92a6-8c359e7e846d'}, 'PAKNSAVE': {'URL': 'https://www.paknsaveonline.co.nz', 'ID': '3404c253-577f-45ca-b301-c98312e46efb'}}


def escapeSpaces(str):
    return(str.replace(' ', '%20'))


def getFoodStuffs(gtin, item, brandName):
    if ('countdown' not in item['brand'].lower().split()): # Ensure item is not a countdown brand item
        url = foodStuffsURL[brandName]['URL'] + '/Search?q=' + str(gtin)
        cookies = {'STORE_ID': foodStuffsURL[brandName]['ID']} # Necessary for request to be accepted

        # Request html for new world search result page
        response = requests.get(url, cookies=cookies)

        # Soupify and scrape html
        soup = BeautifulSoup(response.content, 'html.parser')
        data = soup.find('div', {'class': ['js-product-card-footer', 'fs-product-card__footer-container']})

        if (data): # Check if results were found for search
            # Extract json and convert to python dictionary
            data = json.loads(data.get('data-options'))

            # Get the price
            price = data['ProductDetails']['PricePerItem']

            return([price, None])
        elif (brandName == "NEWWORLD"): # If no results could be found and the brand is new world
            name, brand, size = item['name'], item['brand'], item['size']['volumeSize']
            
            # Create new url using the brand, size and name of the item - limit to 1 result
            url = foodStuffsURL[brandName]['URL'] + '/Search?q=' + escapeSpaces(brand + ' ' + size + ' ' + name) + '&ps=1&pg=1'
            
            # Send the new request
            response = requests.get(url, cookies=cookies)

            # Soupify and scrape html
            soup = BeautifulSoup(response.content, 'html.parser')
            data = soup.find('div', {'class': ['js-product-card-footer', 'fs-product-card__footer-container']})

            if (data):
                # Extract json and convert to python dictionary
                data = json.loads(data.get('data-options'))

                # Split words in brand name into list
                brandSubStrs = item['brand'].lower().split()

                # Check if top matching product contains words from the brand name
                for word in brandSubStrs:
                    if (word in (data['productName'].lower())):
                        # Scrape found product's size and check if it equals countdown product size
                        size = soup.find('a', {'class': ['fs-product-card__row-details']})
                        if (size is None): # If the class 'fs-product-card__row-details' couldn't be found
                            size = soup.find('a', {'class': ['fs-product-card__details']})
                        size.find('p').text.lower()

                        if (size == item['size']['volumeSize'].lower()):
                            # Get the price
                            price = data['ProductDetails']['PricePerItem']

                            return([price, 'Showing result for: "%s %s"' % (data['productName'], size)])

    # Return null if no valid products could be found  
    return([None, None]) 


def getCountdown(searchTerm):
    url = 'https://shop.countdown.co.nz/api/v1/products?target=search&search=' + searchTerm
    headers = {'X-Requested-With': 'OnlineShopping.WebApp'} # Necessary for request to be accepted

    if (searchTerm): # Ensure search isn't an empty string
        # Send get request to countdown's api
        response = requests.get(url, headers=headers) 

        # Convert the json into a python dictionary
        data = json.loads(response.text)['products']['items']

        # Declare results dictionary
        results = {}

        if (data): # Check if results were found for search
            for item in data:
                if (item['type'] == 'Product'): # Ensure item is not a promotion or non product type
                    # Retrieve general information about product
                    gtin, name, size = item['barcode'], item['name'], item['size']['volumeSize']
                    
                    # Retrieve countdown prices
                    countdownPrice = item['price']['originalPrice']

                    # Retrieve new world price and warning messages
                    newWorldPrice, newWorldMsg = [(getFoodStuffs(gtin, item, 'NEWWORLD'))[i] for i in (0, 1)]

                    # Retrieve paknsave price and warning messages
                    paknSavePrice, paknSaveMsg = [(getFoodStuffs(gtin, item, 'PAKNSAVE'))[i] for i in (0, 1)]

                    print('%s | %s %s' % (gtin, name, '(' + size + ')' if (size) else ''))
                    print('Countdown: %s' % ('$' + str(countdownPrice)))
                    print('New World: %s %s' % ('$' + str(newWorldPrice) if (newWorldPrice) else 'NOT FOUND', newWorldMsg if (newWorldMsg) else ''))
                    print('PaknSave: %s %s' % ('$' + str(paknSavePrice) if (paknSavePrice) else 'NOT FOUND', paknSaveMsg if (paknSaveMsg) else ''))

                    print('---')

                    # Create product and add it to dictionary
                    product = {"name": name, "size": size, "countdownPrice": countdownPrice, "newWorldPrice": newWorldPrice, "paknSavePrice": paknSavePrice}
                    results[gtin] = product

        else: # Output if no products were found in db
            print('No results could be found for that search.')

    else: # Output if search was an empty string
        print('No search was entered.')

    # Return the search results
    return(results)
    

# getCountdown(input('Search for: '))