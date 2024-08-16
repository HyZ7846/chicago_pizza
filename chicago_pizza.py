import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, os, datetime

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

    # Create the side order table with the correct structure
    cur.execute('''
        CREATE TABLE IF NOT EXISTS side_order (
            item_number INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            price_s REAL NOT NULL DEFAULT 0.00,
            price_m REAL NOT NULL DEFAULT 0.00,
            price_l REAL NOT NULL DEFAULT 0.00,
            FOREIGN KEY (item_number) REFERENCES menu(item_number)
        )
    ''')

    conn.commit()
    conn.close()

# Function to get the next receipt number
def get_next_receipt_number():
    if not os.path.exists("receipts"):
        os.makedirs("receipts")
    
    receipt_files = [f for f in os.listdir("receipts") if f.endswith(".txt")]
    if receipt_files:
        receipt_numbers = [int(f.split("#")[1].split(".")[0]) for f in receipt_files]
        return max(receipt_numbers) + 1
    else:
        return 1

# Function to get the current timestamp
def get_current_timestamp():
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M")

# Function to search for a customer by phone number
def search_customer_by_phone(phone):
    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
    customer = cur.fetchone()
    conn.close()
    return customer

# Function to open the order detail page
# Updated order detail page function to pass delivery_fee_entry to finish_order and submit_order
def open_order_page(customer=None, phone=None):
    order_page = tk.Toplevel(root)
    order_page.title("Order Detail")
    order_page.geometry("600x700")
    
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

    # Pizza Number Section
    pizza_number_label = ttk.Label(frame, text="Pizza Number:")
    pizza_number_label.grid(row=4, column=0, sticky=tk.W, pady=5)
    pizza_number_entry = ttk.Entry(frame, width=10)
    pizza_number_entry.grid(row=4, column=1, sticky=tk.W, pady=5)

    pizza_size_label = ttk.Label(frame, text="Pizza Size:")
    pizza_size_label.grid(row=5, column=0, sticky=tk.W, pady=5)
    
    pizza_size_var = tk.StringVar()
    pizza_size_var.set("S")  # Default value

    pizza_size_s = ttk.Radiobutton(frame, text="S", variable=pizza_size_var, value="S")
    pizza_size_s.grid(row=5, column=1, sticky=tk.W, pady=5)

    pizza_size_m = ttk.Radiobutton(frame, text="M", variable=pizza_size_var, value="M")
    pizza_size_m.grid(row=5, column=1, padx=50, sticky=tk.W, pady=5)

    pizza_size_l = ttk.Radiobutton(frame, text="L", variable=pizza_size_var, value="L")
    pizza_size_l.grid(row=5, column=1, padx=100, sticky=tk.W, pady=5)

    # Button to add the selected pizza to the order notes
    add_pizza_button = ttk.Button(frame, text="Add to Order", command=lambda: add_pizza_to_order(
        pizza_number_entry.get(), pizza_size_var.get(), order_text))
    add_pizza_button.grid(row=6, column=1, pady=10)

    # Side Order Section
    side_order_label = ttk.Label(frame, text="Side Order:")
    side_order_label.grid(row=7, column=0, sticky=tk.W, pady=10)

    search_label = ttk.Label(frame, text="Search item:")
    search_label.grid(row=8, column=0, sticky=tk.W, pady=5)

    side_search_entry = ttk.Entry(frame, width=30)
    side_search_entry.grid(row=8, column=1, pady=5)

    side_listbox = tk.Listbox(frame, width=30, height=3)
    side_listbox.grid(row=9, column=1, columnspan=2, pady=5)

    def update_side_listbox(*args):
        search_term = side_search_entry.get()
        side_listbox.delete(0, tk.END)
        for item in search_menu_items(search_term, "Side"):
            side_listbox.insert(tk.END, f"{item[1]} - ${item[2]}")

    side_search_entry.bind('<KeyRelease>', update_side_listbox)

    def add_side_to_order():
        selected_item = side_listbox.get(tk.ACTIVE)
        if selected_item:
            order_text.insert(tk.END, f"{selected_item}\n")

    add_side_button = ttk.Button(frame, text="Add to Order", command=add_side_to_order)
    add_side_button.grid(row=10, column=1, pady=5)

    # Delivery Fee
    delivery_fee_label = ttk.Label(frame, text="Delivery Fee: ")
    delivery_fee_label.grid(row=11, column=0, sticky=tk.W, pady=5)
    delivery_fee_entry = ttk.Entry(frame, width=10)
    delivery_fee_entry.grid(row=11, column=1, sticky=tk.W, pady=5)

    # Order Notes Section
    order_label = ttk.Label(frame, text="Order Notes:")
    order_label.grid(row=13, column=0, sticky=tk.W, pady=10)
    order_text = tk.Text(frame, width=40, height=8)
    order_text.grid(row=14, column=0, columnspan=2, pady=5)

    # Populate fields if customer data is provided
    if customer:
        customer_name_entry.insert(0, customer[1])
        customer_address_entry.insert(0, customer[2])
        phone_entry.insert(0, customer[3])
        delivery_fee_entry.insert(0, f"{customer[4]:.2f}")
    elif phone:
        phone_entry.insert(0, phone)  # Pre-fill the phone number if provided
        fetch_delivery_fee(phone, delivery_fee_entry)  # Fetch delivery fee from the database
    else:
        delivery_fee_entry.insert(0, "0.00")

    def on_close():
        order_page.destroy()
        open_work_page()

    order_page.protocol("WM_DELETE_WINDOW", on_close)

    finish_order_button = ttk.Button(frame, text="Finish Order", command=lambda: finish_order(order_text, delivery_fee_entry))
    finish_order_button.grid(row=15, column=0, pady=20, sticky=tk.W)

    submit_button = ttk.Button(frame, text="Submit Order", command=lambda: submit_order(
        customer_name_entry, customer_address_entry, phone_entry, order_text, delivery_fee_entry, order_page))
    submit_button.grid(row=15, column=1, pady=20)


