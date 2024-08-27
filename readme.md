# Pizza Cashiering System

## Overview

The Pizza Cashiering System is a Python-based desktop application designed to help manage customer orders for a pizza house. The system allows the on-caller to manage customer information, take orders, calculate delivery fees, and generate receipts. The application is built using `Tkinter` for the GUI and `SQLite` for the database.

## Features

### Main Page
- **Work**: Opens the work page where the on-caller can search for customers by phone number and proceed to take an order.
- **Customer Management**: `Work in progress`
- **Edit Pizza Menu**: Opens the pizza management page where the user can add, update, and search for pizza menu items.
- **Edit Side Menu**: Opens the side menu management page where the user can add, update, and search for side order items.

### Work Page
- **Customer Search**: Allows the on-caller to search for a customer by phone number. If the customer is found, the order detail page opens with the customer's information pre-filled. If the customer is not found, a new order detail page is opened with the phone number pre-filled.

### Order Detail Page
- **Customer Information**: Displays fields for entering customer name, address, and phone number.
- **Pizza Order**: Allows the user to input the pizza number and select the size (S, M, L). The selected pizza is added to the order notes with its price.
- **Side Orders**: Includes a search bar, size buttons (S, M, L) and listbox for selecting side orders. Selected side orders and their size are added to the order notes.
- **Delivery Fee**: Automatically fetched from the database based on the customer's phone number.
- **Order Notes**: Displays all added items (pizza and sides) along with their prices. 
- **Finish Order**: Calculates the subtotal and tax for the order and appends it to the order notes. Generate the receipt-like txt file prepare for printing.
- **Submit Order**: Saves the customer information to the database and finalizes the order. Generate a txt file receipt into `receipts` folder.

### Menu Management Pages
- **Add/Update Items**: Allows users to add or update items in the pizza or side menu. Each item includes an item number, name, and prices for small, medium, and large sizes.
- **Search Functionality**: Users can search for menu items by name, and the results are displayed in a listbox.

## Database

The application uses an `SQLite` database (`customer_info.db`) to store:
- **Customers**: Stores customer name, address, phone number, and delivery fee.
- **Menu**: Stores pizza items with item number, name, and prices for small, medium, and large sizes.
- **Side Orders**: Stores side order items similarly to the pizza menu.

## Requirements

- Python 3.x
- Tkinter (included within Python)
- SQLite3 (included within Python)

## How to Run

1. Clone the repository or download the source files.
2. Run `chicago_pizza.py` using Python 3.
   ```bash
   python chicago_pizza.py