with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'ai_content_generator' not in content:
    routes = '''
from content_generator import ai_content_generator

@app.get("/api/content/read-aloud")
async def get_read_aloud_content():
    return {"status": "success", "content": ai_content_generator.generate_read_aloud_content()}

@app.get("/api/content/repeats")
async def get_repeats_content():
    return {"status": "success", "content": ai_content_generator.generate_repeats_content()}

@app.get("/api/content/sentence-builds")
async def get_sentence_builds():
    return {"status": "success", "content": ai_content_generator.generate_sentence_builds_content()}

@app.get("/api/content/conversations")
async def get_conversations():
    return {"status": "success", "content": ai_content_generator.generate_conversations_content()}

@app.get("/api/content/story-retelling")
async def get_story_retelling():
    return {"status": "success", "content": ai_content_generator.generate_story_retelling_content()}

@app.get("/api/content/summary")
async def get_summary_content():
    return {"status": "success", "content": ai_content_generator.generate_summary_content()}

@app.get("/api/content/quality-report")
async def get_quality_report():
    return ai_content_generator.get_content_quality_report()

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Content routes added')
else:
    print('Already exists')
