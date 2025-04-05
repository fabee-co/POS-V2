import frappe
import datetime
from frappe.utils import nowdate, add_days, getdate

def check_expiring_inventory():
    """
    Hourly check for inventory items approaching expiration
    Sends notifications and updates batch status
    """
    # Get all active inventory batches
    batches = frappe.get_all(
        "QF Inventory Batch",
        filters={
            "batch_status": ["in", ["Active", "Low Stock"]],
            "expiry_date": ["<=", add_days(nowdate(), 3)],  # Expiring within 3 days
            "quantity": [">", 0]
        },
        fields=["name", "item_code", "item_name", "quantity", "expiry_date", "harvest_date"]
    )
    
    for batch in batches:
        # Calculate days until expiry
        days_to_expiry = (getdate(batch.expiry_date) - getdate(nowdate())).days
        
        # Update batch status
        if days_to_expiry <= 1:
            frappe.db.set_value("QF Inventory Batch", batch.name, "batch_status", "Expiring Soon")
            
            # Create notification for store manager
            frappe.publish_realtime(
                event="eval_js",
                message=f'frappe.show_alert({{message: "Batch {batch.name} for {batch.item_name} expires tomorrow!", indicator: "red"}}, 15);',
                user="Administrator"
            )
            
            # Apply automatic discount pricing
            apply_expiry_discount(batch.name, 50)  # 50% discount for items expiring tomorrow
        
        elif days_to_expiry <= 3:
            # Apply smaller discount for items expiring soon
            apply_expiry_discount(batch.name, 25)  # 25% discount for items expiring within 3 days

def update_inventory_freshness():
    """
    Daily update of inventory freshness indicators
    Updates freshness status based on harvest date and shelf life
    """
    # Get all active inventory batches
    batches = frappe.get_all(
        "QF Inventory Batch",
        filters={
            "batch_status": ["in", ["Active", "Low Stock", "Expiring Soon"]],
            "quantity": [">", 0]
        },
        fields=["name", "item_code", "harvest_date", "expiry_date", "shelf_life_days"]
    )
    
    for batch in batches:
        # Calculate elapsed time since harvest
        if batch.harvest_date:
            days_since_harvest = (getdate(nowdate()) - getdate(batch.harvest_date)).days
            
            # Calculate freshness percentage
            if batch.shelf_life_days:
                freshness = max(0, 100 - (days_since_harvest / batch.shelf_life_days * 100))
                
                # Update freshness indicator
                frappe.db.set_value("QF Inventory Batch", batch.name, "freshness_indicator", freshness)
                
                # Update freshness level
                if freshness >= 75:
                    freshness_level = "Fresh"
                elif freshness >= 50:
                    freshness_level = "Good"
                elif freshness >= 25:
                    freshness_level = "Fair"
                else:
                    freshness_level = "Poor"
                    
                frappe.db.set_value("QF Inventory Batch", batch.name, "freshness_level", freshness_level)
        
        # Check for expired items
        if batch.expiry_date and getdate(batch.expiry_date) <= getdate(nowdate()):
            # Mark as expired
            frappe.db.set_value("QF Inventory Batch", batch.name, "batch_status", "Expired")
            
            # Create wastage record
            if batch.quantity > 0:
                create_wastage_record(batch.name, batch.quantity, "Expired")

def create_inventory_transaction(batch_id, transaction_type, quantity, reference_type=None, reference_id=None):
    """
    Create inventory transaction record
    
    Args:
        batch_id (str): ID of the inventory batch
        transaction_type (str): Type of transaction (Inward, Outward, Adjustment, Transfer, Wastage)
        quantity (float): Quantity to transact
        reference_type (str, optional): Reference document type
        reference_id (str, optional): Reference document ID
    """
    # Get batch details
    batch = frappe.get_doc("QF Inventory Batch", batch_id)
    
    # Create transaction
    transaction = frappe.new_doc("QF Inventory Transaction")
    transaction.batch_id = batch_id
    transaction.item_code = batch.item_code
    transaction.transaction_type = transaction_type
    transaction.quantity = quantity
    transaction.transaction_date = nowdate()
    
    if reference_type:
        transaction.reference_type = reference_type
    
    if reference_id:
        transaction.reference_id = reference_id
    
    transaction.insert()
    
    # Update batch quantity
    new_quantity = batch.quantity
    if transaction_type == "Inward":
        new_quantity += quantity
    elif transaction_type in ["Outward", "Wastage"]:
        new_quantity -= quantity
    elif transaction_type == "Adjustment":
        new_quantity = quantity
    
    frappe.db.set_value("QF Inventory Batch", batch_id, "quantity", new_quantity)
    
    # Update batch status based on new quantity
    if new_quantity <= 0:
        frappe.db.set_value("QF Inventory Batch", batch_id, "batch_status", "Out of Stock")
    elif new_quantity <= batch.reorder_level:
        frappe.db.set_value("QF Inventory Batch", batch_id, "batch_status", "Low Stock")
    else:
        frappe.db.set_value("QF Inventory Batch", batch_id, "batch_status", "Active")
    
    return transaction.name

def apply_expiry_discount(batch_id, discount_percentage):
    """Apply discount to items approaching expiry"""
    batch = frappe.get_doc("QF Inventory Batch", batch_id)
    
    # Calculate discounted price
    standard_rate = frappe.db.get_value("Item", batch.item_code, "standard_rate") or 0
    discounted_rate = standard_rate * (1 - (discount_percentage / 100))
    
    # Update batch with discount information
    frappe.db.set_value("QF Inventory Batch", batch_id, {
        "discount_percentage": discount_percentage,
        "discounted_rate": discounted_rate,
        "is_discounted": 1
    })
    
    # Log the discount application
    frappe.log_error(
        f"Applied {discount_percentage}% discount to batch {batch_id} for {batch.item_name} due to approaching expiry",
        "Expiry Discount Applied"
    )

def create_wastage_record(batch_id, quantity, reason):
    """Create wastage record for expired or damaged inventory"""
    # Create inventory transaction of type Wastage
    transaction_id = create_inventory_transaction(
        batch_id=batch_id,
        transaction_type="Wastage",
        quantity=quantity
    )
    
    # Add wastage reason to the transaction
    frappe.db.set_value("QF Inventory Transaction", transaction_id, "notes", f"Wastage reason: {reason}")
    
    # Log wastage for reporting
    batch = frappe.get_doc("QF Inventory Batch", batch_id)
    frappe.log_error(
        f"Wastage recorded for batch {batch_id} ({batch.item_name}): {quantity} {batch.uom} - Reason: {reason}",
        "Inventory Wastage"
    )
