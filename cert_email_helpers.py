"""
Cert email body builders — standalone, testable, no f-string traps.
Used by email_queue._send_template once validated.
"""


def _esc(value):
    """HTML-escape a value for safe interpolation."""
    if value is None:
        return ""
    s = str(value)
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def build_cert_career_email(payload):
    """Returns (subject, html_body) for the candidate-facing cert email."""
    p = payload or {}
    name = _esc(p.get("candidate_name") or "there")
    cert_id = _esc(p.get("cert_id") or "")
    role = _esc(p.get("role") or "your role")
    industry = _esc(p.get("industry") or "")
    score = p.get("score") or 0
    badge = _esc(p.get("badge_tier") or "certified")
    cert_url = _esc(p.get("cert_url") or f"https://www.charvakit.com/career-certification/{cert_id}")
    verify_url = _esc(p.get("verify_url") or "")

    industry_part = (" (" + industry + ")") if industry else ""
    verify_block = ""
    if verify_url:
        verify_block = (
            '<p style="font-size:13px;color:#555;">Independently verify at: '
            '<a href="' + verify_url + '">' + verify_url + '</a></p>'
        )

    subject = "Your Charvak Career Certification \u2014 " + cert_id

    body = (
        '<div style="font-family:sans-serif;max-width:600px;color:#111;">'
        '<h2 style="color:#3ba591;">Congratulations, ' + name + '!</h2>'
        '<p>You scored <strong>' + str(score) + '/100</strong> on the '
        '<strong>' + role + '</strong> assessment' + industry_part +
        ' and earned the Charvak Career Certification.</p>'
        '<p><strong>Certificate ID:</strong> ' + cert_id + '<br>'
        '<strong>Badge:</strong> ' + badge + '</p>'
        '<p style="margin:24px 0;">'
        '<a href="' + cert_url + '" '
        'style="background:#3ba591;color:#fff;padding:12px 24px;'
        'text-decoration:none;border-radius:6px;display:inline-block;font-weight:600;">'
        'View your certificate</a></p>'
        + verify_block +
        '<p style="margin-top:24px;"><strong>What next?</strong></p>'
        '<ul style="color:#333;line-height:1.7;">'
        '<li><a href="https://www.charvakit.com/open-roles">Browse open roles</a></li>'
        '<li><a href="https://www.charvakit.com/ai-courses">Strengthen weak topics</a></li>'
        '<li><a href="https://www.charvakit.com/mock-drive">Practice a mock drive</a></li>'
        '</ul>'
        '<p style="color:#888;font-size:12px;margin-top:32px;">'
        'Your certificate is cryptographically signed \u2014 any employer can verify '
        'your score in 5 seconds via the link above.<br>'
        'Charvak IT Consulting &middot; <a href="https://www.charvakit.com">charvakit.com</a>'
        '</p></div>'
    )
    return (subject, body)


def build_cert_admin_email(payload):
    """Returns (subject, html_body) for the admin notification email."""
    p = payload or {}
    cand_email = _esc(p.get("candidate_email") or "")
    name = _esc(p.get("candidate_name") or cand_email or "candidate")
    cert_id = _esc(p.get("cert_id") or "")
    role = _esc(p.get("role") or "")
    industry = _esc(p.get("industry") or "")
    score = p.get("score") or 0
    badge = _esc(p.get("badge_tier") or "")
    cert_url = _esc(p.get("cert_url") or f"https://www.charvakit.com/career-certification/{cert_id}")
    verify_url = _esc(p.get("verify_url") or "")
    topics = p.get("top_topics") or []
    weak = p.get("top_weak") or []

    subject = "[Charvak] New Career Certification \u2014 " + cert_id

    topics_html = ""
    if topics:
        items = ""
        for t in topics:
            items += "<li>" + _esc(t[0]) + ": " + str(t[1]) + "%</li>"
        topics_html = "<p><strong>Top skills:</strong></p><ul>" + items + "</ul>"

    weak_html = ""
    if weak:
        items = ""
        for t in weak:
            items += "<li>" + _esc(t[0]) + ": " + str(t[1]) + "%</li>"
        weak_html = "<p><strong>Weaker areas (follow up):</strong></p><ul>" + items + "</ul>"

    verify_link = ""
    if verify_url:
        verify_link = ' &nbsp; <a href="' + verify_url + '" style="color:#3ba591;">Verify URL</a>'

    body = (
        '<div style="font-family:sans-serif;max-width:640px;color:#111;">'
        '<h2 style="color:#3ba591;">New Career Certification issued</h2>'
        '<table style="border-collapse:collapse;font-size:14px;">'
        '<tr><td style="padding:4px 12px 4px 0;color:#555;"><strong>Candidate</strong></td><td>' + cand_email + '</td></tr>'
        '<tr><td style="padding:4px 12px 4px 0;color:#555;"><strong>Name</strong></td><td>' + name + '</td></tr>'
        '<tr><td style="padding:4px 12px 4px 0;color:#555;"><strong>Role</strong></td><td>' + role + ' (' + industry + ')</td></tr>'
        '<tr><td style="padding:4px 12px 4px 0;color:#555;"><strong>Score</strong></td><td>' + str(score) + ' / 100</td></tr>'
        '<tr><td style="padding:4px 12px 4px 0;color:#555;"><strong>Badge</strong></td><td>' + badge + '</td></tr>'
        '<tr><td style="padding:4px 12px 4px 0;color:#555;"><strong>Cert ID</strong></td><td>' + cert_id + '</td></tr>'
        '</table>'
        '<p style="margin:16px 0;">'
        '<a href="' + cert_url + '" style="background:#3ba591;color:#fff;padding:10px 18px;'
        'text-decoration:none;border-radius:6px;font-weight:600;">View certificate</a>'
        + verify_link + '</p>'
        + topics_html + weak_html +
        '<p style="color:#888;font-size:12px;margin-top:24px;">'
        'Reply to this email to reach the candidate.<br>'
        'Automated notification from Charvak.'
        '</p></div>'
    )
    return (subject, body)
