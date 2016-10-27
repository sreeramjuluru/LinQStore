from flask import Flask,render_template,flash, request, url_for, redirect,session,jsonify
from dbconnect import connection
from wtforms import PasswordField,Form,BooleanField, TextField, validators, IntegerField, SelectField, DecimalField
from wtforms.fields.html5 import DateField
from datetime import datetime,date
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from utils import *
from sqlalchemy import Date, cast
import pygal 
import json
import redis 
import ujson,uuid
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:linq12345@localhost/linq'
db = SQLAlchemy(app)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
from pytz import timezone    
india_timezone = timezone("Asia/Calcutta")
#app.secret_key = "super secret key"



class AmazonItems(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  asin        = db.Column(db.String(120))
  category    = db.Column(db.String(120))
  clicks      = db.Column(db.Integer)
  conversion  = db.Column(db.Integer)
  dqty        = db.Column(db.Integer)
  date        = db.Column(db.DateTime)
  link_type   = db.Column(db.String(120))
  nqty        = db.Column(db.Integer)
  price       = db.Column(db.Float)
  qty         = db.Column(db.Integer)
  seller      = db.Column(db.String(120))
  tag         = db.Column(db.String(120))
  title       = db.Column(db.String(120))

  def __init__(self,asin, category,clicks,conversion,dqty,date,link_type,nqty,price,qty,seller, tag , title ):
     self.asin              = asin
     self.category = category
     self.clicks = clicks
     self.conversion = conversion
     self.dqty = dqty
     self.date = date
     self.link_type = link_type
     self.nqty = nqty
     self.price =  price
     self.qty = qty
     self.seller =  seller
     self.tag  =  tag
     self.title =  title

  def __repr__(self):
                return '%s' % self.asin



class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),unique=True)
    state = db.Column(db.String(120))
    stores = db.relationship('Store', backref='store',
		                        lazy='dynamic')
    def __repr__(self):
		return '%s' % self.name


class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),unique=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    address = db.Column(db.Text)
    pincode = db.Column(db.Integer)
    users = db.relationship('User', backref='user',
                    lazy='dynamic')
    def __repr__(self):
            return '%s' % (self.name)

class OrderStatus(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     status = db.Column(db.String(120), unique=True)

     def __init__(self,status):
        self.status = status

     def __repr__(self):
          return '<OrderStatus %r>' % self.status

class ReturnStatus(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     status = db.Column(db.String(120), unique=True)

     def __init__(self,status):
        self.status = status

     def __repr__(self):
          return '<ReturnStatus %r>' % self.status



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(120))
    mobile_num = db.Column(db.String(13), unique=True)
    password = db.Column(db.String(150))
    is_active = db.Column(db.Boolean)
    affliate_id = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))


    def __init__(self, email, name, mobile_num, password, store_id, affliate_id):
        self.email = email
        self.name = name
        self.mobile_num = mobile_num
        self.password = password
        self.store_id = store_id
        self.is_active = True
        self.affliate_id = affliate_id
        self.is_admin = False

        def __repr__(self):
                return '<User %r>' % self.email



class Customer(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     email = db.Column(db.String(120))
     mobile_num = db.Column(db.String(13), unique=True, nullable=False)
     name = db.Column(db.String(120), nullable=False)
     marketing_source = db.Column(db.String(120), nullable=False)
     date_of_birth = db.Column(db.DateTime , nullable=False)
     gender = db.Column(db.String(13), nullable=False)
     store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
     is_new_customer_for_amazon = db.Column(db.Boolean, default=False)
     alternate_mobile_number = db.Column(db.String(13))
     created_at = db.Column(db.DateTime, default=datetime.now(india_timezone).strftime("%Y-%m-%d %H:%M:%S")) 

     @property
     def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
           'mobile_number': self.mobile_num,
           # This is an example how to deal with Many2Many relations
           'name'  : self.name
       }


     def __init__(self,email,mobile_num,name,marketing_source,date_of_birth, gender,store_id, alternate_mobile_number,is_new_customer_for_amazon=False):
         self.email = email
         self.mobile_num = mobile_num
         self.name = name
         self.marketing_source = marketing_source
         self.date_of_birth = date_of_birth
         self.gender = gender
         self.store_id = store_id
         self.is_new_customer_for_amazon = is_new_customer_for_amazon
         self.alternate_mobile_number = alternate_mobile_number
     def __repr__(self):
          return  '<Orderitem %r %r>' % (self.mobile_num ,  self.name)

