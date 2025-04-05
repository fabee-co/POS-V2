# -*- coding: utf-8 -*-
# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class QFOnlineOrder(Document):
    def validate(self):
        # Auto-generate order ID if not provided
        if not self.order_id:
            customer_code = self.customer[:3].upper()
            date_code = datetime.now().strftime("%Y%m%d")
            count = frappe.db.count("QF Online Order", {"order_date": [">=", datetime.now().date()]})
            self.order_id = f"ORD-{customer_code}-{date_code}-{count+1:03d}"
        
        # Validate order items
        if not self.order_items or len(self.order_items) == 0:
            frappe.throw("Order must have at least one item")
        
        # Calculate total amount
        total = 0
        for item in self.order_items:
            total += item.quantity * item.price
        
        self.total_amount = total
        
        # Validate delivery date
        if self.delivery_date:
            today = datetime.now().date()
            if self.delivery_date < today:
                frappe.throw("Delivery date cannot be in the past")
    
    def on_update(self):
        # Update inventory when order status changes
        if self.status in ["Processing", "Packed", "Shipped", "Delivered"]:
            self.update_inventory()
    
    def update_inventory(self):
        """Update inventory when order is confirmed"""
        # Only deduct inventory once when status changes to Processing
        if self.status == "Processing" and frappe.db.get_value("QF Online Order", self.name, "status") != "Processing":
            from qfarmers_pos.qfarmers_pos.utils.inventory_management import create_inventory_transaction
            
            for item in self.order_items:
                # Find appropriate batch for this item (FIFO)
                batch = frappe.get_list(
                    "QF Inventory Batch",
                    filters={
                        "item_code": item.item_code,
                        "quantity": [">", 0],
                        "batch_status": ["!=", "Expired"]
                    },
                    order_by="harvest_date asc",
                    limit=1
                )
                
                if batch and len(batch) > 0:
                    # Create inventory transaction
                    create_inventory_transaction(
                        batch_id=batch[0].name,
                        transaction_type="Outward",
                        quantity=item.quantity,
                        reference_type="QF Online Order",
                        reference_id=self.name
                    )
                else:
                    frappe.log_error(f"No valid batch found for item {item.item_code} in order {self.name}", "Inventory Error")
