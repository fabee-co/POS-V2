# -*- coding: utf-8 -*-
# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class QFOnlineOrderItem(Document):
    def validate(self):
        # Calculate amount based on quantity and price
        self.amount = self.quantity * self.price
        
        # Fetch current price if not specified
        if not self.price and self.item_code:
            self.price = frappe.db.get_value("Item", self.item_code, "standard_rate") or 0
            self.amount = self.quantity * self.price
            
        # Check if item is organic
        if self.item_code:
            # This would typically check a custom field on the Item DocType
            # For now, we'll assume it's not organic unless specified
            if not self.is_organic:
                # Check if this item has any organic batches
                organic_batch = frappe.db.exists("QF Inventory Batch", {
                    "item_code": self.item_code,
                    "is_organic": 1,
                    "quantity": [">", 0]
                })
                
                if organic_batch:
                    self.is_organic = 1