class Customers(db.Model):
     id = db.Column(GUID, primary_key=True)
     email = db.Column(db.String(120))
     mobile_num = db.Column(db.String(13), unique=True, nullable=False)
     name = db.Column(db.String(120), nullable=False)
     marketing_source = db.Column(db.String(120), nullable=False)
     date_of_birth = db.Column(db.DateTime , nullable=False)
     gender = db.Column(db.String(13), nullable=False)
     store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
     is_new_customer_for_amazon = db.Column(db.Boolean, default=False)
     alternate_mobile_number = db.Column(db.String(13))
     created_at = db.Column(db.DateTime, default=datetime.now(india_timezone).strftime("%Y-%m-%d %H:%M:%S"))

     @property
     def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
           'mobile_number': self.mobile_num,
           # This is an example how to deal with Many2Many relations
           'name'  : self.name
       }


     def __init__(self,email,mobile_num,name,marketing_source,date_of_birth, gender,store_id, alternate_mobile_number,is_new_customer_for_amazon=False):
         self.id = uuid.uuid4()
         self.email = email
         self.mobile_num = mobile_num
         self.name = name
         self.marketing_source = marketing_source
         self.date_of_birth = date_of_birth
         self.gender = gender
         self.store_id = store_id
         self.is_new_customer_for_amazon = is_new_customer_for_amazon
         self.alternate_mobile_number = alternate_mobile_number
     def __repr__(self):
          return  '<Orderitem %r %r>' % (self.mobile_num ,  self.name)



class OrderItems(db.Model):
     linq_order_num = db.Column(GUID, primary_key=True)
     order_status_id = db.Column(db.Integer, db.ForeignKey('order_status.id'))
     order_id = db.Column(db.String(100))
     item_name = db.Column(db.String(120))
     item_cost = db.Column(db.Float)
     custmer_id = db.Column(GUID, db.ForeignKey('customers.id'))
     order_date_time = db.Column(db.DateTime)
     order_category = db.Column(db.String(120))
     ordered_by = db.Column(db.Integer, db.ForeignKey('user.id'))
     linq_shipping_cost = db.Column(db.Float)
     website_shipping_cost = db.Column(db.Float)
     total_cost = db.Column(db.Float)
     advance_amount = db.Column(db.Float)
     website = db.Column(db.String(120))
     other = db.Column(db.String(120))
     rvn = db.Column(db.Integer)
     received_date = db.Column(db.DateTime)
     delivered_date = db.Column(db.DateTime)
     store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
     asin = db.Column(db.String(15))

     def __init__(self,order_id,item_name,item_cost,customer_id,order_category, linq_shipping_cost,website_shipping_cost,advance_amount,website,asin,other):
        self.linq_order_num = uuid.uuid4()
        self.order_date_time = datetime.now(india_timezone).strftime("%Y-%m-%d %H:%M:%S")
        self.order_id = order_id
        self.item_name = item_name
        self.item_cost = item_cost
        self.custmer_id = customer_id
        self.order_category = order_category
        self.linq_shipping_cost = linq_shipping_cost
        self.website_shipping_cost = website_shipping_cost
        self.advance_amount = advance_amount
        self.website = website
        self.other = other
        self.asin = asin
        self.store_id = session['store_id']
        self.ordered_by = session['user_id']

        self.total_cost = float(item_cost) + float(linq_shipping_cost) + float(website_shipping_cost)
        self.order_status_id = 1

     def __repr__(self):
          return '%r' % self.item_name



