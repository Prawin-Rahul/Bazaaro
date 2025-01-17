## Learnings

### SQLite v/s MYSql

### Idempotency

### Payment Gateway Integration

### Docker

Users Table
This table will store information about both customers and product owners.

Column Data Type Description
id INT Primary key, auto-incremented user ID
username VARCHAR Unique username
email VARCHAR Unique email address
password_hash VARCHAR Hashed password (ensure proper encryption)
role ENUM Enum field: 'customer', 'admin'
created_at DATETIME Timestamp of account creation
updated_at DATETIME Timestamp of last profile update

Relationships:

Product Owners: The role field will differentiate between product owners and customers. Product owners can add products, manage inventory, etc.

Products Table
This table stores details about the products that product owners add.

Column Data Type Description
id INT Primary key, auto-incremented product ID
owner_id INT Foreign key referencing Users(id) (product owner)
name VARCHAR Product name
description TEXT Product description
price DECIMAL Product price
category VARCHAR Product category (e.g., electronics, clothing)
stock_quantity INT Available stock for the product
image_url VARCHAR URL to product image
created_at DATETIME Timestamp when the product was added
updated_at DATETIME Timestamp of last product update

Relationships:

One-to-Many: One product owner can add multiple products.
Foreign Key: The owner_id links to the Users(id) to associate each product with a product owner.
Orders Table
This table will store order-level information for

######### customer purchases.

Column Data Type Description
id INT Primary key, auto-incremented order ID
user_id INT Foreign key referencing Users(id) (customer)
total_price DECIMAL Total price for the order
status ENUM Enum: 'pending', 'processing', 'shipped', 'completed', 'cancelled'
created_at DATETIME Timestamp of order creation
updated_at DATETIME Timestamp of last status update
Relationships:

One-to-Many: One customer can place multiple orders.
Foreign Key: The user_id field links the order to a customer.
Order Items Table
Each order can contain multiple products. This table will store the details of the items in each

####### order.

Column Data Type Description
id INT Primary key, auto-incremented item ID
order_id INT Foreign key referencing Orders(id)
product_id INT Foreign key referencing Products(id)
quantity INT Quantity of the product in the order
price DECIMAL Price of the product at the time of purchase
Relationships:

Many-to-One: Each order item is linked to one order and one product.
Foreign Keys: order_id links to Orders(id), and product_id links to Products(id).

############## Inventory Table
The inventory table tracks the stock levels for products.

Column DataType Description
id INT Primary key, auto-incremented inventory record ID
product_id INT Foreign key referencing Products(id)
quantity_in_stock INT Current stock level of the product
updated_at DATETIME Timestamp when stock was last updated

Relationships:
One-to-One: Each product has a single inventory record.
Foreign Key: The product_id links to Products(id).

############ Payments Table
This table stores information related to customer payments for their orders.

Column Data Type Description
id INT Primary key, auto-incremented payment ID
order_id INT Foreign key referencing Orders(id)
payment_status ENUM Enum: 'pending', 'completed', 'failed'
amount DECIMAL Amount paid by the customer
payment_method ENUM Enum: 'credit_card', 'paypal', 'stripe', etc.
payment_date DATETIME Timestamp when the payment was made

############ Relationships:

One-to-One: Each order corresponds to one payment.
Foreign Key: order_id links to Orders(id).
Reviews Table
Customers can leave reviews and ratings for products.

Column Data Type Description
id INT Primary key, auto-incremented review ID
product_id INT Foreign key referencing Products(id)
user_id INT Foreign key referencing Users(id) (customer)
rating INT Rating score (e.g., 1-5 stars)
comment TEXT Review comment written by the customer
created_at DATETIME Timestamp of when the review was posted
Relationships:

One-to-Many: One product can have multiple reviews.
Foreign Keys: product_id links to Products(id), and user_id links to Users(id). 3. Schema Diagram
The relationships between the tables can be represented as:

scss
Copy code
Users (id) <--- (order_id) ---> Orders (id)
| |
| v
| Order Items (id)
| |
| v
| Products (id) ---> Inventory (id)
| |
| v
| Reviews (id)
|
v
Payments (id)
One-to-many: One product owner can have many products, and one customer can place many orders.
Many-to-many: Customers can buy multiple products, and products can appear in multiple orders (handled by the Order Items table).
One-to-one: Each order corresponds to one payment and each product corresponds to one inventory record.
