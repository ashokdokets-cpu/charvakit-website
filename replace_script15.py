with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find Script 15 (payment modal script) and replace entirely
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)

# Find the script that contains showPaymentMethodModal
for script in scripts:
    if 'showPaymentMethodModal' in script:
        # Replace this entire script with clean version
        clean_script = '''
function processToolPayment(amount, toolName, callback) {
    var currency = localStorage.getItem('charvak_currency') || 'INR';
    showPaymentMethodModal(amount, toolName, callback);
}

function showPaymentMethodModal(amount, toolName, callback) {
    var modal = document.createElement('div');
    modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.7);z-index:99999;display:flex;align-items:center;justify-content:center;';
    
    var modalContent = '';
    modalContent += '<div style="background:white;padding:30px;border-radius:15px;max-width:400px;width:90%;">';
    modalContent += '<h4>Choose Payment Method</h4>';
    modalContent += '<p>Amount: <strong>' + amount + '</strong> (' + toolName + ')</p>';
    modalContent += '<div style="display:grid;gap:10px;">';
    modalContent += '<button class="btn btn-primary" onclick="payWithRazorpay(' + amount + ', \\'' + toolName + '\\')">Pay with Razorpay</button>';
    modalContent += '<button class="btn btn-warning" onclick="payWithPayPal(' + amount + ', \\'' + toolName + '\\')">Pay with PayPal</button>';
    modalContent += '<button class="btn btn-secondary" onclick="this.parentElement.parentElement.parentElement.remove()">Cancel</button>';
    modalContent += '</div></div>';
    
    modal.innerHTML = modalContent;
    document.body.appendChild(modal);
}

function payWithRazorpay(amount, toolName) {
    var modal = document.querySelector('div[style*="z-index:99999"]');
    if (modal) modal.remove();
    alert('Razorpay payment for ' + toolName + ': ' + amount);
}

function payWithPayPal(amount, toolName) {
    var modal = document.querySelector('div[style*="z-index:99999"]');
    if (modal) modal.remove();
    alert('PayPal payment for ' + toolName + ': ' + amount);
}
'''
        
        # Replace the old script with clean version
        content = content.replace(script, clean_script)
        with open('templates/base.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print('✅ Script 15 replaced with clean version!')
        break
