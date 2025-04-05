# -*- coding: utf-8 -*-
# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class QFSubscription(Document):
    def validate(self):
        # Validate subscription dates
        if self.start_date and self.next_delivery_date:
            if self.next_delivery_date < self.start_date:
                frappe.throw("Next delivery date cannot be before start date")
        
        # Validate subscription items
        if not self.subscription_items or len(self.subscription_items) == 0:
            frappe.throw("Subscription must have at least one item")
    
    def before_save(self):
        # Calculate total amount
        total = 0
        for item in self.subscription_items:
            total += item.quantity * item.price
        
        self.price = total
    
    def on_update(self):
        # Update inventory planning based on subscription
        self.update_inventory_planning()
    
    def update_inventory_planning(self):
        """Update inventory planning based on active subscriptions"""
        if self.status == "Active":
            # Logic to update inventory planning for subscription items
            from qfarmers_pos.qfarmers_pos.utils.subscription_management import update_inventory_for_subscription
            
            # Get all items in this subscription
            for item in self.subscription_items:
                # We don't actually deduct inventory here, just plan for it
                # This will be handled by the daily subscription processing
                pass
