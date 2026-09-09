// Charvak Currency Utility
var CharvakCurrency = {
    current: 'INR',
    rates: {INR: 1, USD: 83.1, EUR: 90.2, GBP: 105.3, AED: 22.6, SGD: 61.2, AUD: 54.8, CAD: 61.0, JPY: 0.56, CNY: 11.5, BRL: 16.8, NGN: 0.055, ZAR: 4.45},
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
                var converted = inrAmount / rate;
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
