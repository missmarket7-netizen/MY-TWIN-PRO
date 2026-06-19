import { useState, useCallback, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, Alert,
  ActivityIndicator, SafeAreaView, KeyboardAvoidingView, Platform,
  ScrollView, Linking, Image
} from 'react-native';
import { router } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import { makeRedirectUri } from 'expo-auth-session';
import { useTwinStore } from '../store/useTwinStore';
import { storeToken } from '../lib/auth';
import { login, signup } from '../lib/httpClient';

WebBrowser.maybeCompleteAuthSession();

const APP_LOGO = require('../assets/icon.png');

export default function Login() {
  const { setAuth, clearHistory, setLang, lang, userId } = useTwinStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const isAr = lang === 'ar';

  useEffect(() => {
    if (userId) {
      router.replace('/welcome');
    }
  }, [userId]);

  const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSuccess = useCallback(async (userId: string, accessToken: string) => {
    await storeToken(accessToken);
    clearHistory();
    setAuth(userId);
    router.replace('/welcome');
  }, [clearHistory, setAuth]);

  const signInWithEmail = async () => {
    if (!email || !password) {
      Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'أدخل البريد وكلمة المرور' : 'Enter email and password');
      return;
    }
    if (!isValidEmail(email)) {
      Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'بريد إلكتروني غير صالح' : 'Invalid email');
      return;
    }
    setLoading(true);
    try {
      const data = await login(email, password);
      if (data.user_id && data.token) {
        handleSuccess(data.user_id, data.token);
      }
    } catch (e: any) {
      Alert.alert(isAr ? 'خطأ' : 'Error', e.message || (isAr ? 'فشل تسجيل الدخول' : 'Login failed'));
    } finally {
      setLoading(false);
    }
  };

  const signUpWithEmail = async () => {
    if (!email || !password) {
      Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'أدخل البريد وكلمة المرور' : 'Enter email and password');
      return;
    }
    if (!isValidEmail(email)) {
      Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'بريد إلكتروني غير صالح' : 'Invalid email');
      return;
    }
    if (password.length < 6) {
      Alert.alert(isAr ? 'خطأ' : 'Error', isAr ? 'كلمة المرور 6 أحرف على الأقل' : 'Min 6 characters');
      return;
    }
    setLoading(true);
    try {
      const data = await signup(email, password);
      if (data.user_id && data.token) {
        handleSuccess(data.user_id, data.token);
      } else {
        Alert.alert(isAr ? 'تم ✅' : 'Done ✅', isAr ? 'تم إنشاء الحساب. يمكنك تسجيل الدخول الآن.' : 'Account created. You can sign in now.');
      }
    } catch (e: any) {
      Alert.alert(isAr ? 'خطأ' : 'Error', e.message || (isAr ? 'فشل إنشاء الحساب' : 'Signup failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={s.safe}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={s.container}>
          <TouchableOpacity style={s.langBtn} onPress={() => setLang(isAr ? 'en' : 'ar')}>
            <Text style={s.langText}>{isAr ? '🌐 English' : '🌐 العربية'}</Text>
          </TouchableOpacity>

          <View style={s.logoContainer}>
            <Image source={APP_LOGO} style={s.logo} resizeMode="contain" />
          </View>

          <Text style={s.heading}>MyTwin</Text>
          <Text style={s.sub}>
            {isAr ? 'سجّل دخولك وابدأ رحلتك' : 'Sign in and start your journey'}
          </Text>

          <TextInput
            style={s.input}
            placeholder={isAr ? 'البريد الإلكتروني' : 'Email'}
            placeholderTextColor="#A09BB5"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            textAlign={isAr ? 'right' : 'left'}
          />

          <View style={s.passwordRow}>
            <TextInput
              style={s.passwordInput}
              placeholder={isAr ? 'كلمة المرور' : 'Password'}
              placeholderTextColor="#A09BB5"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              textAlign={isAr ? 'right' : 'left'}
            />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={s.eyeBtn}>
              <Text style={s.eyeIcon}>{showPassword ? '🙈' : '👁️'}</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={s.button} onPress={signInWithEmail} disabled={loading}>
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <Text style={s.buttonText}>{isAr ? 'تسجيل الدخول' : 'Sign In'}</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity style={[s.button, s.outline]} onPress={signUpWithEmail} disabled={loading}>
            <Text style={[s.buttonText, s.outlineText]}>{isAr ? 'إنشاء حساب جديد' : 'Create Account'}</Text>
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#FFFFFF' },
  container: { flexGrow: 1, backgroundColor: '#FFFFFF', padding: 24, justifyContent: 'center' },
  langBtn: { position: 'absolute', top: 50, right: 24, backgroundColor: '#F3F0FF', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: '#E0D9F5' },
  langText: { color: '#6B21A8', fontSize: 14, fontWeight: '600' },
  logoContainer: { alignItems: 'center', marginBottom: 16 },
  logo: { width: 80, height: 80, borderRadius: 20 },
  heading: { fontSize: 32, fontWeight: '800', color: '#1A1226', textAlign: 'center', marginBottom: 8 },
  sub: { fontSize: 16, color: '#6B5B8A', textAlign: 'center', marginBottom: 32 },
  input: { backgroundColor: '#F8F6F2', color: '#1A1226', padding: 14, borderRadius: 12, marginBottom: 12, borderWidth: 1, borderColor: '#E0D9F5', fontSize: 15 },
  passwordRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#F8F6F2', borderRadius: 12, marginBottom: 16, borderWidth: 1, borderColor: '#E0D9F5' },
  passwordInput: { flex: 1, color: '#1A1226', padding: 14, fontSize: 15 },
  eyeBtn: { padding: 12 },
  eyeIcon: { fontSize: 18 },
  button: { backgroundColor: '#6B21A8', padding: 14, borderRadius: 12, alignItems: 'center', marginBottom: 10 },
  buttonText: { color: '#FFFFFF', fontWeight: '700', fontSize: 16 },
  outline: { backgroundColor: 'transparent', borderWidth: 1.5, borderColor: '#6B21A8' },
  outlineText: { color: '#6B21A8' },
});
