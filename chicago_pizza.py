import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Initialize the database
def init_db():
    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()
    
    # Create the customer table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            delivery_fee REAL NOT NULL
        )
    ''')

    # Create the menu table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            item_number INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            price_s REAL NOT NULL,
            price_m REAL NOT NULL,
            price_l REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Function to search for a customer by phone number
def search_customer_by_phone(phone):
    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
    customer = cur.fetchone()
    conn.close()
    return customer

# Function to open the order detail page
def open_order_page(customer=None, phone=None):
    order_page = tk.Toplevel(root)
    order_page.title("Order Detail")
    order_page.geometry("500x500")
    
    frame = ttk.Frame(order_page, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Components for the order detail page
    customer_name_label = ttk.Label(frame, text="Customer Name:")
    customer_name_label.grid(row=1, column=0, sticky=tk.W, pady=5)
    customer_name_entry = ttk.Entry(frame, width=40)
    customer_name_entry.grid(row=1, column=1, pady=5)

    customer_address_label = ttk.Label(frame, text="Customer Address:")
    customer_address_label.grid(row=2, column=0, sticky=tk.W, pady=5)
    customer_address_entry = ttk.Entry(frame, width=40)
    customer_address_entry.grid(row=2, column=1, pady=5)

    phone_label = ttk.Label(frame, text="Customer Phone:")
    phone_label.grid(row=3, column=0, sticky=tk.W, pady=5)
    phone_entry = ttk.Entry(frame, width=40)
    phone_entry.grid(row=3, column=1, pady=5)

    order_label = ttk.Label(frame, text="Order Details:")
    order_label.grid(row=4, column=0, sticky=tk.W, pady=5)
    order_text = tk.Text(frame, width=40, height=10)
    order_text.grid(row=4, column=1, pady=5)

    delivery_fee_label = ttk.Label(frame, text="Delivery Fee: ")
    delivery_fee_label.grid(row=6, column=0, sticky=tk.W, pady=5)
    
    # Populate fields if customer data is provided
    if customer:
        customer_name_entry.insert(0, customer[1])
        customer_address_entry.insert(0, customer[2])
        phone_entry.insert(0, customer[3])
        delivery_fee_label.config(text=f"Delivery Fee: {customer[4]}")
    elif phone:
        phone_entry.insert(0, phone)  # Pre-fill the phone number if provided
    else:
        delivery_fee_label.config(text="Delivery Fee: ")

    def on_close():
        order_page.destroy()
        open_work_page()

    order_page.protocol("WM_DELETE_WINDOW", on_close)

    submit_button = ttk.Button(frame, text="Submit Order", command=lambda: submit_order(
        customer_name_entry, customer_address_entry, phone_entry, order_text, order_page))
    submit_button.grid(row=5, column=1, pady=20)

# Function to submit an order
def submit_order(customer_name_entry, customer_address_entry, phone_entry, order_text, order_page):
    customer_name = customer_name_entry.get()
    customer_address = customer_address_entry.get()
    phone = phone_entry.get()
    order_details = order_text.get("1.0", tk.END)
    delivery_fee = calculate_delivery_fee(customer_address)

    save_customer(customer_name, customer_address, phone, delivery_fee)

    print(f"Customer Name: {customer_name}")
    print(f"Customer Address: {customer_address}")
    print(f"Customer Phone: {phone}")
    print(f"Order Details: {order_details}")
    print(f"Delivery Fee: {delivery_fee}")

    order_page.destroy()
    open_work_page()

# Function to calculate delivery fee (simple example)
def calculate_delivery_fee(address):
    return 5.00

# Function to save customer information to the database
def save_customer(name, address, phone, delivery_fee):
    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()
    
    # Check if the customer already exists
    cur.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
    customer = cur.fetchone()
    
    if customer:
        # Update the existing customer
        cur.execute('''
            UPDATE customers
            SET name = ?, address = ?, delivery_fee = ?
            WHERE phone = ?
        ''', (name, address, delivery_fee, phone))
    else:
        # Insert a new customer
        cur.execute('''
            INSERT INTO customers (name, address, phone, delivery_fee)
            VALUES (?, ?, ?, ?)
        ''', (name, address, phone, delivery_fee))
    
    conn.commit()
    conn.close()

# Function to open the work page with search functionality
def open_work_page():
    # Hide the main page
    root.withdraw()
    
    # Create the new work page
    work_page = tk.Toplevel(root)
    work_page.title("Search Customer")
    work_page.geometry("500x100")
    
    # Frame for the new page
    frame = ttk.Frame(work_page, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Search bar
    search_label = ttk.Label(frame, text="Search by Phone:")
    search_label.grid(row=0, column=0, pady=10)
    
    search_entry = ttk.Entry(frame, width=30)
    search_entry.grid(row=0, column=1, pady=10)
    
    def search_action_work():
        phone = search_entry.get()
        customer = search_customer_by_phone(phone)
        if customer:
            open_order_page(customer)
            work_page.destroy()  # Close the work page after opening order page
        else:
            messagebox.showinfo("Customer Not Found", "Customer not found, starting with a blank order page.")
            open_order_page(phone=phone)  # Pass the phone number to pre-fill
            work_page.destroy()  # Close the work page after opening order page
    
    # Search button
    search_button = ttk.Button(frame, text="Search", command=search_action_work)
    search_button.grid(row=0, column=2, padx=10)
    
    # Callback to reopen main page if work page is closed
    def on_work_page_close():
        work_page.destroy()
        root.deiconify()  # Show the main page again

    work_page.protocol("WM_DELETE_WINDOW", on_work_page_close)

    work_page.mainloop()

# Function to open the menu management page
def open_menu_page():
    # Create the new menu page
    menu_page = tk.Toplevel(root)
    menu_page.title("Menu Management")
    menu_page.geometry("700x500")
    
    frame = ttk.Frame(menu_page, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Input fields for adding new menu items
    item_number_label = ttk.Label(frame, text="Item Number:")
    item_number_label.grid(row=0, column=0, sticky=tk.W, pady=5)
    item_number_entry = ttk.Entry(frame, width=20)
    item_number_entry.grid(row=0, column=1, pady=5)

    item_name_label = ttk.Label(frame, text="Item Name:")
    item_name_label.grid(row=1, column=0, sticky=tk.W, pady=5)
    item_name_entry = ttk.Entry(frame, width=20)
    item_name_entry.grid(row=1, column=1, pady=5)

    price_s_label = ttk.Label(frame, text="Price (S):")
    price_s_label.grid(row=2, column=0, sticky=tk.W, pady=5)
    price_s_entry = ttk.Entry(frame, width=20)
    price_s_entry.grid(row=2, column=1, pady=5)

    price_m_label = ttk.Label(frame, text="Price (M):")
    price_m_label.grid(row=3, column=0, sticky=tk.W, pady=5)
    price_m_entry = ttk.Entry(frame, width=20)
    price_m_entry.grid(row=3, column=1, pady=5)

    price_l_label = ttk.Label(frame, text="Price (L):")
    price_l_label.grid(row=4, column=0, sticky=tk.W, pady=5)
    price_l_entry = ttk.Entry(frame, width=20)
    price_l_entry.grid(row=4, column=1, pady=5)

    # Button to add a new menu item
    add_item_button = ttk.Button(frame, text="Add/Update Item", command=lambda: add_update_menu_item(
        item_number_entry, item_name_entry, price_s_entry, price_m_entry, price_l_entry, menu_page))
    add_item_button.grid(row=5, column=1, pady=10)

    # Search bar and listbox for searching and displaying menu items
    search_label = ttk.Label(frame, text="Search Item:")
    search_label.grid(row=6, column=0, sticky=tk.W, pady=5)

    search_entry = ttk.Entry(frame, width=30)
    search_entry.grid(row=6, column=1, pady=5)

    listbox = tk.Listbox(frame, width=50, height=10)
    listbox.grid(row=7, column=0, columnspan=2, pady=10)

    # Function to update listbox based on search
    def update_listbox(*args):
        search_term = search_entry.get()
        listbox.delete(0, tk.END)
        for item in search_menu_items(search_term):
            listbox.insert(tk.END, f"{item[0]}: {item[1]} - S: {item[2]}, M: {item[3]}, L: {item[4]}")

    search_entry.bind('<KeyRelease>', update_listbox)

    # Populate the listbox initially with all menu items
    update_listbox()

    menu_page.mainloop()

# Function to add or update a menu item in the database
def add_update_menu_item(item_number_entry, item_name_entry, price_s_entry, price_m_entry, price_l_entry, menu_page):
    item_number = int(item_number_entry.get())
    item_name = item_name_entry.get()
    price_s = float(price_s_entry.get())
    price_m = float(price_m_entry.get())
    price_l = float(price_l_entry.get())

    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()
    
    # Check if the item already exists
    cur.execute('SELECT * FROM menu WHERE item_number = ?', (item_number,))
    item = cur.fetchone()
    
    if item:
        # Update the existing menu item
        cur.execute('''
            UPDATE menu
            SET item_name = ?, price_s = ?, price_m = ?, price_l = ?
            WHERE item_number = ?
        ''', (item_name, price_s, price_m, price_l, item_number))
    else:
        # Insert a new menu item
        cur.execute('''
            INSERT INTO menu (item_number, item_name, price_s, price_m, price_l)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_number, item_name, price_s, price_m, price_l))
    
    conn.commit()
    conn.close()

    menu_page.destroy()
    open_menu_page()

# Function to search for menu items in the database
def search_menu_items(search_term):
    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()
    
    # Search for menu items that match the search term
    cur.execute('''
        SELECT * FROM menu WHERE item_name LIKE ?
    ''', (f'%{search_term}%',))
    
    items = cur.fetchall()
    conn.close()
    return items

# Main application window (main page)
root = tk.Tk()
root.title("Pizza Cashiering System - Main Page")
root.geometry("500x500")

# Main page components
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

work_button = ttk.Button(frame, text="Work", command=open_work_page)
work_button.grid(row=1, column=0, pady=10)

customer_button = ttk.Button(frame, text="Customer Management")
customer_button.grid(row=2, column=0, pady=10)

menu_button = ttk.Button(frame, text="Menu Management", command=open_menu_page)
menu_button.grid(row=3, column=0, pady=10)

# Initialize the database
init_db()

root.mainloop()
