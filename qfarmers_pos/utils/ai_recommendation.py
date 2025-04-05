import frappe
import pandas as pd
import numpy as np
from frappe.utils import nowdate, add_days, getdate

def generate_weekly_recommendations():
    """
    Weekly generation of AI-powered product recommendations
    Analyzes purchase history and creates personalized recommendations
    """
    # Get all customers with purchase history
    customers = frappe.get_all(
        "Customer",
        filters={
            "disabled": 0
        },
        fields=["name", "customer_name"]
    )
    
    for customer in customers:
        # Generate recommendations for each customer
        generate_customer_recommendations(customer.name)
    
    # Generate seasonal recommendations
    generate_seasonal_recommendations()
    
    # Log recommendation generation
    frappe.log_error(
        f"Generated weekly recommendations for {len(customers)} customers",
        "AI Recommendations Generated"
    )

def generate_customer_recommendations(customer_id):
    """
    Generate personalized recommendations for a specific customer
    
    Args:
        customer_id (str): ID of the customer
    """
    # Get customer's purchase history
    purchase_history = get_customer_purchase_history(customer_id)
    
    if not purchase_history or len(purchase_history) == 0:
        # Not enough purchase history for recommendations
        return
    
    # Clear existing recommendations
    clear_existing_recommendations(customer_id)
    
    # Create recommendation document
    recommendation = frappe.new_doc("QF AI Recommendation")
    recommendation.customer = customer_id
    recommendation.generation_date = nowdate()
    recommendation.recommendation_type = "Personalized"
    
    # Generate recommendations using collaborative filtering
    recommended_items = collaborative_filtering_recommendations(customer_id, purchase_history)
    
    # Add recommended items to document
    for item in recommended_items[:5]:  # Top 5 recommendations
        recommendation.append("recommended_products", {
            "product": item["item_code"],
            "product_name": item["item_name"],
            "relevance_score": item["relevance_score"],
            "recommendation_reason": item["reason"]
        })
    
    # Save recommendation
    recommendation.insert()
    
    return recommendation.name

def generate_seasonal_recommendations():
    """Generate seasonal recommendations based on current season"""
    # Determine current season
    month = int(nowdate().split('-')[1])
    
    if month in [3, 4, 5]:
        season = "Summer"
    elif month in [6, 7, 8]:
        season = "Monsoon"
    elif month in [9, 10, 11]:
        season = "Autumn"
    else:
        season = "Winter"
    
    # Get seasonal produce
    seasonal_items = get_seasonal_items(season)
    
    # Create seasonal recommendation
    recommendation = frappe.new_doc("QF AI Recommendation")
    recommendation.recommendation_type = "Seasonal"
    recommendation.generation_date = nowdate()
    recommendation.season = season
    
    # Add seasonal items to recommendation
    for item in seasonal_items[:10]:  # Top 10 seasonal items
        recommendation.append("recommended_products", {
            "product": item["item_code"],
            "product_name": item["item_name"],
            "relevance_score": 90,  # High relevance for seasonal items
            "recommendation_reason": f"In season during {season}"
        })
    
    # Save recommendation
    recommendation.insert()
    
    return recommendation.name

def get_customer_purchase_history(customer_id):
    """
    Get purchase history for a customer
    
    Args:
        customer_id (str): ID of the customer
        
    Returns:
        list: List of purchased items with frequency
    """
    # Get sales invoices for customer
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "customer": customer_id,
            "docstatus": 1,  # Submitted invoices
            "posting_date": [">=", add_days(nowdate(), -90)]  # Last 90 days
        },
        fields=["name"]
    )
    
    if not invoices:
        return []
    
    # Get items from invoices
    items = []
    for invoice in invoices:
        invoice_items = frappe.get_all(
            "Sales Invoice Item",
            filters={"parent": invoice.name},
            fields=["item_code", "item_name", "qty"]
        )
        items.extend(invoice_items)
    
    # Aggregate items by frequency
    item_freq = {}
    for item in items:
        if item.item_code in item_freq:
            item_freq[item.item_code]["qty"] += item.qty
            item_freq[item.item_code]["count"] += 1
        else:
            item_freq[item.item_code] = {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": item.qty,
                "count": 1
            }
    
    return list(item_freq.values())

