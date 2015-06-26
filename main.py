#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi 
import re
import os
import jinja2
import string
import hashlib
import random
import datetime
import json
import logging
import math
import random
from google.appengine.api import memcache
from google.appengine.ext import db 

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = False)

"""========================================================DATABSES================"""

class UserBase(db.Model):
	"""User database contains username, hashed password and salt"""
	username = db.StringProperty(required = True)
	saltedPass = db.StringProperty(required = True)

class OwnerBase(db.Model):
	username = db.StringProperty(required = True)

class UserFavStore(db.Model):
	username = db.StringProperty(required = True)
	favStore = db.TextProperty(required = False)

class UserFavProd(db.Model):
	username = db.StringProperty(required = True)
	favProd = db.TextProperty(required = False)

class StoreBase(db.Model):
	''' StoreBase contains all store information '''
	storeName = db.StringProperty(required = True)
	storeLogo = db.StringProperty(required = True)
	storeLocation = db.StringProperty(required = True)
	storeOwner = db.StringProperty(required = True)
	storeDesc = db.StringProperty(required = True)

class ProductBase(db.Model):
	productName = db.StringProperty(required = True)
	productPrice = db.FloatProperty(required = True)
	productImage = db.StringProperty(required = True)
	productDesc = db.TextProperty(required = True)

class ProductStore(db.Model):
	productName = db.StringProperty(required = True)
	productStore = db.StringProperty(required = True)

class ProductCategory(db.Model):
	productName = db.StringProperty(required = True)
	productCategories = db.TextProperty(required = False)

class CategoryBase(db.Model):
	categoryName = db.StringProperty(required = True)
	categoryPicture = db.StringProperty(required = True)
	categoryDesc = db.TextProperty(required = True)

"""========================================================HELPER FUNCTIONS========================"""

def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(username, password, salt = make_salt()):
	h = hashlib.sha256(username + password + salt).hexdigest()
	return '%s|%s'%(h,salt)

def valid_pw(name, pw, h):
	salt = h.split('|')[1]
	return h == make_pw_hash(name, pw, salt)

def generate_key():
	key = ""
	for x in range(0,9):
		key = key + str(random.randint(0,10))
	return int(key)


"""======================================================================================================"""
def userbase():
	return "UserBase"

def storebase():
	return "StoreBase"

def productbase():
	return "ProuctBase"

def ownerbase():
	return "OwnerBase"

def categorybase():
	return "CategoryBase"

def storeproducts():
	return "StoreProducts"

def categoryproducts():
	return "CategoryProducts"


"""======================================================================================================"""

def get_cache(cache_base):
	cache = memcache.get(cache_base)
	if cache is None:
		if cache_base == ownerbase():
			restore_cache(ownerbase())
			restore_cache(storebase())
		else:
			restore_cache(cache_base)
		cache = memcache.get(cache_base)
	return cache

def check_cache(cache_base, cache_key):

	cache_dict = get_cache(cache_base)
	logging.error(cache_dict)
	
	if cache_dict:
		logging.error('retrieve item')
		logging.error(cache_dict)
		logging.error(cache_key)
		item = cache_dict.get(cache_key)
		if item:
			logging.error(item)
			return item


