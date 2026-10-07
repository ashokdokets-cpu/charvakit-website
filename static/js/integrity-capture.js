/* ========================================================================
 * Charvak Integrity Capture
 * ========================================================================
 * Session 27 shipped environment-signal capture for Career Assessments.
 * Session 39 extracted it into this shared helper so any assessment can
 * opt in with a small init() call.
 *
 * RECORD ONLY. Nothing is blocked. Every failure path is silent.
 *
 * Events recorded:
 *   - paste        (into any text field)
 *   - contextmenu  (right-click, which can be used to paste)
 *   - tab_switch   (via visibilitychange + window blur/focus)
 *   - focus_out    (input/textarea loses focus mid-answer)
 *   - rapid_input  (>= 100 chars in < 200ms = synthetic typing)
 *
 * Flush strategy:
 *   - Batched every 2 seconds
 *   - Beacon-style keepalive fetch on pagehide/beforeunload
 *
 * Usage:
 *   CharvakIntegrity.init({
 *       getAssessmentId: function() {
 *           return window._carCurrentAssessment?.assessment_id || null;
 *       }
 *   });
 *
 * The getAssessmentId callback is called on every event. It must return
 * a non-null string when an assessment is active, or null/undefined
 * when there is nothing to record. Events are dropped when null.
 * ======================================================================== */

