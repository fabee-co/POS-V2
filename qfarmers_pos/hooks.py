app_name = "qfarmers_pos"
app_title = "QFarmers POS System"
app_publisher = "QFarmers"
app_description = "Custom POS application for QFarmers organic produce and grocery store in Chennai"
app_email = "info@qfarmers.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/qfarmers_pos/css/qfarmers_pos.css"
app_include_js = "/assets/qfarmers_pos/js/qfarmers_pos.js"

# include js, css files in header of web template
web_include_css = "/assets/qfarmers_pos/css/qfarmers_pos_web.css"
web_include_js = "/assets/qfarmers_pos/js/qfarmers_pos_web.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "qfarmers_pos/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
page_js = {"qfarmers-pos": "public/js/pos_interface.js"}

# include js in doctype views
# doctype_js = {"doctype": "public/js/doctype.js"}
# doctype_list_js = {"doctype": "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype": "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype": "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "index"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "qfarmers_pos.utils.jinja_methods",
#	"filters": "qfarmers_pos.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "qfarmers_pos.install.before_install"
# after_install = "qfarmers_pos.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "qfarmers_pos.uninstall.before_uninstall"
# after_uninstall = "qfarmers_pos.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "qfarmers_pos.utils.before_app_install"
# after_app_install = "qfarmers_pos.utils.after_app_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "qfarmers_pos.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly": [
		"qfarmers_pos.qfarmers_pos.utils.inventory_management.check_expiring_inventory"
	],
	"daily": [
		"qfarmers_pos.qfarmers_pos.utils.inventory_management.update_inventory_freshness",
		"qfarmers_pos.qfarmers_pos.utils.subscription_management.process_daily_subscriptions"
	],
	"weekly": [
		"qfarmers_pos.qfarmers_pos.utils.ai_recommendation.generate_weekly_recommendations"
	]
}

# Testing
# -------

# before_tests = "qfarmers_pos.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "qfarmers_pos.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "qfarmers_pos.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["qfarmers_pos.utils.before_request"]
# after_request = ["qfarmers_pos.utils.after_request"]

# Job Events
# ----------
# before_job = ["qfarmers_pos.utils.before_job"]
# after_job = ["qfarmers_pos.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"qfarmers_pos.auth.validate"
# ]

# Website Route Rules
website_route_rules = [
    {"from_route": "/app/qfarmers-pos", "to_route": "qfarmers_pos/qfarmers_pos/page/qfarmers_pos/qfarmers_pos"},
    {"from_route": "/shop", "to_route": "qfarmers_pos/www/shop"},
    {"from_route": "/shop/product", "to_route": "qfarmers_pos/www/product"},
    {"from_route": "/shop/cart", "to_route": "qfarmers_pos/www/cart"},
    {"from_route": "/shop/checkout", "to_route": "qfarmers_pos/www/checkout"},
    {"from_route": "/shop/category", "to_route": "qfarmers_pos/www/shop"},
    {"from_route": "/shop/product/:product", "to_route": "qfarmers_pos/www/product"},
    {"from_route": "/shop/category/:category", "to_route": "qfarmers_pos/www/shop"}
]

# Desktop Icons
desktop_icons = [
    {
        "module_name": "QFarmers POS",
        "label": "QFarmers POS",
        "icon": "octicon octicon-credit-card",
        "type": "page",
        "link": "qfarmers-pos",
        "color": "#FF8888"
    },
    {
        "module_name": "Organic Inventory",
        "label": "Organic Inventory",
        "icon": "octicon octicon-package",
        "type": "doctype",
        "link": "QF Inventory Batch",
        "color": "#7CFC00"
    },
    {
        "module_name": "Online Store",
        "label": "Online Store",
        "icon": "octicon octicon-globe",
        "type": "doctype",
        "link": "QF Online Order",
        "color": "#4682B4"
    },
    {
        "module_name": "Subscriptions",
        "label": "Subscriptions",
        "icon": "octicon octicon-sync",
        "type": "doctype",
        "link": "QF Subscription",
        "color": "#9370DB"
    }
]

# Fixtures
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "QFarmers POS"]]},
    {"dt": "Role", "filters": [["name", "like", "QFarmers%"]]},
    {"dt": "Print Format", "filters": [["module", "=", "QFarmers POS"]]}
]
