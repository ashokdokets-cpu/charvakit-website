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

    global.CharvakIntegrity = {
        init: init,
        // Exposed for tests that want to force a flush
        _flush: flush
    };

})(window);