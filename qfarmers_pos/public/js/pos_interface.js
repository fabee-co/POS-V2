// QFarmers POS Interface
// Main JavaScript file for the POS interface

frappe.pages['qfarmers-pos'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'QFarmers POS',
        single_column: true
    });
    
    // Initialize POS
    new QFarmersPOS(page);
    
    // Add actions
    page.add_menu_item('New Transaction', () => qfarmers_pos.new_transaction());
    page.add_menu_item('View Sales History', () => qfarmers_pos.view_sales_history());
    page.add_menu_item('Sync Inventory', () => qfarmers_pos.sync_inventory());
    
    // Add custom CSS
    frappe.dom.set_style(`
        .qf-pos-container {
            display: flex;
            height: calc(100vh - 170px);
            overflow: hidden;
        }
        .qf-pos-items {
            flex: 7;
            overflow-y: auto;
            padding: 15px;
            background: #f5f7fa;
        }
        .qf-pos-cart {
            flex: 3;
            border-left: 1px solid #d1d8dd;
            background: white;
            display: flex;
            flex-direction: column;
        }
        .qf-pos-item-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            grid-gap: 15px;
        }
        .qf-pos-item {
            border: 1px solid #d1d8dd;
            border-radius: 5px;
            padding: 10px;
            background: white;
            cursor: pointer;
            position: relative;
            transition: all 0.2s;
        }
        .qf-pos-item:hover {
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .qf-organic-badge {
            position: absolute;
            top: 5px;
            right: 5px;
            background: #7CFC00;
            color: #006400;
            font-size: 10px;
            padding: 2px 5px;
            border-radius: 3px;
            font-weight: bold;
        }
        .qf-freshness-indicator {
            height: 4px;
            width: 100%;
            background: #f0f0f0;
            margin-top: 5px;
            border-radius: 2px;
            overflow: hidden;
        }
        .qf-freshness-bar {
            height: 100%;
            background: linear-gradient(90deg, #7CFC00, #32CD32);
        }
        .qf-freshness-low {
            background: linear-gradient(90deg, #FFA500, #FF4500);
        }
        .qf-pos-item-name {
            font-weight: bold;
            margin-top: 5px;
        }
        .qf-pos-item-price {
            color: #1a1a1a;
            margin-top: 3px;
        }
        .qf-pos-item-stock {
            font-size: 11px;
            color: #8d99a6;
        }
        .qf-pos-categories {
            display: flex;
            overflow-x: auto;
            padding: 10px 0;
            margin-bottom: 15px;
            -webkit-overflow-scrolling: touch;
        }
        .qf-pos-category {
            white-space: nowrap;
            padding: 8px 15px;
            margin-right: 10px;
            background: white;
            border: 1px solid #d1d8dd;
            border-radius: 20px;
            cursor: pointer;
        }
        .qf-pos-category.active {
            background: #5e64ff;
            color: white;
            border-color: #5e64ff;
        }
        .qf-pos-cart-header {
            padding: 15px;
            border-bottom: 1px solid #d1d8dd;
        }
        .qf-pos-cart-items {
            flex: 1;
            overflow-y: auto;
            padding: 0 15px;
        }
        .qf-pos-cart-item {
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
        }
        .qf-pos-cart-item-details {
            flex: 1;
        }
        .qf-pos-cart-item-name {
            font-weight: bold;
        }
        .qf-pos-cart-item-price {
            font-size: 12px;
            color: #8d99a6;
        }
        .qf-pos-cart-item-qty {
            display: flex;
            align-items: center;
        }
        .qf-pos-cart-qty-btn {
            width: 25px;
            height: 25px;
            border: 1px solid #d1d8dd;
            border-radius: 3px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            user-select: none;
        }
        .qf-pos-cart-qty-input {
            width: 35px;
            text-align: center;
            border: none;
            outline: none;
            margin: 0 5px;
        }
        .qf-pos-cart-footer {
            padding: 15px;
            border-top: 1px solid #d1d8dd;
            background: #f5f7fa;
        }
        .qf-pos-cart-total {
            display: flex;
            justify-content: space-between;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .qf-pos-checkout-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 5px;
            width: 100%;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .qf-pos-checkout-btn:hover {
            background: #45a049;
        }
    `);
};

class QFarmersPOS {
    constructor(page) {
        this.page = page;
        this.items = [];
        this.cart = [];
        this.customer = null;
        
        this.make();
        this.bind_events();
        this.load_items();
    }
    
