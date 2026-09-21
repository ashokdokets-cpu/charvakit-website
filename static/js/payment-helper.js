/**
 * Charvak Payment Helper - Shared payment function for all pages
 * Version: 2.1 - Fixed template literal interpolation + safe onclick
 */

function processCharvakPayment(email, amount, featureName, callback) {
    if (!email) {
        email = prompt('Enter your email:');
        if (!email) return;
    }
    showPaymentMethodSelection(email, amount, featureName, callback);
}

function showPaymentMethodSelection(email, amount, featureName, callback) {
    // Session G6: fetch region to recommend gateway
    var fallback = function () {
        renderPaymentModal(email, amount, featureName, callback, true);
    };
    if (typeof fetch !== 'function') { fallback(); return; }
    fetch('/api/region')
        .then(function (r) { return r.json(); })
        .then(function (region) {
            var country = (region && region.country ? String(region.country) : '').toUpperCase();
            var isIndia = (country === 'IN');
            renderPaymentModal(email, amount, featureName, callback, isIndia);
        })
        .catch(fallback);
}

function renderPaymentModal(email, amount, featureName, callback, isIndia) {
    var modal = document.createElement('div');
    modal.id = 'payment-method-modal';
    modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:99999;display:flex;align-items:center;justify-content:center;';

    var emailJs = JSON.stringify(email);
    var featureJs = JSON.stringify(featureName);
    var hasCallback = callback ? 'true' : 'false';

    var razorpayStyle = 'padding:15px;border-radius:8px;border:none;background:#3ba591;color:white;font-size:16px;font-weight:bold;cursor:pointer;';
    var paypalStyle = 'padding:15px;border-radius:8px;border:none;background:#ffc439;color:#111;font-size:16px;font-weight:bold;cursor:pointer;';
    var razorpayBadge = isIndia ? '<span style="background:#fff;color:#3ba591;padding:2px 8px;border-radius:12px;font-size:11px;margin-left:8px;">RECOMMENDED</span>' : '';
    var paypalBadge = !isIndia ? '<span style="background:#fff;color:#333;padding:2px 8px;border-radius:12px;font-size:11px;margin-left:8px;">RECOMMENDED</span>' : '';

    var razorpayBtn = '<button class="btn btn-primary btn-lg" onclick=\'closePaymentModal(); payWithRazorpay(' + emailJs + ', ' + amount + ', ' + featureJs + ', "' + hasCallback + '");\' style="' + razorpayStyle + '">🇮🇳 Pay with Razorpay (UPI/Cards/Netbanking)' + razorpayBadge + '</button>';

    var paypalBtn = '<button class="btn btn-warning btn-lg" onclick=\'closePaymentModal(); payWithPayPal(' + emailJs + ', ' + amount + ', ' + featureJs + ', "' + hasCallback + '");\' style="' + paypalStyle + '">🌍 Pay with PayPal (International Cards)' + paypalBadge + '</button>';

    // Order: recommended first
    var orderedButtons = isIndia ? (razorpayBtn + paypalBtn) : (paypalBtn + razorpayBtn);

    modal.innerHTML = '<div class="bg-white p-4 rounded" style="max-width:420px;width:90%;background:white;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,0.3);">' +
        '<h4 class="mb-3" style="margin-bottom:15px;font-weight:bold;">Choose Payment Method</h4>' +
        '<p class="mb-3" style="margin-bottom:15px;color:#666;">' +
        'Feature: <strong>' + featureName + '</strong><br>' +
        'Amount: <strong>₹' + amount.toLocaleString() + '</strong>' +
        '</p>' +
        '<div style="display:grid;gap:10px;">' +
        orderedButtons +
        '<button class="btn btn-secondary" onclick="closePaymentModal();" style="padding:10px;border-radius:8px;border:1px solid #ddd;background:#f5f5f5;color:#333;cursor:pointer;">Cancel</button>' +
        '</div></div>';

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
            const razorpayKey = status.razorpay_key_id || '';
            console.log('Razorpay key present:', !!razorpayKey);

            return fetch('/api/payment/create-order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({amount, name: featureName, method: 'razorpay'})
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
                        ondismiss: function() { alert('Payment cancelled'); }
                    }
                };

                console.log('Opening Razorpay...');
                const rzp = new Razorpay(options);
                rzp.open();
            });
        })
        .catch(error => {
            console.error('Razorpay error:', error);
            alert('? Payment gateway error: ' + error.message);
        });
}

function payWithPayPal(email, amount, featureName, hasCallback) {
    console.log('Starting PayPal payment...');
    const usdAmount = (amount / 83).toFixed(2);

    fetch('/api/payment/create-order', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({amount, name: featureName, method: 'paypal'})
    })
    .then(res => res.json())
    .then(orderData => {
        console.log('PayPal order:', orderData);
        const paypalOrderId = orderData.order_id || orderData.id;

        if (!paypalOrderId) {
            alert('❌ Failed to create PayPal order');
            return;
        }

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

        if (typeof paypal === 'undefined') {
            alert('PayPal SDK not loaded. Loading...');
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
                    amount: {currency_code: 'USD', value: usdAmount}
                }]
            });
        },
        onApprove: function(data, actions) {
            return actions.order.capture().then(function(details) {
                console.log('PayPal payment captured:', details);
                const modal = document.getElementById('paypal-modal');
                if (modal) modal.remove();
                alert('✅ PayPal payment successful! Transaction ID: ' + details.id);
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
