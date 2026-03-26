from flask import Flask,render_template_string,request,redirect,session
import sqlite3
import random
import datetime

app=Flask(__name__)
app.secret_key="hotel"

def db():
    return sqlite3.connect("hotel.db")

# DATABASE
con=db()

con.execute("""

CREATE TABLE IF NOT EXISTS customers(

id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
phone TEXT,
address TEXT,
checkin TEXT,
checkout TEXT,
room TEXT,
price INTEGER,
days INTEGER,
roomno INTEGER,
restaurant INTEGER DEFAULT 0,
status TEXT DEFAULT 'active'

)

""")

con.commit()
con.close()

rooms={
"Standard Non AC":3500,
"Standard AC":4000,
"3 Bed Non AC":4500,
"3 Bed AC":5000
}

# LOGIN
@app.route('/',methods=['GET','POST'])
def login():

    if request.method=="POST":

        if request.form['user']=="admin" and request.form['pass']=="venkatesh@7":

            session['login']=True

            return redirect('/dashboard')

    return render_template_string("""

<style>

body{

background:linear-gradient(135deg,#667eea,#764ba2);
font-family:Segoe UI;
color:white;
text-align:center;
padding-top:150px;

}

.box{

background:rgba(255,255,255,0.1);
backdrop-filter:blur(20px);
width:400px;
margin:auto;
padding:40px;
border-radius:20px;

}

input{

width:100%;
padding:15px;
margin:12px 0;
border-radius:10px;
border:none;

}

button{

width:100%;
padding:15px;
background:#00ffd5;
border:none;
border-radius:10px;
font-weight:bold;
cursor:pointer;

}

</style>

<div class="box">

<h1>HOTEL OS</h1>

<form method="post">

<input name="user" placeholder="Username">

<input type="password"
name="pass"
placeholder="Password">

<button>Login</button>

</form>

</div>

""")

# DASHBOARD
@app.route('/dashboard')
def dashboard():

    if 'login' not in session:
        return redirect('/')

    con=db()

    total=con.execute(
"SELECT COUNT(*) FROM customers"
).fetchone()[0]

    active=con.execute(
"SELECT COUNT(*) FROM customers WHERE status='active'"
).fetchone()[0]

    revenue=con.execute(
"SELECT SUM(price*days)+SUM(restaurant) FROM customers"
).fetchone()[0]

    if revenue is None:
        revenue=0

    con.close()

    return render_template_string("""

<style>

body{
margin:0;
font-family:Segoe UI;
background:linear-gradient(135deg,#1f4037,#99f2c8);
}

.sidebar{

width:260px;
height:100vh;
background:linear-gradient(#141e30,#243b55);
position:fixed;
color:white;

}

.logo{

font-size:26px;
text-align:center;
padding:30px;

}

.sidebar a{

display:block;
padding:18px;
color:white;
text-decoration:none;

}

.sidebar a:hover{

background:#00ffd5;
color:black;

}

.main{

margin-left:260px;
padding:40px;

}

.cards{

display:grid;
grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
gap:30px;

}

.card{

background:white;
padding:40px;
border-radius:20px;
text-align:center;
box-shadow:0 10px 25px rgba(0,0,0,0.2);

}

.number{

font-size:45px;
color:#6a11cb;

}

</style>

<div class="sidebar">

<div class="logo">
HOTEL OS
</div>

<a href="/dashboard">Dashboard</a>
<a href="/booking">Booking</a>
<a href="/records">Records</a>
<a href="/active">Active Guests</a>
<a href="/customers">Total Customers</a>
<a href="/logout">Logout</a>

</div>

<div class="main">

<h1>Dashboard</h1>

<div class="cards">

<a href="/customers">

<div class="card">

<div class="number">
{{total}}
</div>

Total Customers

</div>

</a>

<a href="/active">

<div class="card">

<div class="number">
{{active}}
</div>

Active Guests

</div>

</a>

<div class="card">

<div class="number">

₹ {{revenue}}

</div>

Revenue

</div>

</div>

</div>

""",total=total,
active=active,
revenue=revenue)

