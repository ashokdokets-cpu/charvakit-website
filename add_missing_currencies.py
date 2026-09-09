with open('templates/ai-courses.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update symbols map
old_symbols = "var symbols = {INR: '₹', USD: '$', EUR: '€', GBP: '£', AED: 'د.إ', SGD: 'S$', AUD: 'A$', CAD: 'C$', JPY: '¥'};"
new_symbols = "var symbols = {INR: '₹', USD: '$', EUR: '€', GBP: '£', AED: 'د.إ', SGD: 'S$', AUD: 'A$', CAD: 'C$', JPY: '¥', CNY: '¥', BRL: 'R$', NGN: '₦', ZAR: 'R'};"

if old_symbols in content:
    content = content.replace(old_symbols, new_symbols)
    print('✅ Symbols updated with CNY, BRL, NGN, ZAR')

# Update rates map
old_rates = "var rates = {INR: 1, USD: 83.1, EUR: 90.2, GBP: 105.3, AED: 22.6, SGD: 61.2, AUD: 54.8, CAD: 61.0, JPY: 0.56};"
new_rates = "var rates = {INR: 1, USD: 83.1, EUR: 90.2, GBP: 105.3, AED: 22.6, SGD: 61.2, AUD: 54.8, CAD: 61.0, JPY: 0.56, CNY: 11.5, BRL: 16.8, NGN: 0.055, ZAR: 4.45};"

if old_rates in content:
    content = content.replace(old_rates, new_rates)
    print('✅ Rates updated with CNY, BRL, NGN, ZAR')

with open('templates/ai-courses.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')
