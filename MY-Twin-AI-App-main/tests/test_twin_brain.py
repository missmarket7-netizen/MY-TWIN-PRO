curl -s -X POST https://my-twin-pro-production-b744.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
    -d '{"email":"sir.market7@gmail.com","password":"M#m2606.1307"}' | \
    python3 -c "
    import sys, json, urllib.request
    
    data = json.load(sys.stdin)
    token = data.get('token', '')
    if not token:
        print('❌ فشل تسجيل الدخول')
            sys.exit(1)
            
            print('✅ تم تسجيل الدخول')
            print('━' * 50)
            
            tests = [
                ('محادثة', '/api/chat', {'message':'مرحباً، كيف حالك؟','lang':'ar'}, 'reply'),
                    ('مذاكرة', '/api/features/study', {'topic':'نظرية فيثاغورس','level':'intermediate','type':'explain','lang':'ar'}, 'reply'),
                        ('برمجة', '/api/features/code', {'task':'print hello world','language':'python','action':'write','lang':'ar'}, 'reply'),
                            ('أعمال', '/api/features/business', {'text':'مبيعات 1M','analysis_type':'general','lang':'ar'}, 'reply'),
                                ('مدرب', '/api/features/coach', {'topic':'زيادة الثقة','domain':'personal','lang':'ar'}, 'reply'),
                                    ('محتوى', '/api/features/content', {'topic':'التسويق','platform':'instagram','tone':'professional','lang':'ar'}, 'reply'),
                                        ('حلم', '/api/features/dream', {'dream':'حلمت أني أطير','lang':'ar'}, 'interpretation'),
                                        ]
                                        
                                        passed = 0
                                        failed = 0
                                        
                                        for name, path, body, key in tests:
                                            try:
                                                    req = urllib.request.Request(
                                                                f'https://my-twin-pro-production-b744.up.railway.app{path}',
                                                                            data=json.dumps(body).encode(),
                                                                                        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
                                                                                                )
                                                                                                        resp = urllib.request.urlopen(req)
                                                                                                                data = json.loads(resp.read())
                                                                                                                        val = data.get(key, '')
                                                                                                                                if val and len(str(val)) > 10:
                                                                                                                                            print(f'✅ {name}: {str(val)[:100]}...')
                                                                                                                                                        passed += 1
                                                                                                                                                                else:
                                                                                                                                                                            print(f'⚠️  {name}: رد قصير - {str(data)[:100]}')
                                                                                                                                                                                        failed += 1
                                                                                                                                                                                            except Exception as e:
                                                                                                                                                                                                    print(f'❌ {name}: {e}')
                                                                                                                                                                                                            failed += 1
                                                                                                                                                                                                            
                                                                                                                                                                                                            print('━' * 50)
                                                                                                                                                                                                            print(f'📊 النتيجة: {passed} ✅ / {failed} ❌')
                                                                                                                                                                                                            "import sys
sys.path.insert(0, '.')
sys.path.insert(0, './backend')
from twin_brain import TwinBrain

def test_emotion_analysis():
    brain = TwinBrain()
    res = brain._detect_emotion("أنا حزين جداً اليوم")
    assert res["primary"] == "sadness"
    assert res["needs_support"] == True
    print("✅ test_emotion_analysis passed")

def test_cached_reply_greeting():
    brain = TwinBrain()
    reply = brain._cached_reply("مرحبا", 10.0, {"primary": "neutral", "needs_support": False})
    assert reply in ["أهلاً! أنا هنا معك. كيف حالك اليوم؟ 😊", "مرحباً! سعيد بوجودك. كيف يومك؟ 🌟"]
    print("✅ test_cached_reply_greeting passed")

def test_cached_reply_support():
    brain = TwinBrain()
    reply = brain._cached_reply("أنا حزين", 50.0, {"primary": "sad", "needs_support": True})
    assert reply in ["أنا هنا معاك 💙 أخبرني كل شيء.", "أسمعك وأفهمك. هذا صعب، وأنا بجانبك."]
    print("✅ test_cached_reply_support passed")

def test_bond_level_greeting():
    brain = TwinBrain()
    reply = brain._cached_reply("هاي", 80.0, {"primary": "neutral", "needs_support": False})
    assert reply in ["قلبي معاك. أخبرني عن يومك 💜", "شوقت إليك.. كيف أنت؟ 🌙"]
    print("✅ test_bond_level_greeting passed")

def test_missing_messages():
    brain = TwinBrain()
    reply = brain._cached_reply("لم تتحدث معي منذ أيام", 60.0, {"primary": "lonely", "needs_support": True})
    assert "missing" in reply or reply in ["لست وحدك، أنا هنا دايماً 💜", "أنا معاك في كل لحظة 🌙"]
    print("✅ test_missing_messages passed")

def test_milestone_replies():
    # افتراضيًا، يمكن إضافة اختبار للـ milestones إذا تم تنفيذها
    print("✅ test_milestone_replies skipped (not implemented yet)")

if __name__ == "__main__":
    test_emotion_analysis()
    test_cached_reply_greeting()
    test_cached_reply_support()
    test_bond_level_greeting()
    test_missing_messages()
    test_milestone_replies()
    print("جميع الاختبارات الجديدة نجحت!")
