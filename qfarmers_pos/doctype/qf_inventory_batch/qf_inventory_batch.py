# -*- coding: utf-8 -*-
# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class QFInventoryBatch(Document):
    def validate(self):
        # Calculate shelf life days if not specified
        if self.harvest_date and self.expiry_date and not self.shelf_life_days:
            delta = self.expiry_date - self.harvest_date
            self.shelf_life_days = delta.days
        
        # Validate dates
        if self.harvest_date and self.expiry_date:
            if self.expiry_date < self.harvest_date:
                frappe.throw("Expiry date cannot be before harvest date")
        
        # Set freshness indicator based on remaining shelf life
        if self.expiry_date:
            today = datetime.now().date()
            if self.expiry_date < today:
                self.batch_status = "Expired"
                self.freshness_indicator = "Low"
            else:
                days_until_expiry = (self.expiry_date - today).days
                
                if self.shelf_life_days:
                    if days_until_expiry > self.shelf_life_days * 0.7:
                        self.freshness_indicator = "High"
                    elif days_until_expiry > self.shelf_life_days * 0.3:
                        self.freshness_indicator = "Medium"
                    else:
                        self.freshness_indicator = "Low"
                        self.batch_status = "Expiring Soon"
        
        # Set batch status based on quantity
        if self.quantity <= 0:
            self.batch_status = "Depleted"
        elif self.quantity <= 5:  # Low stock threshold
            self.batch_status = "Low Stock"
    
    def before_save(self):
        # Ensure manufacturing date is set for processed products
        if self.is_processed and not self.manufacturing_date:
            self.manufacturing_date = self.harvest_date
