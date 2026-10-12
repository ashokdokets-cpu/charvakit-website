/* ========================================================================
 * tool-pay.js — Session 43-A1.6
 * ========================================================================
 * Adds a "Pay <price>" button alongside the existing credit button on
 * every AI tool page. Detects the user's region, fetches the correct
 * price from the backend, opens Razorpay or PayPal, then runs the tool.
 *
 * Usage — add to any tool template:
 *   <script src="/static/js/tool-pay.js?v=1"></script>
 *   <script>
 *     ToolPay.init({
 *       toolSlug: 'resume_roast',
 *       toolName: 'Resume Roast',
 *       collectInput: function () {
 *         return { resume: ..., job_title: ... };  // fields the tool needs
 *       },
 *       renderResult: function (result) { ... }   // same as credit path
 *     });
 *   </script>
 *
 * The script finds the tool's run button (by id="runBtn") and inserts
 * a "Pay ₹99" button right next to it.
 * ======================================================================== */

window.ToolPay = (function () {
    'use strict';

    var cfg = {};
    var currentRegion = { country: 'IN', currency: 'INR' };
    var cachedPrice = null;
    var currentPurchase = null;
    var razorpayScriptLoaded = false;
    var paypalScriptLoaded = false;

    // ---------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------

    function _esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function _getEmail() {
        return (localStorage.getItem('userEmail') || '').trim().toLowerCase();
    }

    function _getAuthToken() {
        return localStorage.getItem('auth_token') || localStorage.getItem('charvak_token') || '';
    }

    function _getUserId() {
        return localStorage.getItem('userId') || null;
    }

    // ---------------------------------------------------------------
    // Region detection
    // ---------------------------------------------------------------

    function loadRegion() {
        return fetch('/api/region')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                currentRegion = {
                    country: data.country || 'IN',
                    currency: data.currency || 'INR'
                };
                return currentRegion;
            })
            .catch(function () {
                return currentRegion;  // default IN/INR on failure
            });
    }

    // ---------------------------------------------------------------
    // Price fetch
    // ---------------------------------------------------------------

    function fetchPrice() {
        return fetch('/api/tools/paid/create-order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool_slug: cfg.toolSlug,
                country_code: currentRegion.country
            })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status !== 'success') {
                    throw new Error(data.message || 'Could not fetch price');
                }
                cachedPrice = data;
                return data;
            });
    }

    // ---------------------------------------------------------------
    // Button rendering
    // ---------------------------------------------------------------

    function insertPayButton() {
        var runBtn = document.getElementById('runBtn');
        if (!runBtn || document.getElementById('toolPayBtn')) return;

        var wrapper = document.createElement('div');
        wrapper.className = 'mt-2';
        wrapper.style.display = 'flex';
        wrapper.style.gap = '8px';
        wrapper.style.alignItems = 'center';

        var price = cachedPrice ? cachedPrice.amount_display : '...';
        var currency = cachedPrice ? cachedPrice.currency : '';
        var gateway = cachedPrice ? cachedPrice.gateway : '';

        var payBtn = document.createElement('button');
        payBtn.id = 'toolPayBtn';
        payBtn.className = 'btn btn-outline-primary btn-lg w-100';
        payBtn.type = 'button';
        payBtn.innerHTML = 'Or pay ' + _esc(price) + ' <span style="opacity:0.7; font-weight:400;">(no credits needed)</span>';
        payBtn.addEventListener('click', onClickPay);

        wrapper.appendChild(payBtn);

        // Insert right after the run button
        runBtn.parentNode.insertBefore(wrapper, runBtn.nextSibling);

        // Small hint line below
        var hint = document.createElement('div');
        hint.className = 'text-muted small mt-1';
        hint.style.textAlign = 'center';
        hint.textContent = gateway === 'razorpay'
            ? 'One-time payment via Razorpay. Instant result.'
            : 'One-time payment via PayPal. Instant result.';
        wrapper.parentNode.insertBefore(hint, wrapper.nextSibling);
    }

    // ---------------------------------------------------------------
    // Email prompt (for anonymous buyers)
    // ---------------------------------------------------------------

    function promptEmailIfMissing() {
        var email = _getEmail();
        if (email) return email;

        var entered = window.prompt(
            'Please enter your email for the receipt and result delivery:',
            ''
        );
        if (!entered || !entered.includes('@')) {
            alert('Valid email required to complete the purchase.');
            return null;
        }
        entered = entered.trim().toLowerCase();
        localStorage.setItem('userEmail', entered);
        return entered;
    }

    // ---------------------------------------------------------------
    // Load Razorpay SDK on demand
    // ---------------------------------------------------------------

    function ensureRazorpayLoaded() {
        return new Promise(function (resolve, reject) {
            if (razorpayScriptLoaded && window.Razorpay) return resolve();
            if (window.Razorpay) { razorpayScriptLoaded = true; return resolve(); }

            var s = document.createElement('script');
            s.src = 'https://checkout.razorpay.com/v1/checkout.js';
            s.onload = function () { razorpayScriptLoaded = true; resolve(); };
            s.onerror = function () { reject(new Error('Could not load Razorpay')); };
            document.head.appendChild(s);
        });
    }

    // ---------------------------------------------------------------
    // Load PayPal SDK on demand
    // ---------------------------------------------------------------

    function ensurePayPalLoaded(clientId) {
        return new Promise(function (resolve, reject) {
            if (paypalScriptLoaded && window.paypal) return resolve();
            if (window.paypal) { paypalScriptLoaded = true; return resolve(); }

            var s = document.createElement('script');
            s.src = 'https://www.paypal.com/sdk/js?client-id=' + encodeURIComponent(clientId) +
                    '&currency=' + encodeURIComponent(cachedPrice.currency) +
                    '&intent=capture';
            s.onload = function () { paypalScriptLoaded = true; resolve(); };
            s.onerror = function () { reject(new Error('Could not load PayPal')); };
            document.head.appendChild(s);
        });
    }

    // ---------------------------------------------------------------
    // Razorpay flow
    // ---------------------------------------------------------------

    function runRazorpayFlow(email) {
        return ensureRazorpayLoaded().then(function () {
            return new Promise(function (resolve, reject) {
                var options = {
                    key: cachedPrice.key_id,
                    amount: Math.round(cachedPrice.amount * 100),   // paise
                    currency: cachedPrice.currency,
                    name: 'Charvak IT Consulting',
                    description: cachedPrice.tool_name + ' - one-off run',
                    order_id: cachedPrice.order_id,
                    prefill: {
                        email: email
                    },
                    theme: { color: '#3ba591' },
                    handler: function (response) {
                        // Payment success — call /run to verify + execute
                        var input = cfg.collectInput();
                        var payload = Object.assign({}, input, {
                            tool_slug: cfg.toolSlug,
                            email: email,
                            user_id: _getUserId(),
                            gateway: 'razorpay',
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_signature: response.razorpay_signature
                        });
                        resolve(payload);
                    },
                    modal: {
                        ondismiss: function () {
                            reject(new Error('Payment cancelled'));
                        }
                    }
                };
                var rzp = new window.Razorpay(options);
                rzp.on('payment.failed', function (resp) {
                    reject(new Error(resp.error.description || 'Payment failed'));
                });
                rzp.open();
            });
        });
    }

    // ---------------------------------------------------------------
    // PayPal flow
    // ---------------------------------------------------------------

    function runPayPalFlow(email, clientId) {
        return ensurePayPalLoaded(clientId).then(function () {
            return new Promise(function (resolve, reject) {
                // We create a one-shot PayPal Buttons instance in an overlay
                var overlay = _makePayPalOverlay();
                var container = overlay.querySelector('#paypal-btn-container');

                var buttons = window.paypal.Buttons({
                    createOrder: function () {
                        // Use the order we already created server-side
                        return cachedPrice.order_id;
                    },
                    onApprove: function (data) {
                        overlay.remove();
                        var input = cfg.collectInput();
                        var payload = Object.assign({}, input, {
                            tool_slug: cfg.toolSlug,
                            email: email,
                            user_id: _getUserId(),
                            gateway: 'paypal',
                            paypal_order_id: data.orderID
                        });
                        resolve(payload);
                    },
                    onCancel: function () {
                        overlay.remove();
                        reject(new Error('Payment cancelled'));
                    },
                    onError: function (err) {
                        overlay.remove();
                        reject(new Error(err.message || 'PayPal error'));
                    }
                });

                buttons.render(container);
            });
        });
    }

    function _makePayPalOverlay() {
        var o = document.createElement('div');
        o.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:99999;display:flex;align-items:center;justify-content:center;';
        o.innerHTML = '<div style="background:#fff;padding:24px;border-radius:14px;max-width:420px;width:90%;">' +
            '<h3 style="margin:0 0 8px;font-size:1.1rem;">Complete payment</h3>' +
            '<p style="margin:0 0 16px;color:#64748b;font-size:0.9rem;">Pay ' + _esc(cachedPrice.amount_display) + ' via PayPal</p>' +
            '<div id="paypal-btn-container"></div>' +
            '<button type="button" style="margin-top:12px;background:none;border:none;color:#3ba591;cursor:pointer;" id="paypal-cancel">Cancel</button>' +
            '</div>';
        document.body.appendChild(o);
        o.querySelector('#paypal-cancel').addEventListener('click', function () {
            o.remove();
        });
        return o;
    }

    // ---------------------------------------------------------------
    // Main click handler
    // ---------------------------------------------------------------

    function onClickPay(e) {
        if (e && e.preventDefault) e.preventDefault();

        var email = promptEmailIfMissing();
        if (!email) return;

        var btn = document.getElementById('toolPayBtn');
        if (btn) { btn.disabled = true; btn.textContent = 'Processing...'; }

        // Refresh the order server-side in case the cached one is stale
        fetch('/api/tools/paid/create-order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool_slug: cfg.toolSlug,
                country_code: currentRegion.country
            })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.status !== 'success') {
                    throw new Error(data.message || 'Could not create order');
                }
                cachedPrice = data;

                // Also need the PayPal client ID for the SDK
                return fetch('/api/payment/status')
                    .then(function (r) { return r.json(); })
                    .then(function (p) {
                        cachedPrice.paypal_client_id = p.paypal_client_id;
                        return cachedPrice;
                    });
            })
            .then(function () {
                if (cachedPrice.gateway === 'razorpay') {
                    return runRazorpayFlow(email);
                } else {
                    return runPayPalFlow(email, cachedPrice.paypal_client_id);
                }
            })
            .then(function (payload) {
                // Fire the run endpoint
                return fetch('/api/tools/paid/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (data.status !== 'success') {
                            throw new Error(data.message || 'Tool run failed');
                        }
                        return data.result;
                    });
            })
            .then(function (result) {
                if (typeof cfg.renderResult === 'function') {
                    cfg.renderResult(result);
                } else {
                    alert('Tool completed. Check /my-tools for the result.');
                }
            })
            .catch(function (err) {
                var msg = err && err.message ? err.message : 'Payment failed';
                if (msg === 'Payment cancelled') return;
                var errEl = document.getElementById('toolError');
                if (errEl) {
                    errEl.textContent = msg;
                    errEl.classList.remove('d-none');
                } else {
                    alert(msg);
                }
            })
            .then(function () {
                var btn2 = document.getElementById('toolPayBtn');
                if (btn2) {
                    btn2.disabled = false;
                    btn2.innerHTML = 'Or pay ' + _esc(cachedPrice.amount_display) +
                        ' <span style="opacity:0.7; font-weight:400;">(no credits needed)</span>';
                }
            });
    }

    // ---------------------------------------------------------------
    // Public init
    // ---------------------------------------------------------------

    function init(options) {
        cfg = options || {};
        if (!cfg.toolSlug) {
            console.warn('ToolPay.init: toolSlug required');
            return;
        }

        loadRegion()
            .then(fetchPrice)
            .then(function () {
                insertPayButton();
            })
            .catch(function (err) {
                console.warn('ToolPay: setup failed', err);
            });
    }

    return { init: init };
})();