# NEXT-SESSION-PLAN

**Last updated:** 2026-11-09 (Session 109 complete)

---

## Session 109 - COMPLETE
- TPO Dashboard (live, responsive, auto-refresh)
- Employer Dashboard (live, responsive, auto-refresh)
- Brevo bulk invites + Magic Link login
- Pre-filled assessments

---

## Session 110 - NEXT

### Priority 1 - Sales Push
- Demo TPO dashboard at 5+ colleges.
- Demo Employer dashboard at 3+ employers.
- Sales hook: "Upload candidates → They test → You see verified scores live."

### Priority 2 - Verify Mobile Experience
- Open \/college/dashboard\ and \/employer/dashboard\ on your phone.
- Ensure the table scrolls horizontally and buttons stack.
- Confirm \● LIVE\ badge and 30s auto-refresh work on mobile.

### Priority 3 - Optional Builds
- Add job-board to the responsive polish.
- Clean up test data in VIT/Acme batches.

---

**Next action:** Schedule 5 college demos + 3 employer demos.
---

## FLAGGED - Multi-Tenant Isolation (Session 112+, after 5+ paying TPOs/employers)

**Problem:** The 4 business portals now require admin auth. This works for demos but does not scale.

When you have 5+ paying TPOs or employers, each one needs:
- Their own login (not a shared admin password)
- Their own data visibility (VIT sees only VIT students; NIT sees only NIT)
- Self-service password reset
- Audit log per user (who uploaded what, when)

**Current state:**
- All TPO/employer data is in charvak_college_invites, keyed by institution_name
- No auth restricts which institution a user sees
- Admin can see all institutions (via dropdown)

**Fix plan (~2-3 sessions):**
1. Migration: Add charvak_tenant_users table mapping email -> institution_name -> role
2. Auth: Add require_tenant_auth(request) that reads the tenant from the token
3. Dashboard: Remove the institution dropdown; single-institution view based on caller
4. Email: Self-service password reset for tenant users
5. Admin: Super-admin view to impersonate any tenant (for support)

**Trigger to build:** When you sign the 3rd paying customer, OR when a customer asks "how do my team members get their own login?"

**Estimated effort:** 2-3 sessions, 4-6 hours each.

**Session 51 + 84 gaps fixed in this session:** /employer/dashboard and /recruiter/dashboard now require admin login.

---

**Next action:** Test all 4 portals after deploy. Then schedule 5 college demos + 3 employer demos.
