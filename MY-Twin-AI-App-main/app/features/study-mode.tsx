import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { useTwinStore } from '../../store/useTwinStore';

export default function StudyMode() {
  const [concept, setConcept] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const { user } = useTwinStore();

  const startStudy = async () => {
    setLoading(true);
    try {
      const res = await fetch('https://my-twin-pro-production-b744.up.railway.app/api/study/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user?.id, concept, age_group: 'young_adult', language: 'ar' }),
      });
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setResult({ error: 'تعذر الاتصال بالخادم' });
    }
    setLoading(false);
  };

  return (
    <ScrollView style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>📚 مساعد الدراسة ATHENA</Text>
      <TextInput
        placeholder="ما المفهوم الذي تريد تعلمه؟"
        value={concept}
        onChangeText={setConcept}
        style={{ borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 10, marginBottom: 10 }}
      />
      <TouchableOpacity onPress={startStudy} disabled={loading} style={{ backgroundColor: '#4A90D9', padding: 15, borderRadius: 8 }}>
        <Text style={{ color: '#fff', textAlign: 'center', fontWeight: 'bold' }}>{loading ? 'جاري التحميل...' : 'ابدأ الدراسة'}</Text>
      </TouchableOpacity>
      {result && (
        <View style={{ marginTop: 20 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold' }}>الشرح:</Text>
          <Text>{result.explanation?.simplified || result.error || 'لا يوجد شرح بعد'}</Text>
        </View>
      )}
    </ScrollView>
  );
}
