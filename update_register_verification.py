with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the register function
old_register = '''async def api_register(data: RegisterRequest):
    try:
        result = register_user(
            email=data.email,
            password=data.password,
            name=data.name,
            role=data.role,
            phone=data.phone
        )
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Registration failed for {data.email}: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": "Registration failed. Please try again."},
            status_code=500
        )'''

new_register = '''async def api_register(data: RegisterRequest):
    try:
        # Validate registration (anti-bot)
        from registration_guard import validate_registration
        validation = validate_registration(data.email, data.name, data.password)
        if validation["status"] != "success":
            return JSONResponse(validation, status_code=400)
        
        # Register user
        result = register_user(
            email=data.email,
            password=data.password,
            name=data.name,
            role=data.role,
            phone=data.phone
        )
        
        # Send verification email
        if result.get("status") == "success":
            try:
                from email_verification import email_verification
                token = email_verification.generate_token(data.email)
                email_result = email_verification.send_verification_email(
                    data.email, data.name, token
                )
                result["verification_sent"] = email_result.get("email_sent", False)
                result["message"] = "Account created! Please check your email to verify."
            except Exception as e:
                logger.error(f"Verification email failed: {e}")
                result["message"] = "Account created! Email verification pending."
        
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Registration failed for {data.email}: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": "Registration failed. Please try again."},
            status_code=500
        )'''

if old_register in content:
    content = content.replace(old_register, new_register)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Registration updated with email verification!')
else:
    print('Pattern not found')
