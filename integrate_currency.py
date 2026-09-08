with open('templates/ai-courses.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add currency detection function
old_script_start = "    <script>"
new_script_start = '''    <script>
        var userCurrency = {symbol: '₹', rate: 1, country: 'IN'};

        async function detectUserLocation() {
            try {
                const response = await fetch('/api/location/detect');
                const result = await response.json();
                
                if (result.status === 'success') {
                    var country = result.country_code || 'IN';
                    
                    var currencyMap = {
                        'IN': {symbol: '₹', rate: 1, label: 'INR'},
                        'US': {symbol: '$', rate: 83, label: 'USD'},
                        'GB': {symbol: '£', rate: 105, label: 'GBP'},
                        'EU': {symbol: '€', rate: 90, label: 'EUR'},
                        'AE': {symbol: 'د.إ', rate: 22.6, label: 'AED'},
                        'SG': {symbol: 'S$', rate: 62, label: 'SGD'},
                        'AU': {symbol: 'A$', rate: 55, label: 'AUD'}
                    };
                    
                    userCurrency = currencyMap[country] || currencyMap['IN'];
                    
                    // Re-render courses with new currency
                    renderCourses();
                }
            } catch (e) {
                console.log('Using default INR');
            }
        }

        function formatPrice(priceINR) {
            var converted = Math.round(priceINR / userCurrency.rate);
            return userCurrency.symbol + converted;
        }

        function formatInstallment(priceINR, installments) {
            var converted = Math.round(priceINR / installments / userCurrency.rate);
            return userCurrency.symbol + converted;
        }
'''

if old_script_start in content:
    content = content.replace(old_script_start, new_script_start)

# Update renderCourses to use currency
old_price = "₹' + course.price + '</span>"
new_price = "formatPrice(course.price) + '</span>"

if old_price in content:
    content = content.replace(old_price, new_price)

old_installment = "₹' + installmentAmount + '</small>"
new_installment = "formatInstallment(course.price, installments) + '</small>"

if old_installment in content:
    content = content.replace(old_installment, new_installment)

# Update enrollCourse to use currency
old_confirm = "Total Price: ₹' + price + '\\n"
new_confirm = "Total Price: ' + formatPrice(price) + '\\n"

if old_confirm in content:
    content = content.replace(old_confirm, new_confirm)

old_installment_confirm = "Installments: ' + installments + ' × ₹' + installmentAmount + '\\n\\n"
new_installment_confirm = "Installments: ' + installments + ' × ' + formatInstallment(price, installments) + '\\n\\n"

if old_installment_confirm in content:
    content = content.replace(old_installment_confirm, new_installment_confirm)

# Call detectUserLocation on page load
old_render = "renderCourses();"
new_render = "detectUserLocation();"

if old_render in content:
    content = content.replace(old_render, new_render, 1)

with open('templates/ai-courses.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Location-based currency integrated!')
