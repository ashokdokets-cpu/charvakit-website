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
        // Try saved preference first
        var saved = localStorage.getItem('charvak_currency');
        if (saved && this.rates[saved]) {
            this.current = saved;
            this.updateSelector();
            this.updateAllPrices();
            return saved;
        }
        // Fetch region from server (with dev override support)
        try {
            var urlParams = new URLSearchParams(window.location.search);
            var forceCountry = urlParams.get('country');
            var regionUrl = '/api/region' + (forceCountry ? ('?country=' + encodeURIComponent(forceCountry)) : '');
            var res = await fetch(regionUrl);
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
        document.querySelectorAll('[data-inr]').forEach(function(el) {
            var inrAmount = parseFloat(el.getAttribute('data-inr'));
            if (inrAmount && rate) {
                var converted = inrAmount * rate;
                el.textContent = symbol + Math.round(converted);
            }
        });
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    CharvakCurrency.init();
});

// Listen for currency changes
window.addEventListener('charvakCurrencyChange', function(e) {
    if (e.detail && e.detail.currency) {
        CharvakCurrency.setCurrency(e.detail.currency);
    }
});
