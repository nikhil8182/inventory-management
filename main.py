from flask import Flask, render_template, request, redirect
import pyrebase

app = Flask(__name__)
# app.debug=True

config = {
  "apiKey": "AIzaSyD5o6wDopSvuf878qaqnXjmPyZANEwQsl4",
  "authDomain": "inventory-e83ac.firebaseapp.com",
  "projectId": "inventory-e83ac",
  "storageBucket": "inventory-e83ac.appspot.com",
  "messagingSenderId": "202568301540",
  "appId": "1:202568301540:web:a72204375d1426c035a5f1",
  "databaseURL":"https://inventory-e83ac-default-rtdb.firebaseio.com/"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()


def getAllProductId():
    productsData = db.child("products").get().val()
    productIdList = []
    for pid in productsData:
        productIdList.append(pid)
    return productIdList



@app.route('/product_details')
def product_details():
    product_id = request.args.get('product_id')
    # do something with the data
    return render_template('product_details.html', product_id=product_id)

@app.route('/')
def index():

    val = db.child("products").get().val()
    # print(val)
    products = []
    for d in val:
        products.append(val[d])
    print(products)
    return render_template('home.html',products=products)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        product_id = request.form['id']
        obc = request.form['obc']
        min_price = request.form['min_price']
        max_price = request.form['max_price']
        stock = request.form['stock']

        data = {
            "name":name,
            "id":product_id,
            "obc":obc,
            "min_price":min_price,
            "max_price":max_price,
            "stock":stock
        }

        db.child("products").child(product_id).set(data)

        return render_template('popup.html')
    else:
        return render_template('create.html')

@app.route('/point',methods=['GET', 'POST'])
def points():
    global tepProductlist
    tepProductlist.clear()
    if request.method == 'POST':
        pass
    else:
        # print(getAllProductId())
        return render_template('points.html',  pid =getAllProductId())

tepProductlist = []

@app.route('/add-product',methods=['GET', 'POST'])
def addproduct():
    global tepProductlist

    product_id = request.form['id']
    count = request.form['count']
    print(tepProductlist)

    for id in tepProductlist:
        if id['id'] == product_id:
            print("Already exist")
            tepProductlist.remove(id)
        else:
            print("new product")




    productData = db.child("products").child(product_id).get().val()

    data = {
        "name":productData['name'],
        "id": product_id,
        "price":productData['max_price'],
        "min_price":productData['min_price'],
        "obc":productData['obc'],
        "count":count,
        "total_price": int(productData['max_price']) * int(count)
    }
    tepProductlist.append(data)

    grandTotal = 0
    minimumPriceTotal = 0
    obcTotal = 0

    for x in tepProductlist:


        totalPrice = x['total_price']
        grandTotal = grandTotal + totalPrice

        minimumPriceTotal = minimumPriceTotal + int(x["min_price"])*int(x['count'])

        # print(f"mintotoal = minimumprice({int(x['min_price'])}) * count({x['count']}) ")
        obcTotal = obcTotal+int(x["obc"])*int(count)
    # print(f'product name = {x["name"]} , obc = {x["obc"]},mrp = {x["price"]}')

    points = (grandTotal - obcTotal)/1000

    gst = (grandTotal/100)*18

    maxDiscountPrice = grandTotal - minimumPriceTotal

    maxDisPercentage = (maxDiscountPrice*100)/grandTotal


    # print(f'{grandTotal} - {obcTotal}')

    return render_template('points.html', products = tepProductlist, pid =getAllProductId(), grandTotal = grandTotal
                           ,gst=gst, finalTotal = grandTotal+gst, points = points,minTotal = minimumPriceTotal
                           ,mdp=maxDiscountPrice,mdPrecentage = maxDisPercentage)



@app.route('/discount',methods=['POST'])
def discount():
    global tepProductlist

    discount = request.form['discount']


    grandTotal = 0
    minimumPriceTotal = 0
    obcTotal = 0

    for x in tepProductlist:


        totalPrice = x['total_price']
        grandTotal = grandTotal + totalPrice

        minimumPriceTotal = minimumPriceTotal + int(x["min_price"]) * int(x["count"])
        obcTotal = obcTotal + int(x["obc"]) * int(x["count"])
        #
        # print(f'product name = {x["name"]} , obc = {x["obc"]},mrp = {x["price"]}')
        #
        # print(obcTotal)
        # print("end of for")
    discountTotal = grandTotal - int((grandTotal / 100) * int(discount))
    points = (discountTotal - obcTotal) / 1000

    gst = (discountTotal / 100) * 18

    maxDiscountPrice = grandTotal - minimumPriceTotal

    maxDisPercentage = (maxDiscountPrice * 100) / grandTotal
    if int(discount) <= int(maxDisPercentage):
        return render_template('points.html', products=tepProductlist, pid=getAllProductId(), grandTotal=grandTotal
                               , gst=gst, finalTotal=discountTotal + gst, points=points,discountTotal = discountTotal
                               ,discountValue = discount, minTotal = minimumPriceTotal,mdp=maxDiscountPrice,mdPrecentage = maxDisPercentage)
    else:
        pass

@app.route('/delete-product', methods=['POST'])
def delete_product():
    data = request.get_json()
    product_id = data['id']
    global tepProductlist

    for x in tepProductlist:
        if x['id'] == product_id:
            tepProductlist.remove(x)
            print(f'{x} is removed from list')

    return redirect("/points")







if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8182)