class ReturnReason(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     reason = db.Column(db.String(120), unique=True)

     def __init__(self,status):
        self.reason = reason

     def __repr__(self):
          return '<ReturnReason %r>' % self.reason


class ReturnItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    linq_order_num = db.Column(db.Integer, db.ForeignKey('orderitem.linq_order_num'),index=True)
    return_status_id = db.Column(db.Integer, db.ForeignKey('return_status.id'),index=True)
    amount_returnable = db.Column(db.Float)
    courier_tracking_num = db.Column(db.String(120),index=True)
    is_return_shippingcharge_refunded =  db.Column(db.Boolean)
    created_date =  db.Column(db.DateTime,index=True ,default=datetime.now(india_timezone))
    return_reason_id = db.Column(db.Integer, db.ForeignKey('return_reason.id'))  
    def __init__(self,linq_order_num,return_reason_id, returnable_amount=0, return_reason=''):
          self.linq_order_num = linq_order_num
          self.return_reason_id = return_reason_id
          self.amount_returnable = returnable_amount
          self.return_reason = return_reason
          self.return_status_id = 1
    def __repr__(self):
          return '<ReturnItem %r>' % self.id


class ReturnItems(db.Model):
    id = db.Column(GUID, primary_key=True)
    linq_order_num = db.Column(GUID, db.ForeignKey('order_item.linq_order_num'),index=True)
    return_status_id = db.Column(db.Integer, db.ForeignKey('return_status.id'),index=True)
    amount_returnable = db.Column(db.Float)
    courier_tracking_num = db.Column(db.String(120),index=True)
    is_return_shippingcharge_refunded =  db.Column(db.Boolean)
    created_date =  db.Column(db.DateTime,index=True ,default=datetime.now(india_timezone))
    return_reason_id = db.Column(db.Integer, db.ForeignKey('return_reason.id'))
    def __init__(self,linq_order_num,return_reason_id, returnable_amount=0, return_reason=''):
          self.id = uuid.uuid4()
          self.linq_order_num = linq_order_num
          self.return_reason_id = return_reason_id
          self.amount_returnable = returnable_amount
          self.return_reason = return_reason
          self.return_status_id = 1
    def __repr__(self):
          return '<ReturnItem %r>' % self.id


class AddOrderForm(Form):
    order_id  = TextField('Website Order Id', [validators.length(min=4, max=120)])
    item_name = TextField('Item Name', [validators.length(min=4, max=120)])
    item_cost = DecimalField('Item Cost' , [validators.Required()])
    custmer_id = SelectField('Customer',coerce=int)
    order_category = SelectField('Order Category',coerce=int,choices=[(1,'Mobiles'), (2,'Clothing'), (3,'Laptops/Desktops'),(4,'Mobile/Computer Accessories'),(5,'Large Home Appliances'), (6,'Sports/health'),(7,'Books'),(8,'Others')]) 
    linq_shipping_cost =  DecimalField('Linq Shipping Cost' , [validators.Required()])
    website_shipping_cost = DecimalField('Website Shipping Cost' , [validators.Required()])
    advance_amount = DecimalField('Advance Amount' , [validators.Required()])
    website = SelectField('Website', coerce=int,choices=[(1,'Amazon'), (2,'Flipkart')] )
    other = TextField('Any Other Information')
    def __init__(self, *args, **kwargs):
        super(AddOrderForm, self).__init__(*args, **kwargs)
        self.custmer_id.choices = convert_list_wtforms_choices(Customer.query.filter_by(store_id=session['store_id']).order_by(Customer.created_at.desc()).all())


class SendSMSForm(Form):
      message = TextField('Message to be sent', [validators.length(min=4, max=240)])
class SendSMSFormSingle(Form):
      message = TextField('Message to be sent', [validators.length(min=4, max=240)])
      mobile_number = TextField('Mobile Number', [validators.Required()])


class RegistrationForm(Form):
    email = TextField('Email Address', [validators.length(min=4, max=120)])
    name = TextField('Name', [validators.length(min=4, max=120)])
    password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm',message="Passwords must Match!!")])
    confirm = PasswordField('Repeat Password')
    mobile_num = TextField('Telephone', [validators.Required()])
    affliate_id = TextField('Affliate Id', [validators.length(min=5, max=120)])
    stores = Store.query.all()
    store = SelectField('Store',coerce=int,choices= convert_list_wtforms_choices(stores))
    accept_tos = BooleanField('I accept the <a href="/tos/">Terms of Service and <a href="/Privacy/">The Privacy Notice', [validators.Required()])
    def __init__(self, *args, **kwargs):
        super(RegistrationForm,self).__init__(*args, **kwargs)
        self.store.choices = convert_list_wtforms_choices(Store.query.all())


class CustomerForm(Form):
    email = TextField('Email Address')
    name = TextField('Name', [validators.length(min=4, max=120)])
    mobile_num = TextField('Mobile Number', [validators.Required()])
    alternate_mobile_number = TextField('Alternate Mobile Number', [validators.Required()])
    marketing_source = SelectField('Marketing Source' ,coerce=int, choices = [(1,'Word of Mouth'),(2, 'Tv Ad'),(3, 'Flyer Marketing'),(4,'Other')])
    date_of_birth = DateField('Date Of Birth', [validators.Required()])
    gender = SelectField('Gender' ,coerce=int, choices =[(1,'Male'),(2,'Female')])
    is_new_customer_for_amazon = BooleanField('New Customer for Amazon', [validators.Required()])


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("You need to login to avail Jarvis Services")
            return redirect(url_for('login'))
    return wrap

@app.route("/add-customer/", methods = ["GET","POST"])
@login_required
def add_customer():
    try:
        print request
        form = CustomerForm(request.form)
        print form
        print request.method
        print form.email
        print form.email.data
        print form.name.data
        print form.date_of_birth.data
        print form.gender.data
        if request.method == "POST" and form.validate():
            print "posty"
            print form.marketing_source.data
            print form.gender.data
            email = form.email.data
            name = form.name.data
            mobile_num = form.mobile_num.data
            marketing_source = form.marketing_source.data
            date_of_birth = form.date_of_birth.data
            gender = form.gender.data
            store_id = session['store_id']
            is_already_there  = Customer.query.filter_by(mobile_num=mobile_num).first()
            print "is already"
            print is_already_there
            if is_already_there is not None:
		return "Customer with the given phone number already Exists"
            is_new_customer_for_amazon = form.is_new_customer_for_amazon.data
            alternate_mobile_number = form.alternate_mobile_number.data
            customer = Customer(email,mobile_num,name,marketing_source,date_of_birth,gender,store_id,alternate_mobile_number,is_new_customer_for_amazon)
            db.session.add(customer)
            db.session.commit()
            flash("Customer Added successfully")
            return redirect(url_for('dashboard'))
        return render_template('add-customer1.html', form=form)
    except Exception as e:
        return str(e)

@app.route("/add-customer1/", methods = ["POST"])
@login_required
def add_customer1():
    print "pallepu"
    try:
            print "posty"
            print request.json
            email = request.json["email"]
            name = request.json["name"].title()
            mobile_num = request.json["mobile_number"]
            date_of_birth = request.json["date_of_birth"]
            gender = request.json["gender"]
            store_id = session['store_id']
            is_already_there  = Customers.query.filter_by(mobile_num=mobile_num).first()
            print "is already"
            print is_already_there
            if is_already_there is not None:
                return json.dumps({'msg':'Customer with the given phone number already exists'}), 500, {'ContentType':'application/json'}
            is_new_customer_for_amazon = request.json["is_new_customer_for_amazon"]
            alternate_mobile_number = request.json["alternate_mobile_number"]
            print alternate_mobile_number
            print date_of_birth
            customer = Customers(email,mobile_num,name,"Word Of Mouth",date_of_birth,gender,store_id,alternate_mobile_number,is_new_customer_for_amazon)
            print "customer"
            db.session.add(customer)
            db.session.commit()
            print "after commit"
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'msg':str(e)}), 500, {'ContentType':'application/json'}