# BOOKING UI
@app.route('/booking')
def booking():

    return render_template_string("""

<style>

body{

background:linear-gradient(135deg,#ff9a9e,#fad0c4);
font-family:Segoe UI;

}

.form{

width:500px;
margin:auto;
background:white;
padding:40px;
border-radius:20px;
margin-top:50px;

}

input,select{

width:100%;
padding:14px;
margin:10px;
border-radius:10px;
border:1px solid grey;

}

button{

padding:14px;
width:100%;
background:#ff758c;
border:none;
border-radius:10px;
color:white;
cursor:pointer;

}

.phone-group{

display:flex;
gap:10px;
margin:10px 0;

}

.country-code{

width:30%;
padding:14px;
border-radius:10px;
border:1px solid grey;

}

.phone-input{

width:70%;
padding:14px;
border-radius:10px;
border:1px solid grey;

}

.error-message{

color:red;
font-size:12px;
margin-top:5px;
display:none;

}

.success-message{

color:green;
font-size:12px;
margin-top:5px;
display:none;

}

</style>

<div class="form">

<h1>Room Booking</h1>

<form action="/book" method="post" id="bookingForm">

<input name="name" placeholder="Name" required>

<div class="phone-group">

<select name="country_code" id="countryCode" class="country-code">
<option value="+91">🇮🇳 India (+91)</option>
<option value="+1">🇺🇸 USA (+1)</option>
<option value="+44">🇬🇧 UK (+44)</option>
<option value="+61">🇦🇺 Australia (+61)</option>
<option value="+81">🇯🇵 Japan (+81)</option>
<option value="+86">🇨🇳 China (+86)</option>
<option value="+33">🇫🇷 France (+33)</option>
<option value="+49">🇩🇪 Germany (+49)</option>
<option value="+39">🇮🇹 Italy (+39)</option>
<option value="+34">🇪🇸 Spain (+34)</option>
<option value="+92">🇵🇰 Pakistan (+92)</option>
<option value="+880">🇧🇩 Bangladesh (+880)</option>
</select>

<input type="tel" name="phone" id="phoneInput" placeholder="Phone Number" class="phone-input" required>

</div>

<div class="error-message" id="phoneError"></div>
<div class="success-message" id="phoneSuccess"></div>

<input name="address" placeholder="Address" required>

<input type="date" name="checkin" required>

<input type="date" name="checkout" required>

<select name="room" required>

<option>Standard Non AC</option>
<option>Standard AC</option>
<option>3 Bed Non AC</option>
<option>3 Bed AC</option>

</select>

<button type="submit" id="bookBtn">Book Room</button>

</form>

<a href="/dashboard" style="text-decoration:none;">
<button style="padding:14px;width:100%;background:#ff758c;border:none;border-radius:10px;color:white;cursor:pointer;margin-top:10px;">Back</button>
</a>

</div>

<script>

const phoneInput = document.getElementById('phoneInput');
const countryCode = document.getElementById('countryCode');
const phoneError = document.getElementById('phoneError');
const phoneSuccess = document.getElementById('phoneSuccess');
const bookBtn = document.getElementById('bookBtn');
const bookingForm = document.getElementById('bookingForm');

// Phone digit requirements by country code
const phoneDigits = {
    '+91': 10,  // India
    '+1': 10,   // USA
    '+44': 10,  // UK
    '+61': 9,   // Australia
    '+81': 10,  // Japan
    '+86': 11,  // China
    '+33': 9,   // France
    '+49': 11,  // Germany
    '+39': 10,  // Italy
    '+34': 9,   // Spain
    '+92': 10,  // Pakistan
    '+880': 10  // Bangladesh
};

function validatePhone() {
    const phoneNum = phoneInput.value.trim();
    const code = countryCode.value;
    const requiredDigits = phoneDigits[code];
    
    // Only digits
    const digitsOnly = phoneNum.replace(/\D/g, '');
    
    phoneError.style.display = 'none';
    phoneSuccess.style.display = 'none';
    
    if (phoneNum === '') {
        phoneError.textContent = '';
        return true;
    }
    
    if (digitsOnly.length !== requiredDigits) {
        phoneError.textContent = `Invalid ${code} number. Please enter ${requiredDigits} digits.`;
        phoneError.style.display = 'block';
        return false;
    }
    
    phoneSuccess.textContent = '✓ Valid phone number';
    phoneSuccess.style.display = 'block';
    return true;
}

phoneInput.addEventListener('input', validatePhone);
countryCode.addEventListener('change', validatePhone);

bookingForm.addEventListener('submit', function(e) {
    if (!validatePhone()) {
        e.preventDefault();
        alert('Please enter a valid phone number');
    } else {
        // Store full phone number with country code
        const fullPhone = countryCode.value + phoneInput.value.replace(/\D/g, '');
        phoneInput.value = fullPhone;
    }
});

</script>

""")

