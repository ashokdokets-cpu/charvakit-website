// Charvak Currency Utility
var CharvakCurrency = {
    current: 'INR',
    rates: {INR: 1, USD: 0.012, EUR: 0.011, GBP: 0.0095, AED: 0.044, SGD: 0.016, AUD: 0.018, CAD: 0.016, JPY: 1.75, CNY: 0.087, BRL: 0.059, NGN: 18.5, ZAR: 0.22},
    symbols: {INR: '₹', USD: '$', EUR: '€', GBP: '£', AED: 'د.إ', SGD: 'S$', AUD: 'A$', CAD: 'C$', JPY: '¥', CNY: '¥', BRL: 'R$', NGN: '₦', ZAR: 'R'},
    
    init: function() {
        var saved = localStorage.getItem('charvak_currency');
        if (saved) {
            this.current = saved;
        }
        this.updateSelector();
    },
    
    getCurrent: function() {
        return this.current;
    },
    
    setCurrency: function(currency) {
        this.current = currency;
        localStorage.setItem('charvak_currency', currency);
        this.updateSelector();
        this.updateAllPrices();
        window.dispatchEvent(new CustomEvent('charvakCurrencyChanged', {detail: {currency: currency}}));
    },
    
    getSymbol: function() {
        return this.symbols[this.current] || '₹';
    },
    
    getRate: function() {
        return this.rates[this.current] || 1;
    },
    

    getName: function(code) {
        var names = {
            INR: 'Indian Rupee', USD: 'US Dollar', EUR: 'Euro',
            GBP: 'British Pound', AED: 'UAE Dirham', SGD: 'Singapore Dollar',
            AUD: 'Australian Dollar', CAD: 'Canadian Dollar', JPY: 'Japanese Yen',
            CNY: 'Chinese Yuan', BRL: 'Brazilian Real', NGN: 'Nigerian Naira',
            ZAR: 'South African Rand'
        };
        return names[code || this.current] || code || this.current;
    },

    format: function(inrAmount) {
        var rate = this.getRate();
        var symbol = this.getSymbol();
        var converted = (parseFloat(inrAmount) || 0) * rate;
        // Round appropriately: for high-rate currencies show integer, else keep
        if (rate >= 1) {
            return symbol + Math.round(converted).toLocaleString('en-IN');
        }
        return symbol + converted.toFixed(2);
    },

    detectLocation: async function() {
        // URL override takes priority over everything (?country=US forces US)
        var urlParams = new URLSearchParams(window.location.search);
        var forceCountry = urlParams.get('country');
        
        if (forceCountry) {
            try {
                var forceUrl = '/api/region?country=' + encodeURIComponent(forceCountry);
                var forceRes = await fetch(forceUrl);
                var forceData = await forceRes.json();
                if (forceData && forceData.currency && this.rates[forceData.currency]) {
                    this.current = forceData.currency;
                    localStorage.setItem('charvak_currency', forceData.currency);
                    this.updateSelector();
                    this.updateAllPrices();
                    return forceData.currency;
                }
            } catch (e) {
                console.warn('URL country override failed:', e);
            }
            // If override failed, fall through to saved preference
        }

        // Try saved preference next
        var saved = localStorage.getItem('charvak_currency');
        if (saved && this.rates[saved]) {
            this.current = saved;
            this.updateSelector();
            this.updateAllPrices();
            return saved;
        }

        // Finally, ask the server
        try {
            var res = await fetch('/api/region');
            var data = await res.json();
            if (data && data.currency && this.rates[data.currency]) {
                this.current = data.currency;
                localStorage.setItem('charvak_currency', data.currency);
                this.updateSelector();
                this.updateAllPrices();
                return data.currency;
            }
        } catch (e) {
            console.warn('detectLocation failed:', e);
        }
        return this.current;
    },

    updateSelector: function() {
        var selector = document.getElementById('currencySelector');
        if (selector) {
            selector.value = this.current;
        }
    },
    
    updateAllPrices: function() {
        var symbol = this.getSymbol();
        var rate = this.getRate();
        var currency = this.current;
        document.querySelectorAll('[data-inr]').forEach(function(el) {
            var inrAmount = parseFloat(el.getAttribute('data-inr'));
            if (inrAmount && rate) {
                // Prefer explicit per-currency data attributes if present
                var explicit = el.getAttribute('data-' + currency.toLowerCase());
                if (explicit) {
                    el.textContent = symbol + explicit;
                    return;
                }
                // Fallback: convert from INR
                var converted = inrAmount * rate;
                // High-rate currencies (JPY, INR, NGN, ZAR) show integers
                // Low-rate currencies (USD, EUR, GBP) show 2 decimals
                if (rate >= 10) {
                    el.textContent = symbol + Math.round(converted).toLocaleString();
                } else if (rate >= 1) {
                    el.textContent = symbol + Math.round(converted).toLocaleString();
                } else {
                    el.textContent = symbol + converted.toFixed(2);
                }
            }
        });
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    CharvakCurrency.init();
    // Detect region (respects ?country= URL override, then localStorage, then /api/region)
    CharvakCurrency.detectLocation().catch(function(e) {
        console.warn('Region detection skipped:', e);
    });
});

// Listen for currency changes
window.addEventListener('charvakCurrencyChange', function(e) {
    if (e.detail && e.detail.currency) {
        CharvakCurrency.setCurrency(e.detail.currency);
    }
});
