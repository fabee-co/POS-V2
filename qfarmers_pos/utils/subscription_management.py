import frappe
import datetime
from frappe.utils import nowdate, add_days, getdate

def process_daily_subscriptions():
    """
    Daily processing of active subscriptions
    Creates orders for subscriptions due today
    """
    # Get all active subscriptions due for processing today
    subscriptions = frappe.get_all(
        "QF Subscription",
        filters={
            "status": "Active",
            "next_delivery_date": nowdate()
        },
        fields=["name", "customer", "delivery_address", "delivery_time_slot", "total_amount"]
    )
    
    for subscription in subscriptions:
        # Create online order from subscription
        create_order_from_subscription(subscription.name)
        
        # Update next delivery date based on frequency
        update_next_delivery_date(subscription.name)

def create_order_from_subscription(subscription_id):
    """
    Create an online order from subscription
    
    Args:
        subscription_id (str): ID of the subscription
    """
    subscription = frappe.get_doc("QF Subscription", subscription_id)
    
    # Create new online order
    order = frappe.new_doc("QF Online Order")
    order.customer = subscription.customer
    order.delivery_address = subscription.delivery_address
    order.delivery_date = nowdate()
    order.delivery_time_slot = subscription.delivery_time_slot
    order.payment_method = subscription.payment_method
    order.payment_status = "Pending"
    
    # Add subscription items to order
    for item in subscription.items:
        order.append("order_items", {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "quantity": item.quantity,
            "uom": item.uom,
            "price": item.price,
            "amount": item.quantity * item.price,
            "is_organic": item.is_organic,
            "notes": f"From subscription {subscription.name}"
        })
    
    # Apply subscription discount if applicable
    if subscription.discount_percentage > 0:
        order.discount_percentage = subscription.discount_percentage
        order.discount_amount = (order.total_amount * subscription.discount_percentage) / 100
        order.total_amount = order.total_amount - order.discount_amount
    
    # Set order status to Processing for subscription orders
    order.status = "Processing"
    
    # Save the order
    order.insert()
    
    # Log subscription order creation
    frappe.log_error(
        f"Created order {order.name} from subscription {subscription.name} for customer {subscription.customer}",
        "Subscription Order Created"
    )
    
    return order.name

def update_next_delivery_date(subscription_id):
    """
    Update the next delivery date based on frequency
    
    Args:
        subscription_id (str): ID of the subscription
    """
    subscription = frappe.get_doc("QF Subscription", subscription_id)
    
    # Calculate next delivery date based on frequency
    days_to_add = 0
    if subscription.frequency == "Daily":
        days_to_add = 1
    elif subscription.frequency == "Weekly":
        days_to_add = 7
    elif subscription.frequency == "Bi-Weekly":
        days_to_add = 14
    elif subscription.frequency == "Monthly":
        days_to_add = 30
    
    # Update next delivery date
    next_date = add_days(subscription.next_delivery_date, days_to_add)
    
    # Check if next date is within subscription end date
    if subscription.end_date and getdate(next_date) > getdate(subscription.end_date):
        # Subscription has reached its end date
        frappe.db.set_value("QF Subscription", subscription_id, "status", "Completed")
    else:
        # Update next delivery date
        frappe.db.set_value("QF Subscription", subscription_id, "next_delivery_date", next_date)
        
        # Update delivery count
        frappe.db.set_value(
            "QF Subscription", 
            subscription_id, 
            "deliveries_completed", 
            subscription.deliveries_completed + 1
        )

def pause_subscription(subscription_id, pause_until=None):
    """
    Pause an active subscription
    
    Args:
        subscription_id (str): ID of the subscription
        pause_until (str, optional): Date until which subscription is paused
    """
    subscription = frappe.get_doc("QF Subscription", subscription_id)
    
    if subscription.status != "Active":
        frappe.throw(f"Cannot pause subscription {subscription_id} as it is not active")
    
    # Update subscription status
    frappe.db.set_value("QF Subscription", subscription_id, "status", "Paused")
    
    if pause_until:
        frappe.db.set_value("QF Subscription", subscription_id, "pause_until", pause_until)
    
    # Log subscription pause
    frappe.log_error(
        f"Subscription {subscription_id} paused until {pause_until or 'indefinitely'} for customer {subscription.customer}",
        "Subscription Paused"
    )

def resume_subscription(subscription_id):
    """
    Resume a paused subscription
    
    Args:
        subscription_id (str): ID of the subscription
    """
    subscription = frappe.get_doc("QF Subscription", subscription_id)
    
    if subscription.status != "Paused":
        frappe.throw(f"Cannot resume subscription {subscription_id} as it is not paused")
    
    # Update subscription status
    frappe.db.set_value("QF Subscription", subscription_id, "status", "Active")
    
    # Calculate next delivery date
    next_date = add_days(nowdate(), 1)  # Start from tomorrow
    
    # Update next delivery date
    frappe.db.set_value("QF Subscription", subscription_id, "next_delivery_date", next_date)
    
    # Clear pause until date
    frappe.db.set_value("QF Subscription", subscription_id, "pause_until", None)
    
    # Log subscription resume
    frappe.log_error(
        f"Subscription {subscription_id} resumed for customer {subscription.customer}",
        "Subscription Resumed"
    )

def check_paused_subscriptions():
    """Check paused subscriptions that are due to resume"""
    # Get all paused subscriptions with a pause_until date
    subscriptions = frappe.get_all(
        "QF Subscription",
        filters={
            "status": "Paused",
            "pause_until": ["<=", nowdate()]
        },
        fields=["name"]
    )
    
    for subscription in subscriptions:
        resume_subscription(subscription.name)
