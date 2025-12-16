This is a complete Auto Parts Management System for car parts stores. It helps store owners manage their inventory, process sales, handle returns, and keep track of everything in one place.

Main Features
1. Dashboard
See important numbers at a glance

View today's sales and returns

Check how many products are low in stock

Quick buttons to add products or make sales

2. Inventory Management
View all products in stock

Search for products by name or brand

Add new products

Edit product details

Move products to trash (can be restored later)

3. Point of Sale (POS)
Easy checkout system

Scan or search for products

Shopping cart for multiple items

Print or save receipts

Customer name and notes

4. Sales History
See all past sales

Filter by date or invoice number

Track returns and refunds

Clear old records if needed

5. Returns Management
Process returns easily

Select from recent sales

Choose return reasons (defective, wrong item, etc.)

Update inventory automatically

6. Trash Bin
Restore deleted products

Permanently delete items

Empty entire trash bin

7. Auto Parts Catalog
Pre-loaded parts for popular brands:

Toyota

Honda

Mitsubishi

Ford

Nissan

Hyundai

Import all catalogs with one click

Filter by brand in POS

8. Settings
Import/clear catalogs

Clear sales history

View system information

Database management

How to Use
First Time Setup
Run main.py to start the program

Login with:

Username: autoparts

Password: oilengine

The system will auto-load sample parts catalogs

Basic Operations
To sell a product:

Click "Point of Sale" in sidebar

Search for product

Double-click to add to cart

Enter customer name (optional)

Click "Process Sale"

To add a product:

Click "Inventory" in sidebar

Click "Add Product" button

Fill in product details

Click "Save Product"

To process a return:

Click "Returns" in sidebar

Select a recent sale

Enter return quantity and reason

Click "Process Return"

System Requirements
Python 3.7 or higher

Required Python packages:

customtkinter

tkinter (usually comes with Python)

Installation
Make sure Python is installed on your computer

Install required packages:

text
pip install customtkinter
Download all the system files

Run main.py to start

Files in the System
main.py - Starts the program

app.py - Main application

database.py - Handles data storage

gui_manager.py - Creates the user interface

inventory_manager.py - Manages products

sales_manager.py - Handles sales

pos_manager.py - Point of sale system

returns_manager.py - Manages returns

trash_manager.py - Handles deleted items

catalog_manager.py - Manages auto parts catalogs

utils.py - Shared functions and settings

nissan.py, toyota.py, etc. - Parts catalogs for different car brands

Tips for Users
Always backup before clearing sales history or inventory

Use the search feature to find products quickly

The trash bin keeps deleted items for 30 days

Import catalogs to get started with sample products

Use filters in POS to see products by brand

Need Help?
If something doesn't work:

Check if all files are in the same folder

Make sure Python is installed correctly

Try restarting the program

Check for error messages on screen

Security Note
Change the default username and password

The system uses a local database file (autoparts.db)

Regular backups are recommended

This system is designed to be simple and easy to use for auto parts store owners. No technical knowledge is needed to operate it!
