# E-commerce Store API

This repository contains the backend API for a simple e-commerce store, built using Django and Django Rest Framework.

##### Product Flow
1. Checkout the cart which freezes the prices for 10 mins
2. Get total price which calculates cart value with frozen prices after checkout
3. Place order considering checked out prices
4. Proceed with payment which means order is placed and payment is attached to it later


#### Models

* `Item`: Represents a product.
* `Cart`: User's shopping cart.
* `CartItem`: Items within a cart.
* `Order`: Completed order.
* `OrderItem`: Items within an order.


#### Setup

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS and Linux
    venv\Scripts\activate  # On Windows
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run migrations:
    ```bash
    python manage.py migrate
    ```
5.  Start the development server:
    ```bash
    python manage.py runserver
    ```

#### Usage

* Use an API client (e.g., Postman, Insomnia) to [interact](https://drive.google.com/file/d/1AaNXsGGJt4iHsvQEMETHF8lj34tgie5j/view?usp=drive_link) with the API endpoints.
* Set the `HTTP_USER_ID` header in your requests to identify the user.