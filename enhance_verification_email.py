with open('email_verification.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace with enhanced email
old_email = '''        subject = "Verify Your Charvak Account"
        content = f"""
        <h2>Welcome to Charvak, {name}!</h2>
        <p>Please verify your email address to activate your account.</p>
        <p><a href="{verification_url}" style="background:#3ba591;color:white;padding:12px 25px;text-decoration:none;border-radius:50px;">Verify Email</a></p>
        <p>Or copy this link: {verification_url}</p>
        <p>This link expires in 24 hours.</p>
        <p>If you didn't create this account, please ignore this email.</p>
        """'''

new_email = '''        subject = "🎉 Welcome to Charvak - Verify Your Account"
        content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0;">Welcome to Charvak!</h1>
                <p style="margin: 10px 0 0 0;">Hi {name}, let's get you started</p>
            </div>
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                <h3>Verify Your Email Address</h3>
                <p>Thanks for signing up! Please click the button below to verify your email and activate your account.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: #3ba591; color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; font-weight: bold; display: inline-block;">✅ Verify Email</a>
                </div>
                
                <p style="color: #666; font-size: 14px;">Or copy this link:<br>
                <a href="{verification_url}" style="color: #3ba591; word-break: break-all;">{verification_url}</a></p>
                
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 20px;">
                    <strong>⏰ Important:</strong> This link expires in 24 hours.
                </div>
                
                <hr style="margin: 30px 0;">
                
                <p><strong>What you get with Charvak:</strong></p>
                <ul>
                    <li>🤖 25 AI-Driven Courses with personal tutor</li>
                    <li>📝 AI-Powered Assessments (Versant, MCQ)</li>
                    <li>🏢 Company Mock Drives (18 companies)</li>
                    <li>🎯 Career Guidance with AI analysis</li>
                    <li>💼 C2C Placement Platform</li>
                </ul>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    If you didn't create this account, please ignore this email.<br>
                    Questions? Contact us at hr@charvakit.com
                </p>
            </div>
        </div>
        """'''

if old_email in content:
    content = content.replace(old_email, new_email)
    with open('email_verification.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Verification email enhanced!')
else:
    print('Pattern not found')