def restore_cache(database):
	logging.error("Create cache")
	base_dict = {}
	
	if database == userbase():
		query = db.GqlQuery('SELECT * FROM UserBase')
		for q in query:
			base_dict[q.username] = [q.saltedPass]

	if database == categorybase():
		query = db.GqlQuery('SELECT * FROM CategoryBase')
		for q in query:
			base_dict[q.categoryName] = {'categoryPicture':q.categoryPicture, 'categoryDesc':q.categoryDesc}

	if database == ownerbase():
		query = db.GqlQuery('SELECT * FROM OwnerBase')
		for q in query:
			base_dict[q.username] = {'storeOwner': q.username, 'storeName': []}

	if database == storebase():
		query = db.GqlQuery('SELECT * FROM StoreBase')
		owner_cache = get_cache(ownerbase())
		if owner_cache is None:
			owner_cache = {}

		for q in query:
			base_dict[q.storeName] = {'storeLogo':q.storeLogo, 'storeLocation':q.storeLocation, 'storeOwner':q.storeOwner, 'storeDesc':q.storeDesc}
			logging.error('CHECK HEEEERRRRREEEEE  owner record=============')

			owner_record = owner_cache.get(q.storeOwner)
			if owner_record:
				storeArray = owner_record['storeName']
				storeArray.append(q.storeName)
				owner_record['storeName'] = storeArray
				logging.error(owner_record)
				owner_cache[q.storeOwner] = owner_record
			else:
				owner_cache[q.storeOwner] = {'storeOwner':q.storeOwner, 'storeName':[q.storeName]}

		memcache.set(ownerbase(), owner_cache)

	if database == productbase():
		query = db.GqlQuery('SELECT * FROM ProductBase')
		for q in query:
			# Queries to connect related database elements 
			queryStores = db.GqlQuery("SELECT * FROM ProductStore WHERE productName ="+"'"+str(q.productName)+"'")
			queryCategory = db.GqlQuery("SELECT * FROM ProductCategory WHERE productName ="+"'"+str(q.productName)+"'")
			storeArray=[]
			categoryArray=[]

			for store in queryStores:
				storeArray.append(store.productStore)

			for category in queryCategory:
				categoryArray.append(category.productCategories)

			base_dict[q.productName] = {'productImage':q.productImage, 'productDesc':q.productDesc, 'productStore':storeArray, 'productCategories': categoryArray, 'productPrice': q.productPrice}

		querySt = db.GqlQuery('SELECT * FROM ProductStore')
		queryCat = db.GqlQuery('SELECT * FROM ProductCategory')

		storeProd = {}
		for s in querySt:
			products = storeProd.get(s.productStore)
			if products:
				storeProd[s.productStore] = products.append(s.productName)
			else:
				storeProd[s.productStore] = [s.productName]

		storeCat = {}
		for c in queryCat:
			categories = storeProd.get(c.productCategories)
			if products:
				storeProd[c.productCategories] = products.append(c.productName)
			else:
				storeProd[c.productCategories] = [c.productName]

		memcache.set(storeproducts(), storeProd)
		memcache.set(categoryproducts(), storeCat)

	memcache.set(database, base_dict)
	return memcache.get(database)

def create_db_entry(database, key, entarray = None):
	logging.error("Create DB")
	if database == userbase():
		logging.error("Database == USerbase")
		saltedPass = make_pw_hash(key, entarray)
		entry = UserBase(username = key, saltedPass = saltedPass)
		update_memcache(database,key, entry = [saltedPass])

	if database == ownerbase():
		logging.error("Database == Ownerbase")
		entry = OwnerBase(username = key)
		update_memcache(ownerbase(), key, {'storeOwner':key, 'storeName':[]})

	if database == categorybase():
		logging.error("Database == Categorybase")
		entry = CategoryBase(categoryName = key, categoryPicture = entarray['categoryPicture'], categoryDesc = entarray['categoryDesc'])
		update_memcache(categorybase(), key, entarray)

	if database == storebase():
		logging.error("Database == Storebase")
		entry = StoreBase(storeName = key, storeLogo = entarray['storeLogo'], storeLocation = entarray['storeLocation'], storeOwner = entarray['storeOwner'], storeDesc = entarray['storeDesc'])
		update_memcache(database, key, entarray)

		update_memcache(ownerbase(), entarray['storeOwner'], key, True)

	if database == productbase():
		logging.error("Database == Storebase")
		productCode = generate_key()
		entry = ProductBase(productName = key, productImage = entarray['productImage'] ,productPrice = entarray['productPrice'], productDesc = entarray['productDesc'])
		update_memcache(database, key, entarray)
		
		if entarray['productStore']:
			entry3 = ProductStore(productName = key, productStore = entarray['productStore'])
			entry3.put()
		
		if entarray['productCategories']:
			entry4 = ProductCategory(productName = key, productCategories = entarray['productCategories'])
			entry4.put()
		
		#entry2.put()
		#entry3.put()
		#entry4.put()
	entry.put()	
		

def update_memcache(database, key, entry, update = False):
	logging.error("enter cache update")
	cache_dict = get_cache(database)

	if update and database == ownerbase():
		record = cache_dict[key]
		storelist = record['storeName']
		storelist.append(entry)

		record['storeName'] = storelist
		cache_dict[key] = record

	else:
		cache_dict[key] = entry
	
	memcache.set(database, cache_dict)


def check_login(username, password):
	logging.error('check login')
	saltedPass = check_cache(userbase(), username)

	if saltedPass:
		saltedPass = saltedPass[0]
		if valid_pw(username, password, saltedPass):
			return True

def dictionary_keys(database):
	if database == storebase():
		dictionary = memcache.get(userbase())
		if dictionary is None:
			dictionary = restore_cache(userbase())
		
	return dictionary.keys()