@app.route("/add-order/", methods = ["GET","POST"])
@login_required
def add_order():
    try:
            order_id = request.json["order_id"]
            item_name = request.json["item_name"]
            item_cost = request.json["item_cost"]
            order_category = request.json["order_category"]
            custmer_id = request.json["customer"]
            linq_shipping_cost = request.json["linq_shipping_cost"]
            website_shipping_cost = request.json["website_shipping_cost"]
            asin = request.json["asin"]
            total_cost = float(item_cost) + float(linq_shipping_cost) + float(website_shipping_cost )
            advance_amount = request.json["advance_amount"]
            other = ""
            website = "Amazon"
            store_id = session['store_id']
            order_item = OrderItems(order_id,item_name,item_cost,custmer_id,order_category, linq_shipping_cost,website_shipping_cost,advance_amount,website,asin,other) 
            db.session.add(order_item)
            db.session.commit()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except Exception as e:
            return json.dumps({'msg':str(e)}), 500, {'ContentType':'application/json'}


@app.route("/add-order1/", methods = ["POST"])
@login_required
def add_order1():
    try:
        print request
        print "after request"
        print request.form
        form = AddOrderForm(request.form)
        print "before cust id"
        print form.custmer_id.data
        if request.method == "POST" and form.validate():
            print 'postyy'
            order_id = form.order_id.data
            item_name = form.item_name.data
            item_cost = form.item_cost.data
            order_category = form.order_category.data
            custmer_id = form.custmer_id.data
            linq_shipping_cost = form.linq_shipping_cost.data
            website_shipping_cost = form.website_shipping_cost.data
            total_cost = item_cost + linq_shipping_cost + website_shipping_cost
            advance_amount = form.advance_amount.data
            other = form.other.data
            website = form.website.data
            print 'here'
            print custmer_id
            print session['user_id']
            store_id = session['store_id']
            order_item = OrderItem(order_id,item_name,item_cost,custmer_id,order_category, linq_shipping_cost,website_shipping_cost,advance_amount,website,other)
            db.session.add(order_item)
            db.session.commit()
            print 'after commit'
            flash("Order Added successfully")
            return redirect(url_for('dashboard'))
        return render_template('add-order.html', form=form)
    except Exception as e:
        return str(e)


