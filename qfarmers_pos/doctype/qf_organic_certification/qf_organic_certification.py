# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OrganicCertification(Document):
    def validate(self):
        self.validate_dates()
        
    def validate_dates(self):
        if self.valid_from and self.valid_till:
            if self.valid_from > self.valid_till:
                frappe.throw("Valid From date cannot be after Valid Till date")
                
    def before_save(self):
        # Auto-update is_active based on current date
        today = frappe.utils.today()
        if self.valid_from and self.valid_till:
            self.is_active = 1 if self.valid_from <= today <= self.valid_till else 0
