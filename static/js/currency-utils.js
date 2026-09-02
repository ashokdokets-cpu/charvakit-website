/**
 * Charvak IT Consulting - Global Currency Utilities
 * Supports 13 currencies with real-time conversion and location detection
 * Version: 2.0.0 - Unified currency system
 */

const CharvakCurrency = {
    rates: {
        INR: 1, USD: 83.1, EUR: 90.2, GBP: 105.3, AED: 22.6,
        SGD: 61.2, AUD: 54.8, CAD: 61.0, JPY: 0.56, CNY: 11.5,
        BRL: 16.8, NGN: 0.055, ZAR: 4.45
    },
    
    symbols: {
        INR: '₹', USD: '$', EUR: '€', GBP: '£', AED: 'د.إ',
        SGD: 'S$', AUD: 'A$', CAD: 'C$', JPY: '¥', CNY: '¥',
        BRL: 'R$', NGN: '₦', ZAR: 'R'
    },
    
    names: {
        INR: 'Indian Rupee', USD: 'US Dollar', EUR: 'Euro',
        GBP: 'British Pound', AED: 'UAE Dirham', SGD: 'Singapore Dollar',
        AUD: 'Australian Dollar', CAD: 'Canadian Dollar', JPY: 'Japanese Yen',
        CNY: 'Chinese Yuan', BRL: 'Brazilian Real', NGN: 'Nigerian Naira',
        ZAR: 'South African Rand'
    },
    
    getCurrent() {
        return localStorage.getItem('charvak_currency') || 'INR';
    },
    
    setCurrency(currency) {
        if (this.rates[currency]) {
            localStorage.setItem('charvak_currency', currency);
            this.updateAllPrices();
            
            // Dispatch event
            window.dispatchEvent(new CustomEvent('charvakCurrencyChanged', {
                detail: { currency: currency }
            }));
            
            // Show notification
            this.showNotification(`Currency: ${this.symbols[currency]} ${currency} (${this.names[currency]})`);
            
            return true;
        }
        return false;
    },
    
    convert(inrAmount) {
        const currency = this.getCurrent();
        if (currency === 'INR') return inrAmount;
        const rate = this.rates[currency];
        if (!rate) return inrAmount;
        return inrAmount / rate;
    },
    
    format(inrAmount) {
        const converted = this.convert(inrAmount);
        const currency = this.getCurrent();
        const symbol = this.symbols[currency] || '$';
        
        let formatted;
        if (['JPY', 'NGN', 'ZAR', 'CNY'].includes(currency)) {
            formatted = Math.round(converted).toLocaleString();
        } else if (['INR', 'AED', 'BRL'].includes(currency)) {
            formatted = Math.round(converted).toLocaleString();
        } else {
            formatted = converted.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }
        
        return symbol + formatted;
    },
    
    getSymbol() {
        return this.symbols[this.getCurrent()] || '$';
    },
    
    getName() {
        return this.names[this.getCurrent()] || 'US Dollar';
    },
    
    updateAllPrices() {
        document.querySelectorAll('[data-inr]').forEach(el => {
            const inrAmount = parseFloat(el.getAttribute('data-inr'));
            if (inrAmount) {
                el.textContent = this.format(inrAmount);
            }
        });
    },
    
    showNotification(msg) {
        const div = document.createElement('div');
        div.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#3ba591;color:#fff;padding:10px 20px;border-radius:5px;z-index:9999;';
        div.textContent = msg;
        document.body.appendChild(div);
        setTimeout(() => div.remove(), 3000);
    },
    
    async detectLocation() {
        // Default to INR (Charvak is Indian company)
        const existing = localStorage.getItem('charvak_currency');
        if (existing) {
            this.updateAllPrices();
            return existing;
        }
        
        localStorage.setItem('charvak_currency', 'INR');
        this.updateAllPrices();
        console.log('Default currency: INR');
        return 'INR';
    },
    
    async init() {
    // Set INR as default if no currency selected
    if (!localStorage.getItem('charvak_currency')) {
        localStorage.setItem('charvak_currency', 'INR');
    }
    this.updateAllPrices();
    
    // Update currency dropdown
    const selector = document.getElementById('currencySelector');
    if (selector) {
        selector.value = this.getCurrent();
    }
}
        
        // Listen for changes from other scripts
        window.addEventListener('charvakCurrencyChange', (e) => {
            if (e.detail && e.detail.currency) {
                this.setCurrency(e.detail.currency);
            }
        });
    }
};

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => CharvakCurrency.init());
} else {
    CharvakCurrency.init();
}
