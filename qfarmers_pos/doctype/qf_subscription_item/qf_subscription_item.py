# -*- coding: utf-8 -*-
# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class QFSubscriptionItem(Document):
    def validate(self):
        # Calculate amount based on quantity and price
        self.amount = self.quantity * self.price
        
    def before_save(self):
        # Fetch current price if not specified
        if not self.price and self.item_code:
            self.price = frappe.db.get_value("Item", self.item_code, "standard_rate") or 0
            self.amount = self.quantity * self.price
