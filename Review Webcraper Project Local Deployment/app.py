from flask import Flask, render_template, request, redirect
import requests
from bs4 import BeautifulSoup as bs
import pymongo

app=Flask("__name__")

def get_html(link):
    link_response=requests.get(link)
    link_html=bs(link_response.text,'html.parser')
    return link_html

@app.route('/', methods=['POST','GET'])
def home_page():
    if request.method == 'POST':
        search_string = request.form['content']
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            db = dbConn['crawlerDB']
            reviews = db[search_string].find({})
            if reviews.count() > 0:
                return render_template('reviews.html', reviews=reviews)
            else:
                flipkart_url="https://www.flipkart.com/search?q="+search_string.replace(" ","+")
                flipkart_html=get_html(flipkart_url)
                big_boxes=flipkart_html.find_all(class_="bhgxx2 col-12-12")
                del big_boxes[0:3]
                box=big_boxes[0]
                product_link="https://www.flipkart.com"+box.div.div.div.a['href']
                product_html=get_html(product_link)
                comment_boxes=product_html.find_all(class_="_3nrCtb")
                table = db[search_string]
                reviews = list()
                for boxes in comment_boxes:
                    try:
                        comment_heading=boxes.div.div.div.p.text
                    except:
                        comment_heading='No Comment Heading'
                    try:
                        customer_name=boxes.div('p',{'class':'_3LYOAd _3sxSiS'})[0].text
                    except:
                        customer_name='No Name'
                    try:
                        comtag=boxes.div.div.find_all(class_="")
                        comment=comtag[0].div.text
                    except:
                        comment='No Comment'
                    try:
                        rating=boxes.div.div.div.div.text
                    except:
                        rating='No Rating'
                
                    mydict = { "Product":search_string,"Customer Name":customer_name,"Comment Heading":comment_heading, "Rating":rating, "Reviews":comment }
                    x = table.insert_one(mydict)
                    reviews.append(mydict)

                return render_template('reviews.html', reviews = reviews[0:-1])

        except:
            return render_template('error.html')

    else:
        return render_template('index.html')

    

@app.route('/about')
def about():
    return render_template('websitevicky.html')

    

if __name__ == "__main__":
    app.run(debug=True)