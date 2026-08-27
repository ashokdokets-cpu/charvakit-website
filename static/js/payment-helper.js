/**
 * Charvak Payment Helper - Shared payment function for all pages
 * Version: 2.0 - Complete Razorpay + PayPal Integration
 */

function processCharvakPayment(email, amount, featureName, callback) {
    if (!email) {
        email = prompt('Enter your email:');
        if (!email) return;
    }
    
    // Show payment method selection
    showPaymentMethodSelection(email, amount, featureName, callback);
}

function showPaymentMethodSelection(email, amount, featureName, callback) {
    const modal = document.createElement('div');
    modal.id = 'payment-method-modal';
    modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:99999;display:flex;align-items:center;justify-content:center;';
    modal.innerHTML = `
        <div class="bg-white p-4 rounded" style="max-width:420px;width:90%;background:white;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
            <h4 class="mb-3" style="margin-bottom:15px;font-weight:bold;">Choose Payment Method</h4>
            <p class="mb-3" style="margin-bottom:15px;color:#666;">
                Feature: <strong>${featureName}</strong><br>
                Amount: <strong>₹${amount.toLocaleString()}</strong>
            </p>
            <div style="display:grid;gap:10px;">
                <button class="btn btn-primary btn-lg" onclick="closePaymentModal(); payWithRazorpay('${email}', ${amount}, '${featureName}', ${callback ? 'true' : 'false'});" 
                    style="padding:15px;border-radius:8px;border:none;background:#3ba591;color:white;font-size:16px;font-weight:bold;cursor:pointer;">
                    🇮🇳 Pay with Razorpay (UPI/Cards/Netbanking)
                </button>
                <button class="btn btn-warning btn-lg" onclick="closePaymentModal(); payWithPayPal('${email}', ${amount}, '${featureName}', ${callback ? 'true' : 'false'});" 
                    style="padding:15px;border-radius:8px;border:none;background:#ffc439;color:#111;font-size:16px;font-weight:bold;cursor:pointer;">
                    🌍 Pay with PayPal (International Cards)
                </button>
                <button class="btn btn-secondary" onclick="closePaymentModal();" 
                    style="padding:10px;border-radius:8px;border:1px solid #ddd;background:#f5f5f5;color:#333;cursor:pointer;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function closePaymentModal() {
    const modal = document.getElementById('payment-method-modal');
    if (modal) modal.remove();
}

function payWithRazorpay(email, amount, featureName, hasCallback) {
    console.log('Starting Razorpay payment...');
    
    fetch('/api/payment/status')
        .then(res => res.json())
        .then(status => {
            const razorpayKey = status.razorpay_key_id || 'rzp_live_TSniXv6CyEnZ9B';
            console.log('Razorpay key:', razorpayKey);
            
            return fetch('/api/payment/create-order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    amount: amount,
                    name: featureName,
                    method: 'razorpay'
                })
            })
            .then(res => res.json())
            .then(orderData => {
                console.log('Order created:', orderData);
                
                const orderId = orderData.order_id || orderData.id;
                
                if (!orderId) {
                    alert('❌ Failed to create payment order');
                    return;
                }
                
                const options = {
                    key: razorpayKey,
                    amount: amount * 100,
                    currency: 'INR',
                    name: 'Charvak IT Consulting',
                    description: featureName,
                    order_id: orderId,
                    handler: function(response) {
                        console.log('Razorpay response:', response);
                        
                        fetch('/api/payment/verify', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                method: 'razorpay',
                                payment_id: response.razorpay_payment_id,
                                order_id: response.razorpay_order_id,
                                signature: response.razorpay_signature
                            })
                        })
                        .then(r => r.json())
                        .then(v => {
                            if (v.verified || v.status === 'success') {
                                alert('✅ Razorpay payment successful!');
                                if (hasCallback === 'true') callback(response);
                            } else {
                                alert('Payment verification failed');
                            }
                        });
                    },
                    prefill: {email: email, contact: ''},
                    notes: {feature: featureName},
                    theme: {color: '#3ba591'},
                    modal: {
                        ondismiss: function() {
                            alert('Payment cancelled');
                        }
                    }
                };
                
                console.log('Opening Razorpay...');
                const rzp = new Razorpay(options);
                rzp.open();
            });
        })
        .catch(error => {
            console.error('Razorpay error:', error);
            alert('❌ Payment gateway error: ' + error.message);
        });
}

function payWithPayPal(email, amount, featureName, hasCallback) {
    console.log('Starting PayPal payment...');
    
    const usdAmount = (amount / 83).toFixed(2);
    
    // Create PayPal order on backend
    fetch('/api/payment/create-order', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            amount: amount,
            name: featureName,
            method: 'paypal'
        })
    })
    .then(res => res.json())
    .then(orderData => {
        console.log('PayPal order:', orderData);
        
        const paypalOrderId = orderData.order_id || orderData.id;
        
        if (!paypalOrderId) {
            alert('❌ Failed to create PayPal order');
            return;
        }
        
        // Render PayPal buttons in modal
        const paypalModal = document.createElement('div');
        paypalModal.id = 'paypal-modal';
        paypalModal.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:99999;background:white;padding:30px;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,0.3);min-width:350px;';
        paypalModal.innerHTML = `
            <h5 style="margin-bottom:10px;">Complete PayPal Payment</h5>
            <p style="color:#666;margin-bottom:20px;">
                Feature: ${featureName}<br>
                Amount: <strong>$${usdAmount} USD</strong>
            </p>
            <div id="paypal-buttons-container"></div>
            <button onclick="document.getElementById('paypal-modal').remove()" 
                style="margin-top:15px;width:100%;padding:10px;border:1px solid #ddd;background:#f5f5f5;border-radius:8px;cursor:pointer;">
                Cancel
            </button>
        `;
        document.body.appendChild(paypalModal);
        
        // Check if PayPal SDK is loaded
        if (typeof paypal === 'undefined') {
            alert('PayPal SDK not loaded. Loading...');
            
            // Load PayPal SDK dynamically
            const script = document.createElement('script');
            script.src = 'https://www.paypal.com/sdk/js?client-id=YOUR_PAYPAL_CLIENT_ID&currency=USD';
            script.onload = function() {
                renderPayPalButtons(usdAmount, featureName, paypalOrderId, hasCallback);
            };
            document.head.appendChild(script);
        } else {
            renderPayPalButtons(usdAmount, featureName, paypalOrderId, hasCallback);
        }
    })
    .catch(error => {
        console.error('PayPal order error:', error);
        alert('❌ PayPal payment failed: ' + error.message);
    });
}

function renderPayPalButtons(usdAmount, featureName, paypalOrderId, hasCallback) {
    paypal.Buttons({
        createOrder: function(data, actions) {
            return actions.order.create({
                purchase_units: [{
                    description: featureName,
                    amount: {
                        currency_code: 'USD',
                        value: usdAmount
                    }
                }]
            });
        },
        onApprove: function(data, actions) {
            return actions.order.capture().then(function(details) {
                console.log('PayPal payment captured:', details);
                
                // Remove modal
                const modal = document.getElementById('paypal-modal');
                if (modal) modal.remove();
                
                alert('✅ PayPal payment successful! Transaction ID: ' + details.id);
                
                // Verify on backend
                fetch('/api/payment/verify', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        method: 'paypal',
                        order_id: paypalOrderId,
                        paypal_order_id: details.id
                    })
                })
                .then(r => r.json())
                .then(v => {
                    console.log('Verification:', v);
                    if (hasCallback === 'true') callback({paypal_order_id: details.id, details: details});
                });
            });
        },
        onError: function(err) {
            console.error('PayPal error:', err);
            alert('❌ PayPal payment failed. Please try again.');
        },
        onCancel: function(data) {
            alert('Payment cancelled');
            const modal = document.getElementById('paypal-modal');
            if (modal) modal.remove();
        }
    }).render('#paypal-buttons-container');
}