@app.route("/get-customers/", methods = ["GET"])
@login_required
def get_customers():
    try:
	customers = Customers.query.filter_by(store_id=session['store_id']).order_by(Customers.created_at.desc()).all()
        return jsonify(json_list=[i.serialize for i in customers])
    except Exception,e:
        return json.dumps({'msg':str(e)}), 500, {'ContentType':'application/json'}	


@app.route("/add-return/", methods = ["GET","POST"])
@login_required
def add_return():
        if request.method == "POST":
           print "post"
           order= OrderItem.query.filter_by(linq_order_num = request.json['linq_order_num']).first()
           print order
           order.order_status_id = 4
           returnable_amount = 0
           if order.order_status_id == 2 or order.order_status_id == 1:
               returnable_amount = order.advance_amount
           else:
              returnable_amount = order.item_cost + order.website_shipping_cost
           return_reason = request.json['return_reason']
           print return_reason
           return_item = ReturnItems(request.json['linq_order_num'],1, returnable_amount, return_reason)
           db.session.add(return_item)
           db.session.commit()
           print "sucessfully commited"
           return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
 
        orders  = OrderItem.query.join(Customer, OrderItem.custmer_id == Customer.id).add_columns(OrderItem.order_date_time,OrderItem.order_id, OrderItem.item_name, OrderItem.item_cost, OrderItem.website_shipping_cost, OrderItem.order_status_id , Customer.mobile_num, Customer.name, OrderItem.linq_shipping_cost, OrderItem.advance_amount,OrderItem.linq_order_num).filter(OrderItem.store_id == session['store_id'])
        return render_template('add-return.html',orders=orders)



@app.route("/returns-all/", methods = ["GET"])
@login_required
def all_return():
   return "Coming Soon!!"
   print 'zingdi'
   returns  = ReturnItems.query.join(OrderItem ).join(Customer).add_columns(OrderItem.order_date_time,OrderItem.order_id, OrderItem.item_name, OrderItem.item_cost, OrderItem.website_shipping_cost, OrderItem.order_status_id , Customer.mobile_num, Customer.name, OrderItem.linq_shipping_cost, OrderItem.advance_amount,OrderItem.linq_order_num, ReturnItems.id, ReturnItems.return_status_id).filter(OrderItem.store_id == session['store_id'])
   print '---------'
   print returns
   print '----------'
   return render_template('returns-ab.html', returns=returns)


@app.route("/")
@login_required
def hello():
    c,conn = connection()
    today = datetime.now(india_timezone).strftime("%Y-%m-%d")
    data = c.execute('select sum(total_cost),count(*) from order_items where date_format(order_date_time,"%Y-%m-%d") = "{}" and store_id = {}'.format(str(today),session['store_id']))
    data = c.fetchall()
    print data[0][1]
    year = date.today().year
    month = date.today().month
    print year
    print month
    monthly_data = c.execute('select sum(total_cost),count(*) from order_items where date_format(order_date_time,"%Y-%m") = "{}" and store_id = {}'.format(str(date.today().year) + "-" + str(date.today().month), session['store_id']))
    monthly_data = c.fetchall()
    print monthly_data
    daily_cost = daily_orders = monthly_orders = monthly_cost = 0
    if data[0][1] > 0:
       daily_cost =  round(data[0][0],2)
       daily_orders =  data[0][1]
    if monthly_data[0][1] > 0:
       monthly_cost = round(monthly_data[0][0],2)
       monthly_orders = monthly_data[0][1]
    print session 
    return render_template("header2.html", current_user_name=session['username'], total_orders_today = daily_orders , total_sales_today = daily_cost, total_orders_month =monthly_orders, total_sales_month = monthly_cost )
    #return "Its only a matter of time before LinQ makes it big"

