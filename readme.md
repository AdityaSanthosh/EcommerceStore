# E-commerce Store API

This repository contains the backend API for a simple e-commerce store, built using Django and Django Rest Framework.

## Features

* **Product Management:** Define and manage products (items) with prices and discounts.
* **User Carts:** Users can add items to their carts, apply discounts, and checkout.
* **Order Processing:** Orders are created upon successful checkout, tracking payment and discount details.
* **Discount System:** Apply discounts to carts using discount codes.
* **Admin Analytics:** Provides insights into order statistics, including total sales and discount usage.

## Models

* `Item`: Represents a product.
* `Cart`: User's shopping cart.
* `CartItem`: Items within a cart.
* `Order`: Completed order.
* `OrderItem`: Items within an order.

## API Endpoints

* `/cart/`: *GET* user's cart.
* `/cart/items/`: *PUT* items to the cart.
* `/cart/checkout/discount/`: Check and apply(*PUT*) discounts.
* `/cart/checkout/payment/`: Process payment and create(*PUT*) an order.
* `/admin/discount/`: Admin endpoint to check(*GET*) discount availability.
* `/admin/analytics/`: Admin endpoint to get(*GET*) order analytics.

## Setup

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

## Usage

* Use an API client (e.g., Postman, Insomnia) to [interact](https://drive.google.com/file/d/1AaNXsGGJt4iHsvQEMETHF8lj34tgie5j/view?usp=drive_link) with the API endpoints.
* Set the `HTTP_USER_ID` header in your requests to identify the user.