# Function to fetch delivery fee from the database using phone number
def fetch_delivery_fee(phone, delivery_fee_entry):
    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()
    cur.execute('SELECT delivery_fee FROM customers WHERE phone = ?', (phone,))
    result = cur.fetchone()
    conn.close()
    if result:
        delivery_fee_entry.delete(0, tk.END)
        delivery_fee_entry.insert(0, f"{result[0]:.2f}")

# Function to add pizza to the order notes
def add_pizza_to_order(pizza_number, pizza_size, order_text):
    if not pizza_number:
        #messagebox.showerror("Input Error", "Please enter a valid pizza number.")
        return

    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()

    cur.execute('SELECT item_name, price_s, price_m, price_l FROM menu WHERE item_number = ?', (pizza_number,))
    pizza = cur.fetchone()

    conn.close()

    if pizza:
        item_name = pizza[0]
        if pizza_size == "S":
            item_price = pizza[1]
        elif pizza_size == "M":
            item_price = pizza[2]
        else:
            item_price = pizza[3]

        order_text.insert(tk.END, f"#{pizza_number} {item_name} - ${item_price:.2f}\n")
    else:
        return
        #messagebox.showerror("Not Found", "Pizza with this item number does not exist.")

# Function to calculate subtotal, tax, and finish the order
def finish_order(order_text, delivery_fee_entry):
    lines = order_text.get("1.0", tk.END).strip().split("\n")
    subtotal = 0.00
    for line in lines:
        if '-' in line:
            price = float(line.split('- $')[-1].strip())
            subtotal += price

    delivery_fee = float(delivery_fee_entry.get())
    subtotal += delivery_fee
    tax = subtotal * 0.05
    total = subtotal + tax

    order_text.insert(tk.END, f"\n\nDelivery - ${delivery_fee:.2f}\n")
    order_text.insert(tk.END, f"Tax - ${tax:.2f}\n{'-'*20}\nSubtotal - ${total:.2f}\n")

# Function to submit an order
def submit_order(customer_name_entry, customer_address_entry, phone_entry, order_text, delivery_fee_entry, order_page):
    customer_name = customer_name_entry.get()
    customer_address = customer_address_entry.get()
    phone = phone_entry.get()
    order_details = order_text.get("1.0", tk.END)
    delivery_fee = float(delivery_fee_entry.get())

    save_customer(customer_name, customer_address, phone, delivery_fee)

    receipt_number = get_next_receipt_number()
    timestamp = get_current_timestamp()

    receipt_content = f"Receipt# {receipt_number}\n{timestamp}\n\n"
    receipt_content += f"Customer Name: {customer_name}\n"
    receipt_content += f"Customer Address: {customer_address}\n"
    receipt_content += f"Customer Phone: {phone}\n\n"
    receipt_content += f"Order Details:\n{order_details}\n"
    receipt_content += f"Delivery Fee: ${delivery_fee:.2f}\n"

    # Save the receipt to a file
    receipt_filename = f"receipts/Receipt#{receipt_number}.txt"
    with open(receipt_filename, "w") as f:
        f.write(receipt_content)

    print(f"Receipt saved as {receipt_filename}")

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
            #messagebox.showinfo("Customer Not Found", "Customer not found, starting with a blank order page.")
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