def collaborative_filtering_recommendations(customer_id, purchase_history):
    """
    Generate recommendations using collaborative filtering
    
    Args:
        customer_id (str): ID of the customer
        purchase_history (list): Customer's purchase history
        
    Returns:
        list: Recommended items
    """
    # Get purchased item codes
    purchased_items = [item["item_code"] for item in purchase_history]
    
    # Find similar customers who bought the same items
    similar_customers = []
    for item_code in purchased_items:
        customers = frappe.get_all(
            "Sales Invoice Item",
            filters={
                "item_code": item_code,
                "parent": ["in", frappe.get_all("Sales Invoice", filters={"customer": ["!=", customer_id], "docstatus": 1}, pluck="name")]
            },
            fields=["parent"],
            distinct=True
        )
        
        for customer in customers:
            invoice = frappe.get_value("Sales Invoice", customer.parent, "customer")
            if invoice and invoice not in similar_customers:
                similar_customers.append(invoice)
    
    # Get items purchased by similar customers but not by this customer
    recommended_items = []
    for similar_customer in similar_customers:
        similar_history = get_customer_purchase_history(similar_customer)
        
        for item in similar_history:
            if item["item_code"] not in purchased_items and not any(r["item_code"] == item["item_code"] for r in recommended_items):
                # Calculate relevance score based on purchase frequency among similar customers
                relevance_score = min(item["count"] * 20, 100)  # Scale to 0-100
                
                recommended_items.append({
                    "item_code": item["item_code"],
                    "item_name": item["item_name"],
                    "relevance_score": relevance_score,
                    "reason": "Customers who bought similar items also bought this"
                })
    
    # Sort by relevance score
    recommended_items.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return recommended_items

def get_seasonal_items(season):
    """
    Get items that are in season
    
    Args:
        season (str): Current season
        
    Returns:
        list: Seasonal items
    """
    # Get items with seasonal availability
    items = frappe.get_all(
        "Item",
        filters={
            f"seasonal_availability_{season.lower()}": 1  # Custom field for seasonal availability
        },
        fields=["item_code", "item_name"]
    )
    
    # If custom field doesn't exist or no items found, use a fallback approach
    if not items:
        # Get organic produce items
        all_items = frappe.get_all(
            "Item",
            filters={
                "item_group": ["in", ["Vegetables", "Fruits"]]
            },
            fields=["item_code", "item_name"]
        )
        
        # Simulate seasonal availability
        items = []
        seasonal_mapping = {
            "Summer": ["Mango", "Watermelon", "Cucumber", "Tomato", "Okra"],
            "Monsoon": ["Spinach", "Mushroom", "Corn", "Green Chilli", "Bitter Gourd"],
            "Autumn": ["Apple", "Carrot", "Cauliflower", "Pumpkin", "Sweet Potato"],
            "Winter": ["Orange", "Radish", "Cabbage", "Peas", "Broccoli"]
        }
        
        seasonal_keywords = seasonal_mapping.get(season, [])
        
        for item in all_items:
            for keyword in seasonal_keywords:
                if keyword.lower() in item.item_name.lower():
                    items.append(item)
                    break
    
    # Convert to required format
    result = []
    for item in items:
        result.append({
            "item_code": item.item_code,
            "item_name": item.item_name
        })
    
    return result

def clear_existing_recommendations(customer_id):
    """
    Clear existing recommendations for a customer
    
    Args:
        customer_id (str): ID of the customer
    """
    # Get existing recommendations
    recommendations = frappe.get_all(
        "QF AI Recommendation",
        filters={
            "customer": customer_id,
            "recommendation_type": "Personalized",
            "generation_date": ["<", nowdate()]
        }
    )
    
    # Delete old recommendations
    for recommendation in recommendations:
        frappe.delete_doc("QF AI Recommendation", recommendation.name)
