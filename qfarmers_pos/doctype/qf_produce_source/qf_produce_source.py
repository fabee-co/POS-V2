# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ProduceSource(Document):
    def validate(self):
        self.validate_seasonal_availability()
        self.validate_certifications()
        
    def validate_seasonal_availability(self):
        # Validate seasonal availability months
        if self.available_from_month and self.available_to_month:
            months = ["January", "February", "March", "April", "May", "June", 
                     "July", "August", "September", "October", "November", "December"]
            
            from_index = months.index(self.available_from_month)
            to_index = months.index(self.available_to_month)
            
            # Handle cases where availability spans across year end
            if from_index > to_index and to_index != 0:
                frappe.msgprint("Note: Availability period spans across year end.")
    
    def validate_certifications(self):
        # Update organic_certified flag based on certification details
        if self.certification_details and len(self.certification_details) > 0:
            self.organic_certified = 1
        else:
            # Only reset if there are no certifications
            if self.organic_certified:
                if not self.certification_details or len(self.certification_details) == 0:
                    self.organic_certified = 0
                    
    def before_save(self):
        # Auto-calculate distance from store if not provided
        if not self.distance_from_store and self.city and self.city.lower() == "chennai":
            # Default distance for local Chennai suppliers if not specified
            self.distance_from_store = 15.0