@app.route("/dashboard/")
def dashboard():
    print "tehmpydash:"
    return render_template("dashboard.html")

@app.errorhandler(404)
def page_not_found(e):
        return ("The page doesn't exist !!")

@app.route("/pap/")
def hello1():
    return render_template("header2.html")
    try:
        print request
        form = CustomerForm(request.form)
        print form
        print request.method
        print form.email
        print form.email.data
        print form.name.data
        print form.date_of_birth.data
        print form.gender.data
        if request.method == "POST" and form.validate():
            print "posty"
            print form.marketing_source.data
            print form.gender.data
            email = form.email.data
            name = form.name.data
            mobile_num = form.mobile_num.data
            marketing_source = form.marketing_source.data
            date_of_birth = form.date_of_birth.data
            gender = form.gender.data
            store_id = session['store_id']
            is_already_there  = Customer.query.filter_by(mobile_num=mobile_num).first()
            print "is already"
            print is_already_there
            if is_already_there is not None:
                return "Customer with the given phone number already Exists"
            is_new_customer_for_amazon = form.is_new_customer_for_amazon.data
            alternate_mobile_number = form.alternate_mobile_number.data
            customer = Customer(email,mobile_num,name,marketing_source,date_of_birth,gender,store_id,alternate_mobile_number,is_new_customer_for_amazon)
            db.session.add(customer)
            db.session.commit()
            flash("Customer Added successfully")
            return redirect(url_for('dashboard'))
        return render_template('sample.html', form=form)
    except Exception as e:
        return str(e)

    returns  = ReturnItem.query.join(Orderitem ).join(Customer).add_columns(Orderitem.order_date_time,Orderitem.order_id, Orderitem.item_name, Orderitem.item_cost, Orderitem.website_shipping_cost, Orderitem.order_status_id , Customer.mobile_num, Customer.name, Orderitem.linq_shipping_cost, Orderitem.advance_amount,Orderitem.linq_order_num, ReturnItem.id, ReturnItem.return_status_id).all()

    return render_template("sample.html", returns=returns)
    #return "Its only a matter of time before LinQ makes it big"


@app.route("/logout/")
@login_required
def logout():
   session.clear()
   flash("You have been logged out!!")
   gc.collect()
   return redirect(url_for('hello'))

@app.route("/customers/")
@login_required
def customers():
   users= Customers.query.filter_by(store_id = session['store_id']).all()
   return render_template('customers.html', users=users, current_user_name = session['username'])
   return User.query.filter_by(store_id = session['store_id']).all()

@app.route("/orders/")
@login_required
def orders_all():
   orders  = OrderItems.query.join(Customers, OrderItems.custmer_id == Customers.id).add_columns(OrderItems.order_date_time,OrderItems.order_id, OrderItems.item_name, OrderItems.item_cost, OrderItems.website_shipping_cost, OrderItems.order_status_id , Customers.mobile_num, Customers.name, OrderItems.linq_shipping_cost, OrderItems.advance_amount,OrderItems.linq_order_num).filter(OrderItems.store_id == session['store_id']).all()
   return render_template('orders.html', orders=orders,current_user_name=session["username"])

@app.route("/orders-tracked/")
@login_required
def orders_all_tracked():
   tracked_items = AmazonItems.query.filter_by(tag = session['affliate_id']).all()
   return render_template('tracked-orders.html', items =tracked_items, current_user_name=session['username'])


@app.route("/payments/")
@login_required
def payments():
   c,conn = connection()
   store = session['store_id']
   print store 
   data = c.execute('select date_format(order_date_time,"%Y-%m-%d") date  ,sum(total_cost) total , sum(advance_amount) advance_amount, IFNULL( (select sum(total_cost-advance_amount) from order_items a where date_format(a.delivered_date,"%Y-%m-%d") = date_format(d.order_date_time,"%Y-%m-%d") and store_id = {}),0) delivery_amount from order_items d where store_id = {} group by date_format(order_date_time,"%Y-%m-%d"),delivery_amount'.format(store,store))
   data = c.fetchall()
   print data  
   return render_template('payments.html', items = data,current_user_name=session["username"])