# FOOD MENU
@app.route('/foodmenu/<id>')
def foodmenu(id):

    con=db()

    customer=con.execute(
"SELECT * FROM customers WHERE id=?",
(id,)
).fetchone()

    con.close()

    food_items = {
        "Idli": 80,
        "Dosa": 100,
        "Masala Dosa": 120,
        "Rava Dosa": 110,
        "Pesarattu": 110,
        "Upma": 90,
        "Pongal": 100,
        "Veg Meals": 150,
        "Non-Veg Meals": 180,
        "Chicken Curry": 200,
        "Mutton Curry": 220,
        "Fish Curry": 210,
        "Gongura Chicken": 210,
        "Gongura Mutton": 240,
        "Chicken Biryani": 250,
        "Mutton Biryani": 280,
        "Veg Biryani": 200,
        "Andhra Biryani": 280,
        "Sambar": 100,
        "Rasam": 80,
        "Gutti Vankaya Fry": 130,
        "Bendakaya Fry": 120,
        "Aloo Gobi": 110,
        "Mirchi Bajji": 80,
        "Punugulu": 70,
        "Garelu": 60,
        "Puri": 40,
        "Naan": 50,
        "Chapati/Roti": 30,
        "Tomato Rice": 120,
        "Curd Rice": 100,
        "Khichdi": 110,
        "Poha": 80,
        "Chikhalwali": 100,
        "Pachadi": 60,
        "Avial": 110,
        "Pizza": 200,
        "Pasta": 180,
        "Burger": 150,
        "Sandwich": 120,
        "French Fries": 100,
        "Ice Cream": 80,
        "Cake": 150,
        "Juice": 50,
        "Soft Drink": 40,
        "Tea": 30,
        "Coffee": 40,
        "Buttermilk": 40,
        "Lassi": 50
    }

    return render_template_string("""

<style>

body{

background:linear-gradient(135deg,#667eea,#764ba2);
font-family:Segoe UI;
margin:0;
padding:20px;

}

.food-container{

max-width:800px;
margin:auto;
background:white;
padding:40px;
border-radius:20px;

}

.food-title{

text-align:center;
color:#6a11cb;
margin-bottom:30px;

}

.food-grid{

display:grid;
grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
gap:15px;
margin-bottom:30px;

}

.food-item{

background:#f0f0f0;
padding:15px;
border-radius:10px;
border:2px solid #ddd;

}

.food-item input[type="checkbox"]{

cursor:pointer;
margin-right:10px;

}

.food-item label{

cursor:pointer;
font-weight:500;

}

.food-price{

color:#00ffd5;
font-weight:bold;
font-size:14px;
margin-left:20px;

}

.total-section{

background:#f9f9f9;
padding:20px;
border-radius:10px;
margin:20px 0;
border:2px solid #00ffd5;

}

.total-display{

font-size:24px;
color:#6a11cb;
font-weight:bold;
text-align:center;

}

.button-group{

display:flex;
gap:10px;
margin-top:20px;

}

button{

flex:1;
padding:15px;
border:none;
border-radius:10px;
font-weight:bold;
cursor:pointer;
font-size:16px;

}

.submit-btn{

background:#00ffd5;
color:black;

}

.submit-btn:hover{

background:#00e0c0;

}

.back-btn{

background:#ff758c;
color:white;

}

.back-btn:hover{

background:#ff5a7a;

}

</style>

<div class="food-container">

<h1 class="food-title">🍽️ Hotel Services - Food Menu</h1>

<div class="food-grid">

{% for item, price in food_items.items() %}

<div class="food-item">

<input type="checkbox" id="{{item}}" name="food_item" value="{{price}}" data-name="{{item}}" data-price="{{price}}">

<label for="{{item}}">{{item}}</label>

<span class="food-price">₹{{price}}</span>

</div>

{% endfor %}

</div>

<div class="total-section">

<div class="total-display">Total Bill: ₹<span id="totalAmount">0</span></div>

</div>

<div class="button-group">

<button type="button" class="submit-btn" onclick="submitOrder()">Add to Bill</button>

<a href="/records" style="flex:1;text-decoration:none;">

<button class="back-btn" style="width:100%;margin:0;">Back</button>

</a>

</div>

</div>

<script>

var foodItems = {{food_items_json | safe}};
var customerId = "{{customer_id}}";

function calculateTotal() {

    let total = 0;
    let items = document.querySelectorAll('input[name="food_item"]:checked');
    
    items.forEach(item => {
        total += parseInt(item.getAttribute('data-price'));
    });
    
    document.getElementById('totalAmount').textContent = total;

}

document.querySelectorAll('input[name="food_item"]').forEach(checkbox => {

    checkbox.addEventListener('change', calculateTotal);

});

function submitOrder() {

    let items = document.querySelectorAll('input[name="food_item"]:checked');
    let selectedItems = [];
    let total = 0;
    
    items.forEach(item => {
        selectedItems.push(item.getAttribute('data-name'));
        total += parseInt(item.getAttribute('data-price'));
    });
    
    if(total === 0) {
        alert('Please select at least one food item');
        return;
    }
    
    document.getElementById('foodList').value = selectedItems.join(', ');
    document.getElementById('foodTotal').value = total;
    document.getElementById('foodForm').submit();

}

</script>

<form id="foodForm" action="/addfood" method="post" style="display:none;">

<input type="hidden" name="id" value="{{customer_id}}">

<input type="hidden" id="foodList" name="food_list">

<input type="hidden" id="foodTotal" name="food_total">

</form>

""", 
food_items=food_items,
customer_id=id,
food_items_json=str(food_items).replace("'", '"')
)

