import os

env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'ELEVENLABS_API_KEY' not in content:
        with open(env_path, 'a', encoding='utf-8') as f:
            f.write('\n# ElevenLabs AI Voice\nELEVENLABS_API_KEY=YOUR_ELEVENLABS_KEY_HERE\n')
        print('✅ ELEVENLABS_API_KEY added to .env - UPDATE IT WITH YOUR KEY')
    else:
        print('ELEVENLABS_API_KEY already in .env')