@app.route("/advance-amounts/<day>")
@login_required
def advance_amounts(day):
   print day 
   orders  = OrderItem.query.join(Customer, OrderItem.custmer_id == Customer.id).add_columns(OrderItem.order_date_time,OrderItem.order_id, OrderItem.item_name, OrderItem.item_cost, OrderItem.website_shipping_cost, OrderItem.order_status_id , Customer.mobile_num, Customer.name, OrderItem.linq_shipping_cost, OrderItem.advance_amount,OrderItem.linq_order_num).filter(OrderItem.store_id == session['store_id']).filter(func(OrderItem.order_date_time) == day)
   return render_template('payments.html', items = orders)


@app.route("/receive-order/", methods = ["POST"])
@login_required
def orders_receive():
   print request
   print request.json
   order= OrderItems.query.filter_by(linq_order_num = request.json['linq_order_num']).first()
   order.order_status_id = 2
   order.received_date = datetime.now(india_timezone).strftime("%Y-%m-%d %H:%M:%S") 
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/deliver-order/", methods = ["POST"])
@login_required
def orders_deliver():
   print request
   print request.json
   order= OrderItems.query.filter_by(linq_order_num = request.json['linq_order_num']).first()
   order.order_status_id = 3
   order.delivered_date = datetime.now(india_timezone).strftime("%Y-%m-%d %H:%M:%S")
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
   


@app.route("/dispatch-return/", methods = ["POST"])
@login_required
def return_dispatch():
   print "return_dispatch"
   print request
   print request.json
   returnitem = ReturnItems.query.filter_by(id = request.json['return_id']).first()
   returnitem.return_status_id = 2
   returnitem.courier_tracking_num = request.json['courier_details']
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/return-destination/", methods = ["POST"])
@login_required
def return_destination():
   print "return_dispatch"
   print request
   print request.json
   returnitem = ReturnItems.query.filter_by(id = request.json['return_id']).first()
   returnitem.return_status_id = 3
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route("/refund-received/", methods = ["POST"])
@login_required
def refund_received():
   print "return_dispatch"
   print request
   print request.json
   returnitem = ReturnItems.query.filter_by(id = request.json['return_id']).first()
   returnitem.return_status_id = 4
   db.session.commit()
   return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


@app.route("/display-orders/", methods = ["GET"])
@login_required
def display_order():
    return render_template('orders-display.html')



@app.route("/returns/", methods = ["GET"])
@login_required
def display_returns():
    return render_template('returns.html')


@app.route("/login/", methods = ["GET","POST"])
def login():
    if 'logged_in' in session:
        return redirect(url_for('hello'))
    error = ''
    try:
       c,conn = connection()
       if request.method == "POST":
             print request
             print "jkdjfdkj"
             print request.form['username']
             print request.form['password']
             data = c.execute("SELECT * from user where email  = (%s)" ,[thwart(request.form['username'])])
             print "db call "
             print data
             data = c.fetchone()
             print data
             if data and sha256_crypt.verify(request.form['password'], data[4]):
                    print 'matchy'
                    session['logged_in'] = True
                    session['username'] = data[2]
                    session['store_id'] = data[8]
                    session['user_id'] = data[0]
                    session['affliate_id'] = data[6]
                    print "zumbel"
                    flash("You are now logged in !!"+ str(request.form['username']))
                    return redirect(url_for("hello"))
             else:
                print "Invalid"
                error = "Invalid Credentials. Try Again."
                flash(error)
       return render_template("login.html", error=error)

    except Exception as e:
         flash(e)
         return render_template("login.html", error = e)