# BOOK LOGIC
@app.route('/book',methods=['POST'])
def book():

    d=request.form

    ci=datetime.datetime.strptime(
d['checkin'],"%Y-%m-%d")

    co=datetime.datetime.strptime(
d['checkout'],"%Y-%m-%d")

    days=(co-ci).days

    price=rooms[d['room']]

    roomno=random.randint(100,999)

    con=db()

    con.execute("""

INSERT INTO customers

(name,phone,address,
checkin,checkout,
room,price,days,roomno)

VALUES(?,?,?,?,?,?,?,?,?)

""",(d['name'],d['phone'],
d['address'],
d['checkin'],
d['checkout'],
d['room'],
price,
days,
roomno))

    con.commit()
    con.close()

    return redirect('/records')

# RECORDS UI
@app.route('/records')
def records():

    con=db()

    data=con.execute(
"SELECT * FROM customers WHERE status='active'"
).fetchall()

    con.close()

    return render_template_string("""

<style>

body{
font-family:Segoe UI;
background:linear-gradient(135deg,#43cea2,#185a9d);
}

table{

width:90%;
margin:auto;
background:white;
border-radius:15px;

}

th{

background:#6a11cb;
color:white;
padding:15px;

}

td{

padding:15px;
text-align:center;

}

button{

padding:10px 20px;
border:none;
border-radius:8px;
background:#00c9ff;
color:white;
cursor:pointer;

}

.back-button-records{

padding:12px 30px;
background:#00ffd5;
border:none;
border-radius:10px;
font-weight:bold;
cursor:pointer;
font-size:16px;
color:black;

}

</style>

<h1 style="text-align:center">
Active Records
</h1>

<table>

<tr>

<th>Name</th>
<th>Room</th>
<th>Food</th>
<th>Add</th>
<th>Bill</th>
<th>Checkout</th>

</tr>

{% for i in data %}

<tr>

<td>{{i[1]}}</td>
<td>{{i[6]}}</td>
<td>₹ {{i[10]}}</td>

<td>

<a href="/foodmenu/{{i[0]}}">

<button style="padding:10px 20px;border:none;border-radius:8px;background:#00c9ff;color:white;cursor:pointer;">Add</button>

</a>

</td>

<td>

<a href="/bill/{{i[0]}}">
<button>Bill</button>
</a>

</td>

<td>

<a href="/delete/{{i[0]}}">
<button>Checkout</button>
</a>

</td>

</tr>

{% endfor %}

</table>

<div style="text-align:center;margin-top:30px;">
<a href="/dashboard">
<button style="padding:12px 30px;background:#00ffd5;border:none;border-radius:10px;font-weight:bold;cursor:pointer;font-size:16px;color:black;">Back to Dashboard</button>
</a>
</div>

""",data=data)

