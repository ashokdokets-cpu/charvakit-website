/* ========================================================================
 * ielts-deep-report.js - Session 43-A1.7
 * ========================================================================
 * Shared CTA + payment + inline-render flow for the IELTS Deep Report
 * micro-paywall (Rs 99).
 *
 * Usage in a template:
 *   <script src="/static/js/ielts-deep-report.js?v=20261013a"></script>
 *   <script>
 *     IeltsDeepReport.init({
 *       testType: 'writing',              // or 'speaking'
 *       slotId: 'deepReportSlot',         // id of the container div
 *       getSessionId: function () { return IW.sessionId; },
 *       getEmail: function () {
 *         return (localStorage.getItem('userEmail') || '').toLowerCase();
 *       },
 *     });
 *   </script>
 *
 * Requires: window.charvakFetch (from base.html)
 * ======================================================================== */

window.IeltsDeepReport = (function () {
    'use strict';

    var cfg = {};
    var priceInfo = null;
    var razorpayLoaded = false;
    var paypalLoaded = false;

    // ---------- helpers ----------

    function _esc(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    function _fetch(url, opts) {
        // Use charvakFetch if available so the Authorization header is injected
        if (typeof window.charvakFetch === 'function') {
            return window.charvakFetch(url, opts);
        }
        return fetch(url, opts);
    }

    // ---------- pricing ----------

    async function _loadPrice() {
        try {
            var r = await _fetch('/api/ielts/deep-report/price', { method: 'GET' });
            var j = await r.json();
            if (j && j.status === 'success') {
                priceInfo = j;
            }
        } catch (e) {
            // Silent-fail; we'll default to 'Rs 99' in the CTA
            priceInfo = null;
        }
        return priceInfo;
    }

    // ---------- CTA render ----------

    function _renderCta() {
        var slot = document.getElementById(cfg.slotId);
        if (!slot) return;

        var amount = priceInfo ? priceInfo.amount_display : '\u20B999';
        var gateway = priceInfo ? priceInfo.gateway : 'razorpay';

        slot.innerHTML =
            '<div class="idr-cta" style="margin-top:24px;background:linear-gradient(135deg,#ecfdf5 0%,#d1fae5 100%);border:2px solid #10b981;border-radius:12px;padding:24px;">' +
              '<div style="display:inline-block;background:#10b981;color:#fff;font-size:0.72rem;font-weight:700;letter-spacing:0.5px;padding:3px 10px;border-radius:12px;text-transform:uppercase;margin-bottom:12px;">Examiner-grade</div>' +
              '<h4 style="margin:0 0 8px;font-weight:800;color:#065f46;">Unlock the full examiner report</h4>' +
              '<p style="margin:0 0 16px;color:#065f46;font-size:0.94rem;line-height:1.5;">' +
                'Grammar corrections, vocabulary upgrades, an example high-band ' + _esc(cfg.testType) + ' ' +
                'rewrite, and personalised exercises &mdash; delivered as a PDF to your inbox.' +
              '</p>' +
              '<button id="idrUnlockBtn" onclick="IeltsDeepReport.unlock()" ' +
                'style="background:#10b981;color:#fff;border:0;border-radius:8px;padding:12px 24px;font-weight:700;font-size:1rem;cursor:pointer;">' +
                'Unlock for ' + _esc(amount) + ' &rarr;' +
              '</button>' +
              '<p style="margin:12px 0 0;font-size:0.8rem;color:#065f46;">One-time payment &middot; Yours to keep</p>' +
            '</div>';

        // Show the slot if it was hidden
        slot.style.display = 'block';
    }

    // ---------- inline report renderer ----------

    function _renderList(items, labelKey) {
        if (!Array.isArray(items) || !items.length) return '';
        return '<ul style="padding-left:20px;margin:8px 0;">' + items.map(function (it) {
            if (typeof it === 'string') return '<li>' + _esc(it) + '</li>';
            if (typeof it === 'object' && it !== null) {
                var label = it[labelKey] || '';
                var rest = Object.keys(it).filter(function (k) { return k !== labelKey; })
                    .map(function (k) { return '<strong>' + _esc(k) + ':</strong> ' + _esc(it[k]); })
                    .join(' ');
                return '<li><em>' + _esc(label) + '</em> &mdash; ' + rest + '</li>';
            }
            return '<li>' + _esc(String(it)) + '</li>';
        }).join('') + '</ul>';
    }

    function _renderReport(report, testType, reportId) {
        var slot = document.getElementById(cfg.slotId);
        if (!slot) return;

        var h = '';
        h += '<div id="idrReport" style="margin-top:24px;background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:28px;">';

        // Header
        h += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid #10b981;">';
        h += '<div><h3 style="margin:0;color:#065f46;">Your IELTS ' + _esc(testType.charAt(0).toUpperCase() + testType.slice(1)) + ' Deep Report</h3>';
        h += '<p style="margin:4px 0 0;color:#6b7280;font-size:0.85rem;">Report ID: ' + _esc(reportId) + '</p></div>';
        h += '<a href="/api/ielts/deep-report/' + _esc(reportId) + '.pdf" target="_blank" style="background:#065f46;color:#fff;text-decoration:none;padding:10px 18px;border-radius:6px;font-weight:600;">Download PDF</a>';
        h += '</div>';

        // Summary
        if (report.summary) {
            h += '<div style="background:#f0fdf4;border-left:4px solid #10b981;padding:14px 18px;border-radius:6px;margin-bottom:20px;">';
            h += '<div style="font-weight:700;color:#065f46;margin-bottom:4px;">Summary</div>';
            h += '<div style="color:#374151;line-height:1.6;">' + _esc(report.summary) + '</div></div>';
        }

        // Sub-band reasoning
        if (report.sub_band_reasoning && typeof report.sub_band_reasoning === 'object') {
            h += '<h4 style="margin:24px 0 10px;color:#1e40af;">Sub-band reasoning</h4>';
            Object.keys(report.sub_band_reasoning).forEach(function (k) {
                var label = k.replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
                h += '<div style="margin-bottom:12px;"><div style="font-weight:600;color:#374151;">' + _esc(label) + '</div>';
                h += '<div style="color:#6b7280;font-size:0.9rem;line-height:1.5;">' + _esc(report.sub_band_reasoning[k]) + '</div></div>';
            });
        }

        // Grammar corrections
        if (Array.isArray(report.grammar_corrections) && report.grammar_corrections.length) {
            h += '<h4 style="margin:24px 0 10px;color:#1e40af;">Grammar corrections</h4>';
            h += '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">';
            report.grammar_corrections.forEach(function (g, i) {
                h += '<tr style="border-bottom:1px solid #f3f4f6;">';
                h += '<td style="padding:10px 6px;vertical-align:top;color:#9ca3af;width:30px;">' + (i + 1) + '</td>';
                h += '<td style="padding:10px 6px;vertical-align:top;">';
                h += '<div style="color:#dc2626;"><s>' + _esc(g.original || '') + '</s></div>';
                h += '<div style="color:#059669;font-weight:600;">' + _esc(g.corrected || '') + '</div>';
                h += '<div style="color:#6b7280;font-size:0.82rem;margin-top:4px;"><em>' + _esc(g.rule || '') + '</em> &mdash; ' + _esc(g.explanation || '') + '</div>';
                h += '</td></tr>';
            });
            h += '</table>';
        }

        // Vocabulary upgrades
        if (Array.isArray(report.vocabulary_upgrades) && report.vocabulary_upgrades.length) {
            h += '<h4 style="margin:24px 0 10px;color:#1e40af;">Vocabulary upgrades</h4>';
            h += '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">';
            report.vocabulary_upgrades.forEach(function (v) {
                var better = Array.isArray(v.better) ? v.better.join(', ') : (v.better || '');
                h += '<tr style="border-bottom:1px solid #f3f4f6;">';
                h += '<td style="padding:10px 6px;color:#dc2626;">' + _esc(v.original || '') + '</td>';
                h += '<td style="padding:10px 6px;color:#059669;font-weight:600;">' + _esc(better) + '</td>';
                h += '<td style="padding:10px 6px;color:#6b7280;font-size:0.82rem;">' + _esc(v.context || '') + '</td>';
                h += '</tr>';
            });
            h += '</table>';
        }

        // Example high-band rewrite (writing)
        if (report.example_high_band_rewrite && typeof report.example_high_band_rewrite === 'object') {
            h += '<h4 style="margin:24px 0 10px;color:#1e40af;">Example high-band rewrite</h4>';
            ['paragraph_1', 'paragraph_2'].forEach(function (k, i) {
                if (report.example_high_band_rewrite[k]) {
                    h += '<div style="background:#f8fafc;border-left:3px solid #64748b;padding:12px 16px;margin-bottom:10px;border-radius:4px;">';
                    h += '<div style="font-weight:600;color:#64748b;font-size:0.8rem;margin-bottom:6px;">PARAGRAPH ' + (i + 1) + '</div>';
                    h += '<div style="color:#374151;line-height:1.6;">' + _esc(report.example_high_band_rewrite[k]) + '</div></div>';
                }
            });
        }

        // Example high-band answer (speaking)
        if (report.example_high_band_answer && report.example_high_band_answer.band_8_answer) {
            h += '<h4 style="margin:24px 0 10px;color:#1e40af;">Example high-band answer</h4>';
            h += '<div style="background:#f8fafc;border-left:3px solid #64748b;padding:12px 16px;border-radius:4px;">';
            if (report.example_high_band_answer.question) {
                h += '<div style="color:#64748b;font-size:0.85rem;margin-bottom:6px;"><em>Q: ' + _esc(report.example_high_band_answer.question) + '</em></div>';
            }
            h += '<div style="color:#374151;line-height:1.6;">' + _esc(report.example_high_band_answer.band_8_answer) + '</div></div>';
        }

        // Response by response (speaking)
        if (Array.isArray(report.response_by_response) && report.response_by_response.length) {
            h += '<h4 style="margin:24px 0 10px;color:#1e40af;">Response-by-response review</h4>';
            report.response_by_response.forEach(function (r) {
                h += '<div style="background:#f9fafb;border-radius:6px;padding:12px 16px;margin-bottom:10px;">';
                h += '<div style="font-weight:600;color:#374151;">Part ' + _esc(r.part || '?') + ': ' + _esc((r.question || '').slice(0, 100)) + '</div>';
                if (r.strength) h += '<div style="color:#059669;font-size:0.88rem;margin-top:4px;">&#10003; ' + _esc(r.strength) + '</div>';
                if (r.improvement) h += '<div style="color:#dc2626;font-size:0.88rem;margin-top:2px;">&#9888; ' + _esc(r.improvement) + '</div>';
                h += '</div>';
            });
        }

        // Pronunciation notes (speaking)
        if (Array.isArray(report.pronunciation_notes) && report.pronunciation_notes.length) {
            h += '<h4 style="margin:24px 0 10px;color:#1e40af;">Pronunciation notes</h4>';
            report.pronunciation_notes.forEach(function (p) {
                h += '<div style="margin-bottom:10px;"><div style="font-weight:600;color:#374151;">' + _esc(p.sounds || '') + '</div>';
                h += '<div style="color:#6b7280;font-size:0.88rem;">' + _esc(p.tip || '') + '</div></div>';
            });
        }

        // Common pitfalls
        if (Array.isArray(report.common_pitfalls) && report.common_pitfalls.length) {
            h += '<h4 style="margin:24px 0 10px;color:#1e40af;">Common pitfalls in this attempt</h4>';
            h += '<ul style="padding-left:20px;color:#374151;line-height:1.7;">';
            report.common_pitfalls.forEach(function (p) {
                h += '<li>' + _esc(p) + '</li>';
            });
            h += '</ul>';
        }

        // Exercises
        if (Array.isArray(report.exercises) && report.exercises.length) {
            h += '<h4 style="margin:24px 0 10px;color:#1e40af;">Recommended exercises</h4>';
            report.exercises.forEach(function (ex, i) {
                h += '<div style="background:#fffbeb;border-left:3px solid #f59e0b;padding:12px 16px;margin-bottom:10px;border-radius:4px;">';
                h += '<div style="font-weight:700;color:#92400e;">' + (i + 1) + '. ' + _esc(ex.topic || '') + '</div>';
                if (ex.task) h += '<div style="color:#374151;font-size:0.9rem;margin-top:4px;">' + _esc(ex.task) + '</div>';
                if (ex.rationale) h += '<div style="color:#6b7280;font-size:0.82rem;margin-top:2px;"><em>' + _esc(ex.rationale) + '</em></div>';
                h += '</div>';
            });
        }

        // Email note
        h += '<div style="margin-top:20px;padding:12px 16px;background:#eff6ff;border-radius:6px;color:#1e40af;font-size:0.9rem;">';
        h += '&#9993; A copy has been emailed to <strong>' + _esc(cfg.getEmail ? cfg.getEmail() : '') + '</strong>.';
        h += '</div>';

        h += '</div>';

        // Replace slot content with the report (keeps CTA above it gone)
        slot.innerHTML = '<div style="margin-top:12px;"><a href="#scoreCard" style="color:#6b7280;font-size:0.85rem;">&larr; Back to scorecard</a></div>' + h;
        document.getElementById('idrReport').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // ---------- payment scripts ----------

    function _ensureRazorpay() {
        return new Promise(function (resolve, reject) {
            if (razorpayLoaded || typeof window.Razorpay === 'function') { resolve(); return; }
            var s = document.createElement('script');
            s.src = 'https://checkout.razorpay.com/v1/checkout.js';
            s.onload = function () { razorpayLoaded = true; resolve(); };
            s.onerror = reject;
            document.head.appendChild(s);
        });
    }

    function _ensurePayPal() {
        return new Promise(function (resolve, reject) {
            if (paypalLoaded || (window.paypal && window.paypal.Buttons)) { resolve(); return; }
            // Fetch the public client_id from /api/payment/status
            fetch('/api/payment/status').then(function (r) { return r.json(); }).then(function (j) {
                var cid = j && j.paypal_client_id;
                if (!cid) { reject(new Error('PayPal not configured')); return; }
                var s = document.createElement('script');
                s.src = 'https://www.paypal.com/sdk/js?client-id=' + encodeURIComponent(cid) + '&currency=USD';
                s.onload = function () { paypalLoaded = true; resolve(); };
                s.onerror = reject;
                document.head.appendChild(s);
            }).catch(reject);
        });
    }

    // ---------- Razorpay flow ----------

    async function _unlockViaRazorpay(order) {
        await _ensureRazorpay();
        return new Promise(function (resolve, reject) {
            var rzp = new window.Razorpay({
                key: order.key_id,
                amount: Math.round(order.amount * 100),
                currency: order.currency,
                name: 'Charvak IT Consulting',
                description: 'IELTS Deep Report - ' + cfg.testType,
                order_id: order.order_id,
                prefill: { email: cfg.getEmail() },
                theme: { color: '#10b981' },
                handler: function (resp) {
                    resolve({
                        gateway: 'razorpay',
                        razorpay_payment_id: resp.razorpay_payment_id,
                        razorpay_order_id: resp.razorpay_order_id,
                        razorpay_signature: resp.razorpay_signature,
                    });
                },
                modal: { ondismiss: function () { reject(new Error('Payment cancelled')); } },
            });
            rzp.open();
        });
    }

    // ---------- PayPal flow ----------

    async function _unlockViaPayPal(order) {
        await _ensurePayPal();
        return new Promise(function (resolve, reject) {
            // PayPal uses a redirect-style flow inside a modal
            var container = document.createElement('div');
            container.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;';
            var inner = document.createElement('div');
            inner.style.cssText = 'background:#fff;border-radius:12px;padding:20px;max-width:420px;width:90%;';
            inner.innerHTML = '<h5 style="margin:0 0 12px;">Complete your payment</h5><div id="idrPaypalSlot"></div><div id="idrPaypalStatus" style="color:#6b7280;font-size:0.85rem;margin-top:8px;"></div>';
            container.appendChild(inner);
            document.body.appendChild(container);

            window.paypal.Buttons({
                createOrder: function () { return order.order_id; },
                onApprove: function (data) {
                    // In PayPal's flow, the order is already created and approved.
                    // We just need to capture it (server-side or client-side).
                    return fetch('/api/payment/paypal/capture', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ order_id: data.orderID }),
                    }).then(function (r) { return r.json(); }).then(function (j) {
                        if (j.status !== 'success') {
                            document.getElementById('idrPaypalStatus').textContent = 'Capture failed. Contact support.';
                            reject(new Error('PayPal capture failed'));
                            return;
                        }
                        document.body.removeChild(container);
                        resolve({ gateway: 'paypal', paypal_order_id: data.orderID });
                    });
                },
                onError: function (err) {
                    document.body.removeChild(container);
                    reject(err);
                },
            }).render('#idrPaypalSlot');
        });
    }

    // ---------- unlock (public) ----------

    async function unlock() {
        var btn = document.getElementById('idrUnlockBtn');
        if (btn) { btn.disabled = true; btn.textContent = 'Opening checkout\u2026'; }

        try {
            var sessionId = cfg.getSessionId ? cfg.getSessionId() : null;
            var email = cfg.getEmail ? cfg.getEmail() : '';
            if (!sessionId) throw new Error('Session missing. Take the free eval first.');
            if (!email) throw new Error('Please log in first.');

            // 1. Create order
            var cr = await _fetch('/api/ielts/deep-report/create-order', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: sessionId,
                    test_type: cfg.testType,
                    email: email,
                    country_code: (priceInfo && priceInfo.country_code) || '',
                }),
            });
            var order = await cr.json();
            if (order.status !== 'success') {
                throw new Error(order.message || 'Could not create order.');
            }

            // 2. Open gateway
            var payment;
            if (order.gateway === 'razorpay') {
                payment = await _unlockViaRazorpay(order);
            } else if (order.gateway === 'paypal') {
                payment = await _unlockViaPayPal(order);
            } else {
                throw new Error('Unknown gateway: ' + order.gateway);
            }

            // 3. Run (verify + generate)
            if (btn) { btn.textContent = 'Generating report\u2026 (30-60s)'; }
            var runPayload = Object.assign({
                report_id: order.report_id,
                session_id: sessionId,
                test_type: cfg.testType,
                email: email,
            }, payment);

            var rr = await _fetch('/api/ielts/deep-report/run', {
                method: 'POST',
                body: JSON.stringify(runPayload),
            });
            var runResult = await rr.json();
            if (runResult.status !== 'success') {
                throw new Error(runResult.message || 'Could not generate report.');
            }

            // 4. Render inline
            _renderReport(runResult.report, cfg.testType, order.report_id);

        } catch (e) {
            if (btn) { btn.disabled = false; btn.textContent = 'Unlock for ' + (priceInfo ? priceInfo.amount_display : '\u20B999') + ' \u2192'; }
            alert('Could not complete: ' + e.message);
        }
    }

    // ---------- init (public) ----------

    function init(config) {
        cfg = config || {};
        if (!cfg.slotId || !cfg.getSessionId || !cfg.testType) {
            console.warn('[IeltsDeepReport] missing config', cfg);
            return;
        }
        _loadPrice().then(function () { _renderCta(); });
    }

    return { init: init, unlock: unlock };
})();