    make() {
        this.$pos_container = $('<div class="qf-pos-container"></div>').appendTo(this.page.main);
        
        // Items section
        this.$items_section = $('<div class="qf-pos-items"></div>').appendTo(this.$pos_container);
        
        // Categories
        this.$categories = $('<div class="qf-pos-categories"></div>').appendTo(this.$items_section);
        
        // Item grid
        this.$item_grid = $('<div class="qf-pos-item-grid"></div>').appendTo(this.$items_section);
        
        // Cart section
        this.$cart_section = $('<div class="qf-pos-cart"></div>').appendTo(this.$pos_container);
        
        // Cart header
        this.$cart_header = $('<div class="qf-pos-cart-header"></div>').appendTo(this.$cart_section);
        this.$cart_header.html('<h4>Current Order</h4>');
        
        // Cart items
        this.$cart_items = $('<div class="qf-pos-cart-items"></div>').appendTo(this.$cart_section);
        
        // Cart footer
        this.$cart_footer = $('<div class="qf-pos-cart-footer"></div>').appendTo(this.$cart_section);
        this.$cart_footer.html(`
            <div class="qf-pos-cart-total">
                <span>Total</span>
                <span>₹0.00</span>
            </div>
            <button class="qf-pos-checkout-btn">Checkout</button>
        `);
    }
    
    bind_events() {
        let self = this;
        
        // Category selection
        this.$categories.on('click', '.qf-pos-category', function() {
            self.$categories.find('.qf-pos-category').removeClass('active');
            $(this).addClass('active');
            self.filter_items($(this).data('category'));
        });
        
        // Item selection
        this.$item_grid.on('click', '.qf-pos-item', function() {
            let item_code = $(this).data('item-code');
            self.add_to_cart(item_code);
        });
        
        // Cart quantity buttons
        this.$cart_items.on('click', '.qf-pos-cart-qty-btn', function() {
            let $row = $(this).closest('.qf-pos-cart-item');
            let item_code = $row.data('item-code');
            let action = $(this).data('action');
            
            if (action === 'decrease') {
                self.update_cart_qty(item_code, -1);
            } else if (action === 'increase') {
                self.update_cart_qty(item_code, 1);
            }
        });
        
        // Checkout button
        this.$cart_footer.on('click', '.qf-pos-checkout-btn', function() {
            self.checkout();
        });
    }
    