def open_menu_page(menu_type):
    menu_page = tk.Toplevel(root)
    menu_page.title(f"{menu_type} Management")
    menu_page.geometry("700x500")
    
    frame = ttk.Frame(menu_page, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    price_labels = ["Price (S)", "Price (M)", "Price (L)"]

    # Input fields for adding new menu items
    item_number_label = ttk.Label(frame, text="Item Number:")
    item_number_label.grid(row=0, column=0, sticky=tk.W, pady=5)
    item_number_entry = ttk.Entry(frame, width=20)
    item_number_entry.grid(row=0, column=1, pady=5)

    item_name_label = ttk.Label(frame, text="Item Name:")
    item_name_label.grid(row=1, column=0, sticky=tk.W, pady=5)
    item_name_entry = ttk.Entry(frame, width=20)
    item_name_entry.grid(row=1, column=1, pady=5)

    price_entries = []
    for i, label in enumerate(price_labels):
        price_label = ttk.Label(frame, text=label)
        price_label.grid(row=2 + i, column=0, sticky=tk.W, pady=5)
        price_entry = ttk.Entry(frame, width=20)
        price_entry.insert(0, "0.00")  # Set default value to 0.00
        price_entry.grid(row=2 + i, column=1, pady=5)
        price_entries.append(price_entry)

    # Button to add or update a menu item
    add_item_button = ttk.Button(frame, text="Add/Update Item", command=lambda: add_update_menu_item(
        item_number_entry, item_name_entry, price_entries, menu_page, menu_type))
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
        
        items = search_menu_items(search_term, menu_type)
        
        for item in items:
            if menu_type == "Pizza":
                listbox.insert(tk.END, f"{item[0]}: {item[1]} - S: {item[2]}, M: {item[3]}, L: {item[4]}")
            else:  # Side Menu
                listbox.insert(tk.END, f"{item[0]}: {item[1]} - S: {item[2]}, M: {item[3]}, L: {item[4]}")

    search_entry.bind('<KeyRelease>', update_listbox)

    # Populate the listbox initially with all menu items
    update_listbox()

    menu_page.mainloop()


# Function to add or update a menu item in the database
def add_update_menu_item(item_number_entry, item_name_entry, price_entries, menu_page, menu_type):
    item_number = int(item_number_entry.get())
    item_name = item_name_entry.get()
    prices = [float(entry.get()) for entry in price_entries]

    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()
    
    if menu_type == "Pizza" or menu_type == "Side":
        # Check if the item already exists in the corresponding menu
        cur.execute(f'SELECT * FROM {"menu" if menu_type == "Pizza" else "side_order"} WHERE item_number = ?', (item_number,))
        item = cur.fetchone()
        
        if item:
            # Update the existing menu item
            cur.execute(f'''
                UPDATE {"menu" if menu_type == "Pizza" else "side_order"}
                SET item_name = ?, price_s = ?, price_m = ?, price_l = ?
                WHERE item_number = ?
            ''', (item_name, prices[0], prices[1], prices[2], item_number))
        else:
            # Insert a new menu item
            cur.execute(f'''
                INSERT INTO {"menu" if menu_type == "Pizza" else "side_order"} (item_number, item_name, price_s, price_m, price_l)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_number, item_name, prices[0], prices[1], prices[2]))

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"{menu_type} item added/updated successfully!")
    menu_page.destroy()
    open_menu_page(menu_type)

def search_menu_items(search_term, menu_type):
    conn = sqlite3.connect('customer_info.db')
    cur = conn.cursor()
    
    if menu_type == "Pizza":
        cur.execute('''
            SELECT item_number, item_name, price_s, price_m, price_l FROM menu WHERE item_name LIKE ?
        ''', (f'%{search_term}%',))
    else:
        cur.execute('''
            SELECT item_number, item_name, price_s, price_m, price_l FROM side_order WHERE item_name LIKE ?
        ''', (f'%{search_term}%',))
    
    items = cur.fetchall()
    conn.close()
    return items

# Main application window (main page)
root = tk.Tk()
root.title("Pizza Cashiering System - Main Page")
root.geometry("600x600")

# Main page components
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

work_button = ttk.Button(frame, text="Work", command=open_work_page)
work_button.grid(row=1, column=0, pady=10)

customer_button = ttk.Button(frame, text="Customer Management")
customer_button.grid(row=2, column=0, pady=10)

edit_pizza_button = ttk.Button(frame, text="Edit Pizza Menu", command=lambda: open_menu_page("Pizza"))
edit_pizza_button.grid(row=3, column=0, pady=10)

edit_side_button = ttk.Button(frame, text="Edit Side Menu", command=lambda: open_menu_page("Side"))
edit_side_button.grid(row=4, column=0, pady=10)

# Initialize the database
init_db()

root.mainloop()