@app.route("/register/", methods = ["GET","POST"])
def register():
    try:
       form = RegistrationForm(request.form)
       print form
       print form.store
       if request.method == "POST" and form.validate():
           email = form.email.data
           name = form.name.data
           mobile_num = form.mobile_num.data
           affliate_id = form.affliate_id.data
           print 'storeeeees'
           print form.store.data
           print 'kayees'
           store_id = form.store.data
           password = sha256_crypt.encrypt(str(form.password.data))
           c,conn = connection()
           #x = c.execute("SELECT * from users where user_name= (%s)",[thwart(username)])
           x = User.query.filter_by(email=thwart(email)).first()
           print x
           if x is not None:
                 flash("The username already exists! Please choose another")
                 render_template('register.html', form=form)
           else:
               #c.execute("INSERT into users (user_name,password,email) VALUES  (%s,%s,%s)",[thwart(username),thwart(password),thwart(email)])
               #conn.commit()
               #flash("Thanks For Registering!!")
               #c.close()
               #conn.close()
               #gc.collect()
               admin = User(email,name,mobile_num, password,store_id,affliate_id)
               db.session.add(admin)
               db.session.commit()
               #session['logged_in'] = True
               #session['name'] = name
               #session['store_id'] = store_id
               #session['user_id']=User.query.filter_by(mobile_num=mobile_num).first().id 
               return "Successfully created"
       return render_template('register.html', form=form)
    except Exception as e:
       return str(e)

@app.route('/send-sms/', methods = ["GET","POST"])
@login_required
def send_sms():
        try:
           form = SendSMSForm(request.form)
           if request.method == "POST":
              c,conn = connection()
              print "hello"
              data = form.message.data 
              print data
              redis_client.sadd('sms-queue',  data)
              return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

           return render_template('send-sms.html', form=form)

	    

        except Exception,e :
               return(str(e))

              
@app.route('/send-sms-single/', methods = ["GET","POST"])
@login_required
def send_sms_single():
        try:
           form = SendSMSFormSingle(request.form)
           if request.method == "POST":
              c,conn = connection()
              print "hello ckwhjqwbh"
              data = request.json['message']
              mobile_number = request.json['mobile_number']
              print data
              redis_client.sadd('sms-queue-single', ujson.dumps({'data': data, 'mobile_number': mobile_number }))
              print "sfksjb"
              return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

           return render_template('send-sms-single.html', form=form)


        except Exception,e :
               return(str(e))
             

@app.route('/sales/')
def pygal2():
        try:    
		towns = [u'linqecil-21', u'linqguntur-21', u'linqjaggayyapeta-21', u'linqkhammam-21', u'linqkodad-21', u'linqkodada-21', u'linqkothagudem-21', u'linqmedak-21', u'linqmedchal-21', u'linqnandigama-21', u'linqnarasaraopet-21', u'linqnuzividu-21', u'linqsattupally-21', u'linqsecunderabad-21', u'linqsiddipet-21', u'linqsircilla-21', u'linqtiruvuru-21', u'linqvijayawada-21', u'linqvissannapeta-21']
                graph = pygal.Line()
                query = 'select round(sum(price*qty),2) , date_format(date,"%Y-%m-%d") ,tag from amazon_items group by date_format(date,"%Y-%m-%d") ,tag;'
                c,conn = connection()
                data = c.execute(query)
                data = c.fetchall()
                print data
                dates = range(1,32)
                graph.title = 'Total Sales on a daily basis'
                graph.x_labels = dates
                labels_for_y = []
                data_map = {}
                for town in towns:
                      data_map[town]=  [None] * 32
                for order_row in data:
			data_map[order_row[2]][int(order_row[1][8:10])] = order_row[0]
                for d in data_map.keys():
                       graph.add(d, data_map[d])
                graph_data = graph.render_data_uri()
                return render_template("graphing.html", graph_data = graph_data)
        except Exception, e:
                return(str(e))


@app.route('/total-sales/')
def pygal3():
        try:
                graph = pygal.Line()
                query = 'select round(sum(price*qty),2) , date_format(date,"%Y-%m-%d") from amazon_items group by date_format(date,"%Y-%m-%d") '
                c,conn = connection()
                data = c.execute(query)
                data = c.fetchall()
                print data
                dates = range(1,32)
                graph.title = 'Total Sales on a daily basis'
                graph.x_labels = dates
                labels_for_y = []
                data_map = {}
                data_map["Sales"]=  [None] * 32
                for order_row in data:
                        data_map["Sales"][int(order_row[1][8:10])] = order_row[0]
                graph.add("Total Sales", data_map["Sales"])
                graph_data = graph.render_data_uri()
                return render_template("graphing.html", graph_data = graph_data)
        except Exception, e:
                return(str(e))


if __name__ == "__main__":
    app.run(host='0.0.0.0')

