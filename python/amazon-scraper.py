from bs4 import BeautifulSoup
import requests
import mysql.connector as mysql
import re
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Function to extract Product Title
def get_title(soup):

    try:
        # Outer Tag Object
        title_string = soup.find(
            "span", attrs={"id": 'productTitle'}).string.strip()

    except AttributeError:
        title_string = ""

    return title_string

# Function to extract Product Price


def get_price(soup):

    try:
        price = soup.find(
            "span", attrs={'id': 'priceblock_ourprice'}).string.strip()
        price_pattern = '(\d+\.\d+)'
        price_match = re.search(price_pattern, price)
        price = price_match.group(1)

    except AttributeError:
        price = ""

    return price

# Function to extract Product Rating


def get_rating(soup):

    try:
        rating = soup.find(
            "i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).string.strip()

    except AttributeError:

        try:
            rating = soup.find(
                "span", attrs={'class': 'a-icon-alt'}).string.strip()
        except:
            rating = ""

    return rating

# Function to extract Number of User Reviews


def get_review_count(soup):
    try:
        review_count = soup.find(
            "span", attrs={'id': 'acrCustomerReviewText'}).string.strip()

    except AttributeError:
        review_count = ""

    return review_count

# Function to extract Availability Status


def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip()

    except AttributeError:
        available = ""

    return available

# Write to the database


def write_db(conn, cursor, url_idx, price):
    timestamp = time.time()
    cursor.execute("INSERT into scrape_data (url_idx, price, timestamp) VALUES (%s, %s, %s)",
                   (url_idx, price, timestamp))
    conn.commit()

# Send out an email


def send_email(type, price, old_price, soup, url):
    recipients = ['twripley@gmail.com', 'dianna.eastcoastgirl@gmail.com']
    #recipients = ['twripley@gmail.com']
    sender = 'twripley@gmail.com'
    message = MIMEMultipart('alternative')
    message['From'] = 'Tyler Ripley <twripley@gmail.com>'
    message['To'] = ", ".join(recipients)

    product_desc = get_title(soup)
    rating = get_rating(soup)
    reviews = get_review_count(soup)
    availability = get_availability(soup)

    if type == 'initial':
        message['Subject'] = f"Starting to Price Track = {product_desc}"

        html = f"""\
        <html>
        <body>
            <h3>Starting to Price Track</h3>
            <p>I will start to track the price of the following item on Amazon</p>
            <p>Item: <a href=\"{url}\">{product_desc}</a><br />
            Price: <b>{price}</b><br />
            Product Rating: <b>{rating}</b><br />
            Number of Product Reviews: <b>{reviews}</b><br />
            Availability: <b>{availability}</b>
            </p>
            <p>This script will run every 6 hours and email you if the price drops more than 15%</p>

        </body>
        </html>
        """
    elif type == 'drop':
        message['Subject'] = f"Price Drop = {product_desc}"
        html = f"""\
        <html>
        <body>
            <h1>Price Drop!</h1>
            <p>The following item has dropped price on Amazon!</p>
            <p><a href=\"{url}\">{product_desc}</a><br />
            Old Price: <b>{old_price}</b><br />
            New Price: <b>{price}</b></p>
            <p>
            Product Rating: <b>{rating}</b><br />
            Number of Product Reviews: <b>{reviews}</b><br />
            Availability: <b>{availability}</b>
            </p>
        </body>
        </html>
        """

    part1 = MIMEText(html, "html")
    message.attach(part1)

    mail_server = 'relay.tylerripley.int'
    with smtplib.SMTP(mail_server, '25') as server:
        server.sendmail(sender, recipients, message.as_string())


if __name__ == '__main__':

    # Headers for request
    HEADERS = ({'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 RuxitSynthetic/1.0 v6613970779 t55095 ath889cb9b1 altpub cvcv=2 smf=0',
                'Accept-Language': 'en-US, en;q=0.5'})

    # Connect to the database
    # Parse database connection info
    server = 'sql.tylerripley.int'
    username = 'furgussen'
    password = 'G3nt00Rul3'
    database = 'scraper'

    # Connect to the Infratools database
    conn = mysql.connect(host=server, user=username,
                         password=password, database=database)
    cursor = conn.cursor()

    # Get the URL's
    cursor.execute("SELECT * from scrape_url WHERE site=%s", ('amazon',))
    rows = cursor.fetchall()

    for thisRow in rows:
        webpage = requests.get(thisRow[1], headers=HEADERS)

        # Soup Object containing all data
        soup = BeautifulSoup(webpage.content, "lxml")

        # Function calls to display all necessary product information
        # print("Product Title =", get_title(soup))
        # print("Product Price =", get_price(soup))
        # print("Product Rating =", get_rating(soup))
        # print("Number of Product Reviews =", get_review_count(soup))
        # print("Availability =", get_availability(soup))
        # print()
        # print()

        # Get the timestamp for the database
        timestamp = time.time()
        # If the product is 15% lower than the last price, let me know
        price = float(get_price(soup))

        # What was the old price?
        cursor.execute(
            "SELECT * from scrape_data WHERE url_idx=%s ORDER BY timestamp DESC LIMIT 1", (thisRow[0],))
        row = cursor.fetchone()

        if row is not None:
            old_price = float(row[2])
            compare_price = old_price - (old_price * 0.15)
            if price <= compare_price:
                # Then we have a deal!
                print('We have a deal')

                # Send out an email
                send_email('drop', price, old_price, soup, thisRow[1])
                # Write it to the database
                write_db(conn, cursor, thisRow[0], price)
            else:
                print('No Deal')

                # Write it to the database
                write_db(conn, cursor, thisRow[0], price)
        else:
            # We've never scraped this item before, so just record the price
            write_db(conn, cursor, thisRow[0], price)

            # Send out an initial Email
            send_email('initial', price, 'no old price', soup, thisRow[1])
