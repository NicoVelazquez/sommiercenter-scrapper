from bs4 import BeautifulSoup
import requests
import pandas as pd

colchones_products = {'name': [], 'url': [], 'category': [], 'price': [], 'price_promo': [], 'keys': [], 'values': []}


def colchones():
    # url = 'https://sommiercenter.com/colchones'
    # url = 'https://sommiercenter.com/sommier-y-colchon'
    # url = 'https://sommiercenter.com/divanes'
    # url = 'https://sommiercenter.com/camas'
    # url = 'https://sommiercenter.com/blanqueria'
    # url = 'https://sommiercenter.com/muebles'
    url = 'https://sommiercenter.com/ba-o'
    r = requests.get(url)
    s = BeautifulSoup(r.text, "html.parser")

    filter_options = s.find("div", {"class": "filter-options"})
    if filter_options:
        # Esto si es Baño
        # categories = filter_options.findAll("ol")[1].findAll("li")
        # Si no es Baño
        categories = filter_options.find.findAll("li")

        # PROD
        for category in categories:
            category_url = category.find("a")["href"]
            category_name = category.find("a").text.strip()
            print(category_name)
            colchones_productos(category_url, category_name)
    else:
        colchones_productos(url, '')

    # DEV
    # colchones_productos(categories[0].find('a')['href'], categories[0].find("a").text.strip())

    createExcel()


def colchones_productos(category_url, category_name):
    global colchones_products

    products = colchones_products_navigate_pages(category_url, [])
    for product in products:
        r = requests.get(product["url"])
        s = BeautifulSoup(r.text, "html.parser")

        # TEST
        print(product['url'])

        price = s.find("span", {"class": "price-final_price"}).find("span", {"class": "price"}).text[1:]
        price_promo = s.find("span", {"class": "promo-price"}).find("span", {"class": "price"}).text[1:]

        characteristics_names = []
        characteristics_values = []

        try:
            product_data_items = s.find("div", {"class": "product data items"}).findAll("div", {"class": "data"})[3]
        except IndexError:
            product_data_items = s.find("div", {"class": "product data items"}).findAll("div", {"class": "data"})[1]

        characteristics_names_table = product_data_items.findAll("th")
        for characteristics_name in characteristics_names_table:
            characteristics_names.append(characteristics_name.text)
        characteristics_values_table = product_data_items.findAll("td")
        for characteristics_value in characteristics_values_table:
            characteristics_values.append(characteristics_value.text)

        colchones_products['name'].append(product['name'])
        colchones_products['url'].append(product['url'])
        colchones_products['category'].append(category_name)
        colchones_products['price'].append(int(price.replace('.', '')))
        colchones_products['price_promo'].append(int(price_promo.replace('.', '')))
        colchones_products['keys'].append(characteristics_names)
        colchones_products['values'].append(characteristics_values)


def colchones_products_navigate_pages(page_url, products):
    r = requests.get(page_url)
    s = BeautifulSoup(r.text, "html.parser")

    products_list = s.findAll("li", {"class": "item product product-item"})
    for product in products_list:
        product_url = product.find("a", {"class": "product-item-link"})["href"]
        product_name = product.find("a", {"class": "product-item-link"}).text.strip()
        products.append({'url': product_url, 'name': product_name})

    # has more products?
    pages = s.find("div", {"class": "pages"})
    if pages:
        next_page_url = pages.find("li", {"class": "pages-item-next"}).find("a")["href"]
        if next_page_url != 'javascript:void(0)':
            return colchones_products_navigate_pages(next_page_url, products)

    return products


def createExcel():
    global colchones_products

    product_keys_index = 0
    for product_keys in colchones_products['keys']:
        k_index = 0
        for k in product_keys:
            if k not in colchones_products:
                colchones_products[k] = [""] * len(colchones_products['keys'])
            colchones_products[k][product_keys_index] = colchones_products['values'][product_keys_index][k_index]
            k_index += 1
        product_keys_index += 1

    del colchones_products['keys']
    del colchones_products['values']

    df = pd.DataFrame.from_dict(colchones_products)
    df.to_excel('bano.xlsx', index=False)
    print("Finished creating excel")


if __name__ == "__main__":
    colchones()
    print("Finished")
