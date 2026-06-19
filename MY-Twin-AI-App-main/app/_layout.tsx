import * as Sentry from '@sentry/react-native';
import { Stack, useRouter } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useEffect, useRef, useMemo } from "react";
import { Pressable, StyleSheet, Animated, Modal, useWindowDimensions } from "react-native";
import { useTwinStore } from "../store/useTwinStore";
import { initAnalytics } from "../lib/analytics";
import SideMenu from "../components/SideMenu";
import { ToastProvider } from "../components/Toast";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { registerForPushNotifications, setupNotificationHandlers, setupAndroidChannels } from "../lib/notifications";

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN || "",
  tracesSampleRate: 1.0,
  environment: process.env.EXPO_PUBLIC_ENVIRONMENT || 'production',
  enableNative: true,
});

export default function RootLayout() {
  const theme = useTwinStore(s => s.theme);
  const menuVisible = useTwinStore(s => s.menuVisible);
  const closeMenu = useTwinStore(s => s.closeMenu);
  const lang = useTwinStore(s => s.lang);
  const userId = useTwinStore(s => s.userId);
  const isDark = theme === 'dark';
  const isRTL = lang === 'ar';
  const slideAnim = useRef(new Animated.Value(isRTL ? 300 : -300)).current;
  const { width } = useWindowDimensions();
  const drawerWidth = width * 0.8;

  useEffect(() => { setupNotificationHandlers(); setupAndroidChannels(); }, []);
  useEffect(() => { if (userId) registerForPushNotifications(); }, [userId]);
  useEffect(() => { let cancelled = false; const setup = async () => { if (!cancelled) await initAnalytics(); }; setup(); return () => { cancelled = true; }; }, []);

  useEffect(() => {
    Animated.spring(slideAnim, {
      toValue: menuVisible ? 0 : (isRTL ? drawerWidth : -drawerWidth),
      damping: 18,
      stiffness: 120,
      useNativeDriver: true,
    }).start();
  }, [menuVisible, drawerWidth, isRTL]);

  const screenOptions = useMemo(() => ({
    headerShown: false,
    contentStyle: { backgroundColor: isDark ? '#1A1A1A' : '#F8F6F2' },
  }), [isDark]);

  return (
    <ErrorBoundary>
      <ToastProvider>
        <StatusBar style={isDark ? "light" : "dark"} />
        <Stack screenOptions={screenOptions}>
          <Stack.Screen name="index" />
          <Stack.Screen name="splash" />
          <Stack.Screen name="welcome" />
          <Stack.Screen name="chat" />
          <Stack.Screen name="login" />
          <Stack.Screen name="onboarding" />
          {/* الشاشات الأساسية */}
          <Stack.Screen name="relationship" />
          <Stack.Screen name="memories" />
          <Stack.Screen name="mood" />
          <Stack.Screen name="history" />
          <Stack.Screen name="profile" />
          <Stack.Screen name="customize" />
          <Stack.Screen name="subscription" />
          <Stack.Screen name="referral" />
          <Stack.Screen name="settings" />
          <Stack.Screen name="help" />
          <Stack.Screen name="about" />
          <Stack.Screen name="privacy" />
          <Stack.Screen name="terms" />
          <Stack.Screen name="feedback" />
          {/* شاشات الميزات الجديدة */}
          <Stack.Screen name="features/index" />
          <Stack.Screen name="features/study-mode" />
          <Stack.Screen name="features/code-lab" />
          <Stack.Screen name="features/business-analyzer" />
          <Stack.Screen name="features/life-coach" />
          <Stack.Screen name="features/image-creator" />
          <Stack.Screen name="features/dreams" />
          <Stack.Screen name="features/content-creator" />
          <Stack.Screen name="features/smart-home" />
          <Stack.Screen name="features/task-manager" />
        </Stack>

        {menuVisible && (
          <Modal visible transparent animationType="none" onRequestClose={closeMenu}>
            <Pressable style={st.overlay} onPress={closeMenu}>
              <Animated.View
                style={[
                  st.sidebar,
                  {
                    backgroundColor: isDark ? '#1A1A1A' : '#FFFFFF',
                    width: drawerWidth,
                    [isRTL ? 'right' : 'left']: 0,
                    transform: [{ translateX: slideAnim }],
                  },
                ]}
              >
                <SideMenu onClose={closeMenu} />
              </Animated.View>
            </Pressable>
          </Modal>
        )}
      </ToastProvider>
    </ErrorBoundary>
  );
}

const st = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)' },
  sidebar: { position: 'absolute', top: 0, bottom: 0, shadowColor: "#000", shadowOffset: { width: 2, height: 0 }, shadowOpacity: 0.3, shadowRadius: 8, elevation: 15 },
});
