# QFarmers POS System

A custom Point of Sale (POS) application for QFarmers organic produce and grocery store in Chennai, built on Frappe/ERPNext.

## Features

- **POS Interface**: User-friendly interface for in-store sales
- **Organic Inventory Management**: Track inventory with organic certification details
- **Online Store**: E-commerce functionality for online sales
- **Subscription Management**: Manage recurring customer subscriptions
- **AI Recommendations**: Generate product recommendations based on customer preferences

## Installation

1. Install Frappe Bench and ERPNext v15 following the [official documentation](https://frappeframework.com/docs/v14/user/en/installation)

2. Navigate to your bench directory:
   ```
   cd frappe-bench
   ```

3. Get the QFarmers POS app:
   ```
   bench get-app qfarmers_pos https://github.com/qfarmers/qfarmers_pos
   ```
   
   Or install from the zip file:
   ```
   bench get-app qfarmers_pos /path/to/qfarmers_pos.zip
   ```

4. Install the app on your site:
   ```
   bench --site your-site install-app qfarmers_pos
   ```

5. Run migrations to create the database tables:
   ```
   bench --site your-site migrate
   ```

6. Build assets and restart:
   ```
   bench build
   bench restart
   ```

## Usage

### POS Interface
- Access the POS interface at: `/app/qfarmers-pos`

### Online Store
- Access the online store at: `/shop`
- Product details: `/shop/product/:product`
- Category browsing: `/shop/category/:category`
- Shopping cart: `/shop/cart`
- Checkout: `/shop/checkout`

### DocTypes
All DocTypes use the "qf_" prefix to avoid conflicts with standard ERPNext DocTypes:

- QF Inventory Batch
- QF Inventory Transaction
- QF Online Order
- QF Online Order Item
- QF Organic Certification
- QF Produce Source
- QF Recommended Product
- QF Subscription
- QF Subscription Item
- QF AI Recommendation

## Development

### Directory Structure
```
qfarmers_pos/
├── qfarmers_pos/
│   ├── doctype/
│   │   ├── qf_ai_recommendation/
│   │   ├── qf_inventory_batch/
│   │   ├── qf_inventory_transaction/
│   │   ├── qf_online_order/
│   │   ├── qf_online_order_item/
│   │   ├── qf_organic_certification/
│   │   ├── qf_produce_source/
│   │   ├── qf_recommended_product/
│   │   ├── qf_subscription/
│   │   └── qf_subscription_item/
│   ├── page/
│   │   └── qfarmers_pos/
│   ├── public/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── utils/
│   │   ├── ai_recommendation.py
│   │   ├── inventory_management.py
│   │   └── subscription_management.py
│   └── www/
│       ├── cart/
│       ├── checkout/
│       ├── product/
│       └── shop/
├── setup.py
├── MANIFEST.in
├── license.txt
└── requirements.txt
```

### Scheduler Tasks
The application includes the following scheduled tasks:

- Hourly: Check for expiring inventory
- Daily: Update inventory freshness and process subscriptions
- Weekly: Generate AI recommendations

## License
This project is licensed under the MIT License - see the license.txt file for details.
