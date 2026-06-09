import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useEffect, useRef, useMemo } from "react";
import { Pressable, StyleSheet, Animated, Modal, useWindowDimensions } from "react-native";
import { useTwinStore } from "../store/useTwinStore";
import { initAnalytics } from "../lib/analytics";
import SideMenu from "../components/SideMenu";
import { ToastProvider } from "../components/Toast";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { shallow } from 'zustand/shallow';

export default function Layout() {
  // ✅ استخدام selectors منفصلة لمنع إعادة الرندر غير الضرورية
  const theme = useTwinStore(s => s.theme);
  const menuVisible = useTwinStore(s => s.menuVisible);
  const closeMenu = useTwinStore(s => s.closeMenu);
  const isDark = theme === 'dark';
  
  const slideAnim = useRef(new Animated.Value(-300)).current;
  const { width } = useWindowDimensions();
  const drawerWidth = width * 0.8;

  // ✅ Analytics يُشغّل مرة واحدة مع cleanup
  useEffect(() => {
    let cancelled = false;
    const setup = async () => {
      if (!cancelled) await initAnalytics();
    };
    setup();
    return () => { cancelled = true; };
  }, []);

  // ✅ Animation أكثر سلاسة مع Animated.spring
  useEffect(() => {
    Animated.spring(slideAnim, {
      toValue: menuVisible ? 0 : -drawerWidth,
      damping: 18,
      stiffness: 120,
      useNativeDriver: true,
    }).start();
  }, [menuVisible, drawerWidth]);

  return (
    <ErrorBoundary>
      <ToastProvider>
        <StatusBar style={isDark ? "light" : "dark"} />
        {/* ✅ لا حاجة لتعريف كل الشاشات يدوياً – Expo Router يكتشفها تلقائياً */}
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: isDark ? '#1A1A1A' : '#F8F6F2' },
            animation: 'slide_from_right',
          }}
        >
          {/* نُبقي شاشة chat فقط لأنها تحتاج خيارًا خاصًا (headerShown: false) */}
          <Stack.Screen name="chat" options={{ headerShown: false }} />
        </Stack>

        {menuVisible && (
          <Modal visible transparent animationType="none" onRequestClose={closeMenu}>
            {/* ✅ عزل اللمسات: الطبقة الخارجية للإغلاق، والداخلية تمنع تمرير اللمس */}
            <Pressable style={styles.overlay} onPress={closeMenu}>
              <Pressable style={StyleSheet.absoluteFill} onPress={() => {}}>
                <Animated.View
                  style={[
                    styles.sidebar,
                    {
                      backgroundColor: isDark ? '#1A1A1A' : '#FFFFFF',
                      width: drawerWidth,
                      transform: [{ translateX: slideAnim }],
                    },
                  ]}
                >
                  <SideMenu onClose={closeMenu} />
                </Animated.View>
              </Pressable>
            </Pressable>
          </Modal>
        )}
      </ToastProvider>
    </ErrorBoundary>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  sidebar: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    shadowColor: "#000",
    shadowOffset: { width: 2, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 15,
  },
});
