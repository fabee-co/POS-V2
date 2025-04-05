# -*- coding: utf-8 -*-
# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class QFInventoryTransaction(Document):
    def validate(self):
        # Validate transaction date
        if not self.transaction_date:
            self.transaction_date = datetime.now()
        
        # Validate quantity
        if self.quantity <= 0:
            frappe.throw("Transaction quantity must be greater than zero")
        
        # Validate batch exists
        batch = frappe.get_doc("QF Inventory Batch", self.batch_id)
        if not batch:
            frappe.throw(f"Batch {self.batch_id} does not exist")
        
        # Validate outward transactions have sufficient stock
        if self.transaction_type in ["Outward", "Transfer", "Wastage"]:
            if batch.quantity < self.quantity:
                frappe.throw(f"Insufficient stock in batch {self.batch_id}. Available: {batch.quantity}, Required: {self.quantity}")
    
    def on_submit(self):
        # Update inventory batch quantity
        self.update_batch_quantity()
    
    def update_batch_quantity(self):
        """Update the quantity in the inventory batch based on transaction type"""
        batch = frappe.get_doc("QF Inventory Batch", self.batch_id)
        
        if self.transaction_type == "Inward":
            # Add to inventory
            batch.quantity += self.quantity
            
        elif self.transaction_type in ["Outward", "Transfer", "Wastage", "Expiry"]:
            # Remove from inventory
            batch.quantity -= self.quantity
            
            # Update batch status if needed
            if batch.quantity <= 0:
                batch.batch_status = "Depleted"
            elif batch.quantity <= 5:  # Low stock threshold
                batch.batch_status = "Low Stock"
                
        elif self.transaction_type == "Adjustment":
            # Direct adjustment (could be positive or negative)
            batch.quantity = max(0, batch.quantity + self.quantity)
            
            # Update batch status if needed
            if batch.quantity <= 0:
                batch.batch_status = "Depleted"
            elif batch.quantity <= 5:  # Low stock threshold
                batch.batch_status = "Low Stock"
            else:
                batch.batch_status = "Active"
        
        # Save the updated batch
        batch.save()
