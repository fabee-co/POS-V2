# -*- coding: utf-8 -*-
# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class QFRecommendedProduct(Document):
    def validate(self):
        # Ensure relevance score is within valid range (0-100)
        if self.relevance_score < 0:
            self.relevance_score = 0
        elif self.relevance_score > 100:
            self.relevance_score = 100
            
        # Ensure product exists
        if not frappe.db.exists("Item", self.product):
            frappe.throw(f"Product {self.product} does not exist")
            
        # Fetch product name if not already set
        if not self.product_name and self.product:
            self.product_name = frappe.db.get_value("Item", self.product, "item_name")
            
        # Ensure recommendation reason is provided
        if not self.recommendation_reason:
            self.recommendation_reason = "Recommended based on purchase history"
