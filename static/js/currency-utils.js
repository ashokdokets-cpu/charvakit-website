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
        // Use browser language (no external API - CSP compliant)
        const lang = navigator.language || navigator.userLanguage || 'en-US';
        
        const langToCurrency = {
            'en-IN': 'INR', 'hi-IN': 'INR', 'ta-IN': 'INR', 'te-IN': 'INR',
            'en-US': 'USD', 'en-GB': 'GBP', 'en-AU': 'AUD', 'en-CA': 'CAD',
            'en-SG': 'SGD', 'en-NZ': 'AUD', 'en-IE': 'EUR', 'en-ZA': 'ZAR',
            'en-NG': 'NGN', 'en-GH': 'NGN', 'en-KE': 'NGN',
            'ja': 'JPY', 'ja-JP': 'JPY',
            'zh': 'CNY', 'zh-CN': 'CNY', 'zh-TW': 'CNY', 'zh-HK': 'CNY',
            'pt': 'BRL', 'pt-BR': 'BRL', 'pt-PT': 'EUR',
            'ar': 'AED', 'ar-AE': 'AED', 'ar-SA': 'AED',
            'de': 'EUR', 'de-DE': 'EUR', 'de-AT': 'EUR', 'de-CH': 'EUR',
            'fr': 'EUR', 'fr-FR': 'EUR', 'fr-BE': 'EUR',
            'it': 'EUR', 'it-IT': 'EUR',
            'es': 'EUR', 'es-ES': 'EUR', 'es-MX': 'USD',
            'nl': 'EUR', 'nl-NL': 'EUR',
            'sv': 'EUR', 'sv-SE': 'EUR',
            'da': 'EUR', 'da-DK': 'EUR',
            'fi': 'EUR', 'fi-FI': 'EUR',
            'pl': 'EUR', 'pl-PL': 'EUR',
            'cs': 'EUR', 'cs-CZ': 'EUR',
            'ro': 'EUR', 'ro-RO': 'EUR',
            'hu': 'EUR', 'hu-HU': 'EUR',
            'el': 'EUR', 'el-GR': 'EUR'
        };
        
        const detected = langToCurrency[lang] || 'USD';
        localStorage.setItem('charvak_currency', detected);
        this.updateAllPrices();
        console.log('Currency detected:', detected, 'from language:', lang);
        return detected;
    },
    
    async init() {
        if (!localStorage.getItem('charvak_currency')) {
            await this.detectLocation();
        }
        this.updateAllPrices();
        
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