# -*- coding: utf-8 -*-
# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from datetime import datetime, timedelta

class QFAIRecommendation(Document):
    def validate(self):
        # Auto-generate recommendation ID if not provided
        if not self.recommendation_id:
            customer_code = self.customer[:3].upper()
            date_code = datetime.now().strftime("%Y%m%d")
            count = frappe.db.count("QF AI Recommendation", {"generation_date": self.generation_date})
            self.recommendation_id = f"REC-{customer_code}-{date_code}-{count+1:03d}"
        
        # Validate recommended products
        if not self.recommended_products or len(self.recommended_products) == 0:
            frappe.throw("At least one recommended product is required")
        
        # Calculate confidence score based on product relevance scores
        if self.recommended_products:
            total_relevance = sum(item.relevance_score for item in self.recommended_products)
            avg_relevance = total_relevance / len(self.recommended_products)
            self.confidence_score = min(100, avg_relevance)
        
        # Set data points used if not specified
        if not self.data_points_used:
            # Default to number of products * 10 as an estimate
            self.data_points_used = len(self.recommended_products) * 10
    
    def before_save(self):
        # Check if recommendations are still valid
        today = datetime.now().date()
        days_since_generation = (today - self.generation_date).days
        
        # Weekly recommendations expire after 7 days
        if self.recommendation_type == "Weekly" and days_since_generation > 7:
            self.status = "Expired"
        
        # Seasonal recommendations expire after 30 days
        elif self.recommendation_type == "Seasonal" and days_since_generation > 30:
            self.status = "Expired"
        
        # Special offers expire after 3 days
        elif self.recommendation_type == "Special Offer" and days_since_generation > 3:
            self.status = "Expired"
    
    def on_update(self):
        # Track if customer has viewed or acted on recommendations
        self.track_recommendation_effectiveness()
    
    def track_recommendation_effectiveness(self):
        """Track if customer has purchased recommended products"""
        # This would be implemented to track conversion rates
        pass
