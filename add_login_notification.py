with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add notification after successful login
if 'login_notifications.send_login_alert' not in content:
    content = content.replace(
        'return JSONResponse(result)\n    except Exception as e:\n        logger.error(f"Login failed for {data.email}',
        '''# Send login notification
        if result.get("status") == "success":
            try:
                ip = request.client.host if request.client else "unknown"
                ua = request.headers.get("user-agent", "unknown")
                login_notifications.send_login_alert(data.email, ip, ua)
            except Exception as e:
                logger.error(f"Login notification failed: {e}")
        
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Login failed for {data.email}'''
    )
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Login notifications added')
else:
    print('Already added')