(function (global) {
    'use strict';

    // --- Configuration -------------------------------------------------
    var CONFIG = {
        endpoint: '/api/integrity/event',
        flushIntervalMs: 2000,
        maxQueueSize: 50,
        rapidInputWindowMs: 500,   // window reset for ordinary typing
        rapidInputBurstMs: 200,    // delta must be under this to flag
        rapidInputBurstChars: 100  // and at least this many chars
    };

    // --- State ---------------------------------------------------------
    var _initialized = false;
    var _getAssessmentId = null;

    var queue = [];
    var flushTimer = null;

    var tabHiddenAt = null;
    var blurAt = null;
    var lastKey = {};

    // --- Storage accessors --------------------------------------------

    function getEmail() {
        try {
            return (localStorage.getItem('userEmail') || '').trim().toLowerCase();
        } catch (e) {
            return '';
        }
    }

    function getToken() {
        try {
            return localStorage.getItem('auth_token')
                || localStorage.getItem('charvak_token')
                || '';
        } catch (e) {
            return '';
        }
    }

    function getActiveAid() {
        try {
            if (typeof _getAssessmentId !== 'function') return null;
            var aid = _getAssessmentId();
            if (!aid || typeof aid !== 'string') return null;
            return aid.trim() || null;
        } catch (e) {
            return null;
        }
    }

    // --- Queue + flush -------------------------------------------------

    function queueEvent(type, metadata) {
        var aid = getActiveAid();
        if (!aid) return;
        var email = getEmail();
        var token = getToken();
        if (!email || !token) return;

        queue.push({
            email: email,
            assessment_id: aid,
            event_type: type,
            metadata: metadata || {},
            _token: token
        });
        if (queue.length > CONFIG.maxQueueSize) queue.shift();

        if (!flushTimer) {
            flushTimer = setTimeout(flush, CONFIG.flushIntervalMs);
        }
    }

    function sendOne(ev) {
        var body = JSON.stringify({
            email: ev.email,
            assessment_id: ev.assessment_id,
            event_type: ev.event_type,
            metadata: ev.metadata
        });
        try {
            fetch(CONFIG.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + ev._token
                },
                body: body,
                keepalive: true
            }).catch(function () { /* silent */ });
        } catch (e) { /* silent */ }
    }

    function flush() {
        flushTimer = null;
        if (!queue.length) return;
        var batch = queue.slice();
        queue = [];
        batch.forEach(sendOne);
    }

    function flushBeacon() {
        if (!queue.length) return;
        var batch = queue.slice();
        queue = [];
        batch.forEach(sendOne);
    }

    // --- Event handlers ------------------------------------------------

    function onPaste(e) {
        if (!getActiveAid()) return;
        var t = e.target || {};
        var chars = 0;
        try {
            if (e.clipboardData && e.clipboardData.getData) {
                chars = (e.clipboardData.getData('text') || '').length;
            }
        } catch (err) { /* ignore */ }
        queueEvent('paste', {
            target_id: t.id || t.name || t.tagName || 'unknown',
            chars: chars
        });
    }

    function onContextMenu(e) {
        if (!getActiveAid()) return;
        var t = e.target || {};
        queueEvent('contextmenu', {
            target_id: t.id || t.name || t.tagName || 'unknown'
        });
    }

    function onVisibilityChange() {
        if (!getActiveAid()) return;
        if (document.hidden) {
            tabHiddenAt = Date.now();
        } else {
            var dur = tabHiddenAt ? (Date.now() - tabHiddenAt) : 0;
            tabHiddenAt = null;
            queueEvent('tab_switch', { duration_ms: dur });
        }
    }

    function onBlur() {
        if (!getActiveAid()) return;
        blurAt = Date.now();
    }

    function onFocus() {
        if (!getActiveAid()) return;
        if (blurAt) {
            var dur = Date.now() - blurAt;
            blurAt = null;
            if (!tabHiddenAt) {
                queueEvent('tab_switch', { duration_ms: dur, source: 'window' });
            }
        }
    }

    function onFocusOut(e) {
        if (!getActiveAid()) return;
        var t = e.target || {};
        var tag = (t.tagName || '').toLowerCase();
        if (tag === 'textarea' || tag === 'input') {
            queueEvent('focus_out', {
                target_id: t.id || t.name || tag
            });
        }
    }

    function onInput(e) {
        if (!getActiveAid()) return;
        var t = e.target || {};
        var tag = (t.tagName || '').toLowerCase();
        if (tag !== 'textarea' && tag !== 'input') return;

        var now = Date.now();
        var key = t.id || t.name || tag;
        var entry = lastKey[key];

        if (!entry) {
            lastKey[key] = { t0: now, chars: (t.value || '').length };
            return;
        }
        var deltaMs = now - entry.t0;
        var deltaChars = (t.value || '').length - entry.chars;

        if (deltaMs >= CONFIG.rapidInputWindowMs) {
            lastKey[key] = { t0: now, chars: (t.value || '').length };
            return;
        }

        if (deltaChars >= CONFIG.rapidInputBurstChars && deltaMs < CONFIG.rapidInputBurstMs) {
            var cpm = deltaMs > 0 ? (deltaChars / deltaMs) : deltaChars;
            queueEvent('rapid_input', {
                target_id: key,
                chars: deltaChars,
                window_ms: deltaMs,
                chars_per_ms: Math.round(cpm * 100) / 100
            });
            lastKey[key] = { t0: now, chars: (t.value || '').length };
        }
    }

    // --- Public API ----------------------------------------------------

    function init(options) {
        if (_initialized) {
            // Re-init is a no-op. Silent.
            return;
        }
        options = options || {};
        if (typeof options.getAssessmentId !== 'function') {
            // Without a getter there is nothing to guard against.
            // Silent no-op - callers that misconfigure simply get no capture.
            return;
        }
        _getAssessmentId = options.getAssessmentId;
        _initialized = true;

        // Attach listeners once. Using capture phase for paste/contextmenu/
        // focusout/input so we see events before any bubble-phase handlers.
        document.addEventListener('paste', onPaste, true);
        document.addEventListener('contextmenu', onContextMenu, true);
        document.addEventListener('visibilitychange', onVisibilityChange);
        window.addEventListener('blur', onBlur);
        window.addEventListener('focus', onFocus);
        document.addEventListener('focusout', onFocusOut, true);
        document.addEventListener('input', onInput, true);

        // Periodic flush (belt) + teardown flush (suspenders)
        setInterval(flush, CONFIG.flushIntervalMs);
        window.addEventListener('pagehide', flushBeacon);
        window.addEventListener('beforeunload', flushBeacon);

        // Debug hook - harmless in prod, useful in dev
        global.__integrityDebug = {
            queue: function () { return queue.slice(); },
            flush: flush,
            activeAid: getActiveAid,
            isInitialized: function () { return _initialized; }
        };
    }

    // ========================================================================
    // Session 39-7a - Shared Trust Score badge renderer
    // ========================================================================
    // Renders the badge into a target slot by ID. Injects the CSS once.
    // Silent-fail on any error. Idempotent CSS injection.
    //
    // Usage:
    //   CharvakIntegrity.renderBadge({
    //       slotId: 'mdIntegritySlot',
    //       assessmentId: 'MOCK-1234...'
    //   });
    // ========================================================================

    var _badgeCssInjected = false;

    function _injectBadgeCss() {
        if (_badgeCssInjected) return;
        if (document.getElementById('charvak-integrity-badge-css')) {
            _badgeCssInjected = true;
            return;
        }
        var style = document.createElement('style');
        style.id = 'charvak-integrity-badge-css';
        style.textContent = [
            '.rd-integrity-card { margin-top: 16px; padding: 14px 16px; border-radius: 10px; border-left: 4px solid #9ca3af; background: #f9fafb; display: flex; gap: 12px; align-items: flex-start; }',
            '.rd-integrity-card.clean { border-left-color: #10b981; background: #ecfdf5; }',
            '.rd-integrity-card.minor { border-left-color: #3b82f6; background: #eff6ff; }',
            '.rd-integrity-card.moderate { border-left-color: #f59e0b; background: #fffbeb; }',
            '.rd-integrity-card.elevated { border-left-color: #ef4444; background: #fef2f2; }',
            '.rd-integrity-icon { font-size: 1.6rem; line-height: 1; flex-shrink: 0; }',
            '.rd-integrity-title { font-weight: 700; margin: 0 0 3px; font-size: 1rem; }',
            '.rd-integrity-msg { margin: 0; color: #4b5563; font-size: 0.88rem; }',
            '.rd-integrity-toggle { margin-top: 6px; font-size: 0.82rem; }',
            '.rd-integrity-toggle a { color: #2563eb; text-decoration: none; }',
            '.rd-integrity-toggle a:hover { text-decoration: underline; }',
            '.rd-integrity-explainer { margin-top: 8px; padding: 10px 12px; background: #fff; border-radius: 6px; font-size: 0.82rem; color: #4b5563; display: none; }',
            '.rd-integrity-explainer.open { display: block; }',
            '.rd-integrity-explainer ul { margin: 5px 0 0 0; padding-left: 18px; }'
        ].join('\n');
        document.head.appendChild(style);
        _badgeCssInjected = true;
    }

    function _badgeEsc(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function _toggleExplainer(explainerId) {
        var el = document.getElementById(explainerId);
        if (el) el.classList.toggle('open');
    }

    async function renderBadge(options) {
        options = options || {};
        var slotId = options.slotId;
        var assessmentId = options.assessmentId;
        if (!slotId || !assessmentId) return;

        var slot = document.getElementById(slotId);
        if (!slot) return;

        _injectBadgeCss();

        try {
            var r = await fetch('/api/integrity/public/' + encodeURIComponent(assessmentId));
            if (!r.ok) return;
            var j = await r.json();
            if (j.status !== 'success') return;

            var level = j.risk_level || 'clean';
            var icons = {
                'clean':    '\uD83D\uDEE1\uFE0F',
                'minor':    '\u2139\uFE0F',
                'moderate': '\u26A0\uFE0F',
                'elevated': '\uD83D\uDEA8'
            };
            var titles = {
                'clean':    'Integrity Verified',
                'minor':    'Minor signals detected',
                'moderate': 'Multiple signals detected',
                'elevated': 'Frequent signals detected'
            };

            var explainerId = slotId + 'Explainer';
            var html = '';
            html += '<div class="rd-integrity-card ' + _badgeEsc(level) + '">';
            html += '<div class="rd-integrity-icon">' + (icons[level] || icons.clean) + '</div>';
            html += '<div class="flex-grow-1">';
            html += '<p class="rd-integrity-title">' + _badgeEsc(titles[level] || 'Integrity status') + '</p>';
            html += '<p class="rd-integrity-msg">' + _badgeEsc(j.message || '') + '</p>';
            html += '<div class="rd-integrity-toggle"><a href="#" onclick="CharvakIntegrity._toggleExplainer(\'' + explainerId + '\');return false;">What does this mean?</a></div>';
            html += '<div class="rd-integrity-explainer" id="' + _badgeEsc(explainerId) + '">';
            html += '<strong>How to read this signal</strong>';
            html += '<ul>';
            html += '<li><b>What we capture:</b> paste events, tab switches, focus loss, and rapid input during the assessment.</li>';
            html += '<li><b>What it means:</b> these are signals, not verdicts.</li>';
            html += '<li><b>What it doesn\'t mean:</b> this is one data point alongside the score.</li>';
            html += '<li><b>Verified</b> (green) means no signals were detected.</li>';
            html += '</ul>';
            html += '</div>';
            html += '</div></div>';

            slot.innerHTML = html;
        } catch (e) {
            // silent — badge simply doesn't render
        }
    }

    // Public helper for the inline onclick above
    function _toggleExplainerPublic(id) { _toggleExplainer(id); }
    global.CharvakIntegrity = {
        init: init,
        renderBadge: renderBadge,
        _toggleExplainer: _toggleExplainer,
        // Exposed for tests that want to force a flush
        _flush: flush
    };

})(window);