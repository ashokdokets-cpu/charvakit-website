# Charvak IT Consulting — Project Status

**Last updated:** 2026-09-11

## Live URLs
- Production: https://www.charvakit.com
- Render: https://dashboard.render.com
- GitHub: https://github.com/ashokdokets-cpu/charvakit-website
- Supabase: https://supabase.com/dashboard

## Git Tag
Latest stable: `v1.0-stable-20260911`

## Backup
`C:\Users\lenovo\OneDrive\Desktop\Charvak_Complete_Backup_20260911_235803.zip`

## Done
- [x] Core platform
- [x] Auth (login, register, reset, logout)
- [x] Payments (Razorpay INR + PayPal multi-currency)
- [x] 12 AI tools
- [x] 122 exams
- [x] Admin security (middleware + cookies)
- [x] Pricing page with live currency
- [x] Capabilities sheet
- [x] Emoji/encoding cleanup

## Next — Priority List
1. [ ] End-to-end user journey test (30 min)
2. [ ] Enable email verification (30 min)
3. [ ] Test email templates (30 min)
4. [ ] Verify legal pages (30 min)
5. [ ] Test contact form (15 min)
6. [ ] Mobile responsiveness check (20 min)
7. [ ] Performance audit (20 min)
8. [ ] SEO verification (20 min)
9. [ ] GA4 + Search Console (20 min)
10. [ ] Test one real ₹1 payment (30 min)

## Known Issues
- Email verification currently disabled (allow all)
- 61 templates may have mojibake (need scan)
- PayPal client ID hardcoded in a few places
- Contact form may not actually send email

## Env Vars Needed (Render + local .env)
- DATABASE_URL (Supabase Postgres)
- RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
- PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
- SENDGRID_API_KEY, ADMIN_EMAIL
- OPENAI_API_KEY
- ELEVENLABS_API_KEY
- SECRET_KEY
- SITE_URL
- ADMIN_EMAIL=charvakit@gmail.com
- HR_EMAIL=hr@charvakit.com
