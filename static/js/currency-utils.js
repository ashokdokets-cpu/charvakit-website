/**
 * Charvak IT Consulting - Global Currency Utilities
 * Supports 13 currencies with real-time conversion and location detection
 * Version: 1.0.0
 */

const CharvakCurrency = {
    // Currency conversion rates (to INR) - Updated as of 2024
    rates: {
        INR: 1,        // Indian Rupee (Base)
        USD: 83.1,     // US Dollar
        EUR: 90.2,     // Euro
        GBP: 105.3,    // British Pound
        AED: 22.6,     // UAE Dirham
        SGD: 61.2,     // Singapore Dollar
        AUD: 54.8,     // Australian Dollar
        CAD: 61.0,     // Canadian Dollar
        JPY: 0.56,     // Japanese Yen
        CNY: 11.5,     // Chinese Yuan
        BRL: 16.8,     // Brazilian Real
        NGN: 0.055,    // Nigerian Naira
        ZAR: 4.45      // South African Rand
    },

    // Currency symbols
    symbols: {
        INR: '₹',
        USD: '$',
        EUR: '€',
        GBP: '£',
        AED: 'د.إ',
        SGD: 'S$',
        AUD: 'A$',
        CAD: 'C$',
        JPY: '¥',
        CNY: '¥',
        BRL: 'R$',
        NGN: '₦',
        ZAR: 'R'
    },

    // Currency full names
    names: {
        INR: 'Indian Rupee',
        USD: 'US Dollar',
        EUR: 'Euro',
        GBP: 'British Pound',
        AED: 'UAE Dirham',
        SGD: 'Singapore Dollar',
        AUD: 'Australian Dollar',
        CAD: 'Canadian Dollar',
        JPY: 'Japanese Yen',
        CNY: 'Chinese Yuan',
        BRL: 'Brazilian Real',
        NGN: 'Nigerian Naira',
        ZAR: 'South African Rand'
    },

    // Country to currency mapping for location detection
    countryToCurrency: {
        // Asia
        'IN': 'INR', 'US': 'USD', 'GB': 'GBP', 'AE': 'AED',
        'SG': 'SGD', 'AU': 'AUD', 'CA': 'CAD', 'JP': 'JPY',
        'CN': 'CNY', 'BR': 'BRL', 'NG': 'NGN', 'ZA': 'ZAR',
        
        // Europe
        'DE': 'EUR', 'FR': 'EUR', 'IT': 'EUR', 'ES': 'EUR',
        'NL': 'EUR', 'BE': 'EUR', 'IE': 'EUR', 'PT': 'EUR',
        'AT': 'EUR', 'FI': 'EUR', 'GR': 'EUR', 'LU': 'EUR',
        'CH': 'EUR', 'SE': 'EUR', 'NO': 'EUR', 'DK': 'EUR',
        'PL': 'EUR', 'CZ': 'EUR', 'RO': 'EUR', 'HU': 'EUR',
        'BG': 'EUR', 'HR': 'EUR', 'SK': 'EUR', 'SI': 'EUR',
        'LT': 'EUR', 'LV': 'EUR', 'EE': 'EUR', 'CY': 'EUR',
        'MT': 'EUR', 'IS': 'EUR',
        
        // Asia Pacific
        'NZ': 'AUD', 'HK': 'CNY', 'TW': 'CNY', 'MO': 'CNY',
        'MY': 'SGD', 'ID': 'SGD', 'TH': 'SGD', 'VN': 'SGD',
        'PH': 'SGD', 'KR': 'CNY', 'KP': 'CNY', 'MN': 'CNY',
        'LA': 'SGD', 'KH': 'SGD', 'MM': 'SGD', 'BN': 'SGD',
        
        // Middle East
        'SA': 'AED', 'KW': 'AED', 'QA': 'AED', 'BH': 'AED',
        'OM': 'AED', 'YE': 'AED', 'IQ': 'AED', 'SY': 'AED',
        'JO': 'AED', 'LB': 'AED', 'PS': 'AED',
        
        // Africa
        'GH': 'NGN', 'KE': 'NGN', 'TZ': 'NGN', 'UG': 'NGN',
        'ET': 'NGN', 'ZM': 'ZAR', 'ZW': 'ZAR', 'BW': 'ZAR',
        'MZ': 'ZAR', 'NA': 'ZAR', 'LS': 'ZAR', 'SZ': 'ZAR',
        'MW': 'ZAR', 'AO': 'ZAR', 'CG': 'NGN', 'CD': 'NGN',
        'CM': 'NGN', 'SN': 'NGN', 'CI': 'NGN', 'ML': 'NGN',
        'BF': 'NGN', 'NE': 'NGN', 'TD': 'NGN', 'SD': 'NGN',
        'ER': 'NGN', 'DJ': 'NGN', 'SO': 'NGN', 'RW': 'NGN',
        'BI': 'NGN', 'GA': 'NGN', 'GQ': 'NGN', 'ST': 'NGN',
        
        // South America
        'AR': 'BRL', 'CL': 'BRL', 'CO': 'BRL', 'PE': 'BRL',
        'VE': 'BRL', 'EC': 'BRL', 'BO': 'BRL', 'PY': 'BRL',
        'UY': 'BRL', 'GY': 'BRL', 'SR': 'BRL', 'GF': 'BRL',
        
        // North America
        'MX': 'USD', 'GT': 'USD', 'BZ': 'USD', 'SV': 'USD',
        'HN': 'USD', 'NI': 'USD', 'CR': 'USD', 'PA': 'USD',
        'CU': 'USD', 'DO': 'USD', 'HT': 'USD', 'JM': 'USD',
        'TT': 'USD', 'BS': 'USD', 'BB': 'USD', 'LC': 'USD',
        'VC': 'USD', 'GD': 'USD', 'KN': 'USD', 'AG': 'USD',
        'DM': 'USD'
    },

    // Browser language to currency mapping
    browserLangToCurrency: {
        'en-IN': 'INR', 'hi-IN': 'INR', 'ta-IN': 'INR', 'te-IN': 'INR',
        'en-US': 'USD', 'en-GB': 'GBP', 'en-AU': 'AUD', 'en-CA': 'CAD',
        'en-SG': 'SGD', 'en-NZ': 'AUD', 'en-IE': 'EUR', 'en-ZA': 'ZAR',
        'en-NG': 'NGN', 'en-GH': 'NGN', 'en-KE': 'NGN',
        'ja': 'JPY', 'ja-JP': 'JPY',
        'zh': 'CNY', 'zh-CN': 'CNY', 'zh-TW': 'CNY', 'zh-HK': 'CNY',
        'pt': 'BRL', 'pt-BR': 'BRL', 'pt-PT': 'EUR',
        'ar': 'AED', 'ar-AE': 'AED', 'ar-SA': 'AED',
        'de': 'EUR', 'de-DE': 'EUR', 'de-AT': 'EUR', 'de-CH': 'EUR',
        'fr': 'EUR', 'fr-FR': 'EUR', 'fr-BE': 'EUR', 'fr-CH': 'EUR',
        'it': 'EUR', 'it-IT': 'EUR', 'it-CH': 'EUR',
        'es': 'EUR', 'es-ES': 'EUR', 'es-MX': 'USD',
        'nl': 'EUR', 'nl-NL': 'EUR', 'nl-BE': 'EUR',
        'sv': 'EUR', 'sv-SE': 'EUR',
        'no': 'EUR', 'nb-NO': 'EUR', 'nn-NO': 'EUR',
        'da': 'EUR', 'da-DK': 'EUR',
        'fi': 'EUR', 'fi-FI': 'EUR',
        'pl': 'EUR', 'pl-PL': 'EUR',
        'cs': 'EUR', 'cs-CZ': 'EUR',
        'ro': 'EUR', 'ro-RO': 'EUR',
        'hu': 'EUR', 'hu-HU': 'EUR',
        'bg': 'EUR', 'bg-BG': 'EUR',
        'hr': 'EUR', 'hr-HR': 'EUR',
        'sk': 'EUR', 'sk-SK': 'EUR',
        'sl': 'EUR', 'sl-SI': 'EUR',
        'lt': 'EUR', 'lt-LT': 'EUR',
        'lv': 'EUR', 'lv-LV': 'EUR',
        'et': 'EUR', 'et-EE': 'EUR',
        'el': 'EUR', 'el-GR': 'EUR'
    },

    /**
     * Get current currency from localStorage
     */
    getCurrent() {
        return localStorage.getItem('charvak_currency') || 'INR';
    },

    /**
     * Set current currency
     */
    setCurrency(currency) {
        if (this.rates[currency]) {
            localStorage.setItem('charvak_currency', currency);
            this.updateAllPrices();
            return true;
        }
        return false;
    },

    /**
     * Convert INR amount to current currency
     */
    convert(inrAmount) {
        const currency = this.getCurrent();
        if (currency === 'INR') return inrAmount;
        const rate = this.rates[currency];
        if (!rate) return inrAmount;
        return inrAmount / rate;
    },

    /**
     * Format amount in current currency
     */
    format(inrAmount) {
        const converted = this.convert(inrAmount);
        const currency = this.getCurrent();
        const symbol = this.symbols[currency] || '$';
        
        // Round based on currency
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

    /**
     * Get currency symbol
     */
    getSymbol() {
        const currency = this.getCurrent();
        return this.symbols[currency] || '$';
    },

    /**
     * Get currency name
     */
    getName() {
        const currency = this.getCurrent();
        return this.names[currency] || 'US Dollar';
    },

    /**
     * Detect user location using multiple methods
     */
    async detectLocation() {
        let countryCode = null;
        
        // Try IP geolocation APIs
        const apis = [
            'https://ipapi.co/json/',
            'https://ipinfo.io/json',
            'https://ip-api.com/json/'
        ];
        
        for (const api of apis) {
            try {
                const response = await fetch(api);
                const data = await response.json();
                
                if (api.includes('ipapi.co') && data.country_code) {
                    countryCode = data.country_code;
                    break;
                } else if (api.includes('ipinfo.io') && data.country) {
                    countryCode = data.country;
                    break;
                } else if (api.includes('ip-api.com') && data.countryCode) {
                    countryCode = data.countryCode;
                    break;
                }
            } catch (error) {
                console.log(`Failed: ${api}`);
            }
        }
        
        // Fallback to browser language
        if (!countryCode) {
            const browserLang = navigator.language || navigator.userLanguage;
            const detected = this.browserLangToCurrency[browserLang] || 'USD';
            
            // Find a country that uses this currency
            for (const [country, currency] of Object.entries(this.countryToCurrency)) {
                if (currency === detected) {
                    countryCode = country;
                    break;
                }
            }
        }
        
        if (countryCode) {
            const detected = this.countryToCurrency[countryCode] || 'USD';
            if (!localStorage.getItem('charvak_currency')) {
                this.setCurrency(detected);
                console.log(`Detected: ${detected} (${this.names[detected]}) for country: ${countryCode}`);
            }
            return detected;
        }
        
        return this.getCurrent();
    },

    /**
     * Update all price elements on the page
     */
    updateAllPrices() {
        const currency = this.getCurrent();
        const symbol = this.getSymbol();
        
        // Update elements with data-inr attribute
        document.querySelectorAll('[data-inr]').forEach(el => {
            const inrAmount = parseFloat(el.getAttribute('data-inr'));
            if (inrAmount) {
                el.textContent = this.format(inrAmount);
            }
        });
        
        // Update elements with data-currency-price attribute
        document.querySelectorAll('[data-currency-price]').forEach(el => {
            const inrAmount = parseFloat(el.getAttribute('data-currency-price'));
            if (inrAmount) {
                el.textContent = this.format(inrAmount);
            }
        });
        
        // Dispatch event for other scripts
        window.dispatchEvent(new CustomEvent('currencyChanged', {
            detail: { currency: currency, symbol: symbol }
        }));
    },

    /**
     * Initialize currency system
     */
    async init() {
        // Set default if not set
        if (!localStorage.getItem('charvak_currency')) {
            await this.detectLocation();
        }
        
        // Update all prices on page load
        this.updateAllPrices();
        
        // Listen for currency changes
        window.addEventListener('charvakCurrencyChange', (e) => {
            if (e.detail && e.detail.currency) {
                this.setCurrency(e.detail.currency);
            }
        });
        
        console.log(`Charvak Currency initialized: ${this.getCurrent()} (${this.getName()})`);
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        CharvakCurrency.init();
    });
} else {
    CharvakCurrency.init();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CharvakCurrency;
}