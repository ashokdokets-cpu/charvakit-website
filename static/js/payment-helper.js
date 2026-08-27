/**
 * Charvak Payment Helper - Shared payment function for all pages
 * Version: 1.0
 */

function processCharvakPayment(email, amount, featureName, callback) {
    if (!email) {
        email = prompt('Enter your email:');
        if (!email) return;
    }
    
    if (!confirm(`Proceed with payment for ${featureName}?\n\nAmount: ₹${amount}\n\nClick OK to continue to payment.`)) {
        return;
    }
    
    fetch('/api/payment/create-order', {
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
        if (orderData.status === 'success' || orderData.order_id) {
            const options = {
                key: orderData.key_id || window.charvak_razorpay_key,
                amount: amount * 100,
                currency: 'INR',
                name: 'Charvak IT Consulting',
                description: featureName,
                order_id: orderData.order_id,
                handler: function(response) {
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
                        if (v.verified) {
                            alert('✅ Payment successful!');
                            if (callback) callback(response);
                        } else {
                            alert('Payment verification failed');
                        }
                    });
                },
                prefill: {email: email},
                theme: {color: '#3ba591'},
                modal: {
                    ondismiss: function() {
                        alert('Payment cancelled');
                    }
                }
            };
            
            const rzp = new Razorpay(options);
            rzp.open();
        } else {
            alert('Failed to create payment order: ' + (orderData.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Payment error:', error);
        alert('Payment gateway error. Please try again.');
    });
}