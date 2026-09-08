with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'mcq_bank' not in content:
    routes = '''
from mcq_bank import mcq_bank

@app.get("/api/mcq/topics")
async def get_mcq_topics():
    return mcq_bank.get_all_topics()

@app.get("/api/mcq/questions/{category}/{topic}")
async def get_topic_questions(category: str, topic: str):
    return mcq_bank.get_topic_questions(category, topic)

'''
    content = content.replace('if __name__', routes + '\nif __name__', 1)
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ MCQ bank routes added')
else:
    print('Already exists')