"""========================================================CLASSES=================================="""


class BaseClass(webapp2.RequestHandler):
	def write(self, *a, **k):
		self.response.out.write(*a, **k)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **params):
		self.write(self.render_str(template, **params))

	def login(self, username, password, nexturl = '/'):
		
		logging.error('Login')

		if check_login(username,password):
			passSalt = check_cache(userbase(), username)
			passSalt = passSalt[0]
			login_cookie = "%s|%s" % (str(username), str(passSalt))
			self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % login_cookie)
			self.redirect(nexturl)
			return True


	def log_out(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def log_check(self):
		cookie = self.request.cookies.get('user_id')
		if cookie:
			username = cookie.split('|')[0]
			passhash = cookie.split('|')[1]
			cookie_check = check_cache(userbase(), username)

			if cookie_check and passhash == cookie_check[0].split('|')[0]:
				return username
			else:
				return False
		else:
			return False



"""========================End of BaseClass=============================================="""

class MainHandler(BaseClass):
    def get(self):
    	products = get_cache(productbase())
    	stores = get_cache(storebase())
    	categories = get_cache(categorybase())
        self.render("home.html", stores = stores, products = products, categories =categories)

class Signup(BaseClass):
	def get(self):
		nexturl = self.request.headers.get('referer', '/')
		self.render("signup.html", nexturl = nexturl)

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")

		
		nexturl = str(self.request.get("nexturl"))
		if not nexturl or nexturl.startswith('/login'):
			nexturl = '/'

		e_username = ""
		e_password = ""
		e_verify = ""

		UName = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
		Pword = re.compile(r"^.{3,20}$")
	

		if UName.match(username) and Pword.match(password) and password == verify:
			user = check_cache(userbase(), username)
			if user:
				self.login(username, password, nexturl)
			else:
				logging.error("Inputs verified")
				create_db_entry(userbase(), username, password)
				self.login(username, password, nexturl)

		else:
			if username == "":
				e_username = "You goofed the username"
			if password =="":
				e_password = "You goofed the password"
			if verify == "" or (verify != password):
				e_verify = "You goofed the verify"
			
			self.render("signup.html", username=username, e_username = e_username, e_password = e_password, e_verify = e_verify)


class Logout(BaseClass):
	def get(self):
		nexturl = self.request.headers.get('referer', '/')
		self.log_out()
		self.redirect(nexturl)


class Login(BaseClass):
	def get(self):
		nexturl = self.request.headers.get('referer', '/')
		self.log_out()
		self.render("login.html", nexturl = nexturl)

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		nexturl = str(self.request.get('nexturl'))
		if not nexturl or nexturl.startswith('/login'):
			nexturl = '/'

		if self.login(username, password):
			self.redirect(nexturl)
		else:
			self.render("login.html", error = "Incorrect username or password")

#A Site for checking all the database entries and caches
class userCheck(BaseClass):
	def get(self):
		user = self.log_check()
		usercache = get_cache(userbase())
		storecache = get_cache(storebase())
		productcache = get_cache(productbase())
		ownercache = get_cache(ownerbase())
		
		if user:
			self.render("usercheck.html", logstatus = "logged in", username = user, usercache = usercache, storecache = storecache, productcache =productcache, ownercache = ownercache)
		else:
			self.render("usercheck.html", logstatus = "logged in", username = user, usercache = usercache, storecache = storecache, productcache =productcache, ownercache = ownercache)

# ======================= Product Content ==========================================
class productForm(BaseClass):
	def get(self):
		owner = self.log_check()
		ownerdict = check_cache(ownerbase(), owner)
		categories = get_cache(categorybase()).keys()
		if categories is None:
			categories = []

		if owner and ownerdict:
			self.render("productform.html", storeName = ownerdict['storeName'], categories = categories)
		else:
			self.redirect('/')


	def post(self):
		prodName = self.request.get("prodname")
		prodImage = self.request.get("prodimage")
		price = float(self.request.get("price"))
		productDesc = self.request.get("proddesc")
		store = self.request.get("store")
		category = self.request.get("category")

		if prodName and prodImage and price and productDesc and store and category:
			logging.error("Accepted prodform")
			entry = {'productImage':prodImage, 'productPrice':price, 'productDesc':productDesc, 'productStore':store, 'productCategories':category}
			create_db_entry(productbase(), prodName, entry)
			self.redirect('/product/%s'%prodName)
		else:
			self.render("productform.html")


class productPage(BaseClass):
	def get(self, product_name):
		product_name = product_name[1:]
		product = check_cache(productbase(), product_name)
		
		if product:
			store = check_cache(storebase(), product['productStore'][0])
			
			self.render("productpage.html", Name = product_name, image = product['productImage'], store = product['productStore'], price = product['productPrice'], desc = product['productDesc'], location = store['storeLocation'])
		else:
			self.render("productpage.html")

#======================= Category Form ============================================
class categoryForm(BaseClass):
	def get(self):
		owner = self.log_check()
		ownerdict = check_cache(ownerbase(), owner)

		if owner and ownerdict:
			self.render("categoryForm.html")
		else:
			self.redirect('/')

	def post(self):
		Name = self.request.get("catname")
		Image = self.request.get("catimage")
		Desc = self.request.get("catdesc")
		logging.error('Name')
		logging.error(Name)
		logging.error('Image')
		logging.error(Image)
		logging.error('Desc')
		logging.error(Desc)

		if Name and Image and Desc:
			logging.error("Accepted catform")
			entry = {'categoryPicture':Image, 'categoryDesc':Desc}
			create_db_entry(categorybase(), Name, entry)
			self.redirect('/categories')
		else:
			self.render("categoryForm.html")


class categories(BaseClass):
	def get(self):
		category_catalogue = get_cache(categorybase())

		self.render('categories.html', category_catalogue = category_catalogue)

# ======================= Store Content ==========================================
class storeForm(BaseClass):
	def get(self):
		owner = self.log_check()
		ownerdict = check_cache(ownerbase(), owner)
		

		if owner and ownerdict:
			self.render("storeform.html", user = owner)
		else:
			self.redirect('/')

	def post(self):
		storeName = self.request.get("storename")
		storeLogo = self.request.get("storeLogo")
		storeLocation = self.request.get("location")
		storeOwner = self.request.get("owner")
		storeDesc = self.request.get("storedesc")

		if storeName and storeLogo and storeLocation and storeOwner:
			logging.error("Accepted form")
			entry = {'storeLogo':storeLogo, 'storeLocation':storeLocation, 'storeOwner':storeOwner, 'storeDesc':storeDesc}
			create_db_entry(storebase(), storeName, entry)
			self.redirect('/store/%s'%storeName)
		else:
			logging.error("Rejected form")
			e_storename = "Store Name missing"
			e_storelogo = "Store Logo missing"
			e_location = "Location missing"
			e_owner = "Owner missing"

			if storeName:
				e_storename = ""
			if storeLogo:
				e_storelogo = ""
			if location:
				e_location = ""
			if owner:
				e_owner = ""

			self.render("storeform.html", e_storename = e_storename, e_storelogo = e_storelogo, e_location = e_location, e_owner = e_owner)

class storePage(BaseClass):
	def get(self, entry_id):
		entry_id = entry_id[1:]
		logging.error(entry_id)
		store = check_cache(storebase(), entry_id)

		if store:
			products = get_cache(storeproducts())
			self.render("storepage.html", storeName = entry_id, logo=store['storeLogo'], location=store['storeLocation'] , owner=store['storeOwner'], desc=store['storeDesc'], products = products)
		else:
			self.redirect('/storeForm')


class Admin(BaseClass):
	def get(self):
		admin = self.log_check()
		users = get_cache(userbase())
		users = users.keys()

		if admin and admin == 'Admin':
			self.render("adminConsole.html", users = users)
		else:
			self.redirect('/')

	def post(self):
		owner = self.request.get('owner')

		if owner:
			create_db_entry(ownerbase(), owner)
			self.redirect('/usercheck')

class catalogue(BaseClass):
	def get(self, pagetype):
		pagetype= pagetype[1:]

		if pagetype == "products":
			content = get_cache(productbase())
			self.render("catalogue.html", pagetype = pagetype, content = content)
		if pagetype == "stores":
			content = get_cache(storebase())
			self.render("catalogue.html", pagetype = pagetype, content = content)
		if pagetype == "categories":
			content = get_cache(categorybase())
			self.render("catalogue.html", pagetype = pagetype, content = content)

		

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/signup', Signup),
    ('/login', Login),
    ('/logout', Logout),
    ('/admin', Admin),
    ('/usercheck', userCheck),
    ('/categoryform', categoryForm),
    ('/categories', categories),
    ('/productform', productForm),
    ('/product'+PAGE_RE, productPage),	
    ('/storeform', storeForm),
    ('/catalogue'+PAGE_RE, catalogue),
    ('/store'+PAGE_RE, storePage)
], debug=True)