    load_items() {
        let self = this;
        
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Item',
                fields: ['name', 'item_name', 'item_code', 'standard_rate', 'item_group', 'stock_uom'],
                limit: 500
            },
            callback: function(r) {
                if (r.message) {
                    self.items = r.message;
                    self.render_items();
                    self.load_categories();
                }
            }
        });
    }
    
    load_categories() {
        let self = this;
        let categories = [];
        
        // Extract unique categories from items
        this.items.forEach(item => {
            if (!categories.includes(item.item_group)) {
                categories.push(item.item_group);
            }
        });
        
        // Render categories
        this.$categories.empty();
        this.$categories.append('<div class="qf-pos-category active" data-category="All">All</div>');
        
        categories.forEach(category => {
            this.$categories.append(`<div class="qf-pos-category" data-category="${category}">${category}</div>`);
        });
    }
    
    render_items(filter_category) {
        this.$item_grid.empty();
        
        let items_to_display = this.items;
        
        // Apply category filter if specified
        if (filter_category && filter_category !== 'All') {
            items_to_display = this.items.filter(item => item.item_group === filter_category);
        }
        
        items_to_display.forEach(item => {
            // Simulate organic status and freshness for demo
            let is_organic = Math.random() > 0.5;
            let freshness = Math.floor(Math.random() * 100);
            let freshness_class = freshness < 50 ? 'qf-freshness-low' : '';
            
            let html = `
                <div class="qf-pos-item" data-item-code="${item.item_code}">
                    ${is_organic ? '<div class="qf-organic-badge">ORGANIC</div>' : ''}
                    <div class="qf-pos-item-name">${item.item_name}</div>
                    <div class="qf-pos-item-price">₹${item.standard_rate.toFixed(2)}</div>
                    <div class="qf-pos-item-stock">In stock</div>
                    <div class="qf-freshness-indicator">
                        <div class="qf-freshness-bar ${freshness_class}" style="width: ${freshness}%"></div>
                    </div>
                </div>
            `;
            
            this.$item_grid.append(html);
        });
    }
    
    filter_items(category) {
        this.render_items(category);
    }
    
    add_to_cart(item_code) {
        let item = this.items.find(i => i.item_code === item_code);
        
        if (!item) return;
        
        // Check if item already in cart
        let cart_item = this.cart.find(i => i.item_code === item_code);
        
        if (cart_item) {
            this.update_cart_qty(item_code, 1);
        } else {
            this.cart.push({
                item_code: item.item_code,
                item_name: item.item_name,
                price: item.standard_rate,
                qty: 1,
                uom: item.stock_uom
            });
            
            this.render_cart();
        }
    }
    
    update_cart_qty(item_code, change) {
        let cart_item = this.cart.find(i => i.item_code === item_code);
        
        if (!cart_item) return;
        
        cart_item.qty += change;
        
        if (cart_item.qty <= 0) {
            // Remove item from cart
            this.cart = this.cart.filter(i => i.item_code !== item_code);
        }
        
        this.render_cart();
    }
    
    render_cart() {
        this.$cart_items.empty();
        
        if (this.cart.length === 0) {
            this.$cart_items.html('<div class="text-center text-muted p-3">Cart is empty</div>');
            this.$cart_footer.find('.qf-pos-cart-total span:last-child').text('₹0.00');
            return;
        }
        
        let total = 0;
        
        this.cart.forEach(item => {
            let subtotal = item.price * item.qty;
            total += subtotal;
            
            let html = `
                <div class="qf-pos-cart-item" data-item-code="${item.item_code}">
                    <div class="qf-pos-cart-item-details">
                        <div class="qf-pos-cart-item-name">${item.item_name}</div>
                        <div class="qf-pos-cart-item-price">₹${item.price.toFixed(2)} × ${item.qty} ${item.uom}</div>
                    </div>
                    <div class="qf-pos-cart-item-qty">
                        <div class="qf-pos-cart-qty-btn" data-action="decrease">-</div>
                        <input type="text" class="qf-pos-cart-qty-input" value="${item.qty}" readonly>
                        <div class="qf-pos-cart-qty-btn" data-action="increase">+</div>
                    </div>
                </div>
            `;
            
            this.$cart_items.append(html);
        });
        
        this.$cart_footer.find('.qf-pos-cart-total span:last-child').text(`₹${total.toFixed(2)}`);
    }
    
    checkout() {
        if (this.cart.length === 0) {
            frappe.msgprint('Cart is empty');
            return;
        }
        
        let self = this;
        
        // Select customer dialog
        let d = new frappe.ui.Dialog({
            title: 'Checkout',
            fields: [
                {
                    label: 'Customer',
                    fieldname: 'customer',
                    fieldtype: 'Link',
                    options: 'Customer',
                    reqd: 1
                },
                {
                    label: 'Payment Method',
                    fieldname: 'payment_method',
                    fieldtype: 'Select',
                    options: 'Cash\nCredit Card\nDebit Card\nUPI\nWallet',
                    default: 'Cash'
                }
            ],
            primary_action_label: 'Create Invoice',
            primary_action: function(values) {
                self.create_invoice(values);
                d.hide();
            }
        });
        
        d.show();
    }
    
    create_invoice(values) {
        let self = this;
        let items = this.cart.map(item => {
            return {
                item_code: item.item_code,
                qty: item.qty
            };
        });
        
        frappe.call({
            method: 'frappe.client.insert',
            args: {
                doc: {
                    doctype: 'Sales Invoice',
                    customer: values.customer,
                    items: items,
                    is_pos: 1,
                    payments: [
                        {
                            mode_of_payment: values.payment_method,
                            amount: self.get_total()
                        }
                    ]
                }
            },
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert({
                        message: 'Sales Invoice created successfully',
                        indicator: 'green'
                    });
                    
                    // Clear cart
                    self.cart = [];
                    self.render_cart();
                    
                    // Open invoice
                    frappe.set_route('Form', 'Sales Invoice', r.message.name);
                }
            }
        });
    }
    
    get_total() {
        return this.cart.reduce((total, item) => total + (item.price * item.qty), 0);
    }
    
    new_transaction() {
        this.cart = [];
        this.render_cart();
        frappe.show_alert({
            message: 'New transaction started',
            indicator: 'blue'
        });
    }
    
    view_sales_history() {
        frappe.set_route('List', 'Sales Invoice', {is_pos: 1});
    }
    
    sync_inventory() {
        frappe.show_alert({
            message: 'Syncing inventory...',
            indicator: 'blue'
        });
        
        // Simulate inventory sync
        setTimeout(() => {
            frappe.show_alert({
                message: 'Inventory synced successfully',
                indicator: 'green'
            });
        }, 2000);
    }
}

// Initialize global object
window.qfarmers_pos = {
    new_transaction: function() {
        frappe.msgprint('Starting new transaction');
    },
    
    view_sales_history: function() {
        frappe.set_route('List', 'Sales Invoice', {is_pos: 1});
    },
    
    sync_inventory: function() {
        frappe.show_alert({
            message: 'Syncing inventory with online store...',
            indicator: 'blue'
        });
        
        // Simulate sync
        setTimeout(() => {
            frappe.show_alert({
                message: 'Inventory synced successfully',
                indicator: 'green'
            });
        }, 2000);
    }
};