# ACTIVE GUEST UI
@app.route('/active')
def active():

    con=db()

    data=con.execute(
"SELECT * FROM customers WHERE status='active'"
).fetchall()

    con.close()

    return render_template_string("""

<style>

body{

background:linear-gradient(135deg,#30cfd0,#330867);
font-family:Segoe UI;

}

.card{

background:white;
width:300px;
padding:25px;
border-radius:15px;
margin:20px;
display:inline-block;

}

</style>

<h1 style="text-align:center;color:white">
Active Guests
</h1>

{% for i in data %}

<div class="card">

<h3>{{i[1]}}</h3>

<p>Room {{i[9]}}</p>

<p>{{i[6]}}</p>

</div>

{% endfor %}

<div style="text-align:center;margin-top:30px;">
<a href="/dashboard">
<button style="padding:12px 30px;background:#00ffd5;border:none;border-radius:10px;font-weight:bold;cursor:pointer;font-size:16px;color:white;">Back to Dashboard</button>
</a>
</div>

""",data=data)

# TOTAL CUSTOMERS UI
@app.route('/customers')
def customers():

    con=db()

    data=con.execute(
"SELECT * FROM customers"
).fetchall()

    con.close()

    return render_template_string("""

<style>

body{

background:linear-gradient(135deg,#f7971e,#ffd200);
font-family:Segoe UI;

}

table{

width:80%;
margin:auto;
background:white;
border-radius:15px;

}

th{

background:#ff512f;
color:white;
padding:15px;

}

td{

padding:15px;
text-align:center;

}

</style>

<h1 style="text-align:center">

Customer History

</h1>

<table>

<tr>

<th>Name</th>
<th>Room</th>
<th>Status</th>

</tr>

{% for i in data %}

<tr>

<td>{{i[1]}}</td>
<td>{{i[6]}}</td>
<td>{{i[11]}}</td>

</tr>

{% endfor %}

</table>

<div style="text-align:center;margin-top:30px;">
<a href="/dashboard">
<button style="padding:12px 30px;background:#ff512f;border:none;border-radius:10px;font-weight:bold;cursor:pointer;font-size:16px;color:white;">Back to Dashboard</button>
</a>
</div>

""",data=data)

# FOOD
@app.route('/addfood',methods=['POST'])
def addfood():

    id=request.form['id']

    price=int(request.form['food_total'])

    con=db()

    con.execute("""

UPDATE customers

SET restaurant=restaurant+?

WHERE id=?

""",(price,id))

    con.commit()
    con.close()

    return redirect('/records')

# BILL UI
@app.route('/bill/<id>')
def bill(id):

    con=db()

    d=con.execute(
"SELECT * FROM customers WHERE id=?",
(id,)
).fetchone()

    con.close()

    room=d[7]*d[8]

    food=d[10]

    gst=(room+food)*.18

    total=room+food+gst

    return render_template_string("""

<style>

body{

font-family:Segoe UI;
background:linear-gradient(135deg,#667eea,#764ba2);
color:white;
text-align:center;

}

.bill{

background:white;
color:black;
width:400px;
margin:auto;
padding:30px;
border-radius:20px;

}

</style>

<div class="bill">

<h1>Invoice</h1>

<p>{{d[1]}}</p>

<p>Room ₹ {{room}}</p>

<p>Food ₹ {{food}}</p>

<p>GST ₹ {{gst}}</p>

<h2>Total ₹ {{total}}</h2>

<button onclick="window.print()" style="cursor:pointer;">
Print
</button>

</div>

<div style="text-align:center;margin-top:20px;">
<a href="/records">
<button style="padding:12px 30px;background:#667eea;border:none;border-radius:10px;font-weight:bold;cursor:pointer;font-size:16px;color:white;">Back to Records</button>
</a>
</div>

""",d=d,
room=room,
food=food,
gst=gst,
total=total)

# CHECKOUT
@app.route('/delete/<id>')
def delete(id):

    con=db()

    con.execute("""

UPDATE customers

SET status='checkedout'

WHERE id=?

""",(id,))

    con.commit()
    con.close()

    return redirect('/records')

# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

if __name__=="__main__":

    app.run(debug=True)