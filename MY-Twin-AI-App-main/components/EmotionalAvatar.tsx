import { useEffect, useRef } from 'react';
import { Animated, StyleSheet, View, Text } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';

// نظام المشاعر المتكامل
const EMOTION_CONFIG: Record<string, { emoji: string; color: string; glowColor: string; pulseSpeed: number; energyLabel: string }> = {
  joy:       { emoji: '😊', color: '#F59E0B', glowColor: '#FEF3C7', pulseSpeed: 800,  energyLabel: 'نشيط' },
  happy:     { emoji: '😊', color: '#F59E0B', glowColor: '#FEF3C7', pulseSpeed: 800,  energyLabel: 'نشيط' },
  excited:   { emoji: '🤩', color: '#F59E0B', glowColor: '#FEF3C7', pulseSpeed: 600,  energyLabel: 'مفعم' },
  sad:       { emoji: '😢', color: '#3B82F6', glowColor: '#DBEAFE', pulseSpeed: 1800, energyLabel: 'منخفض' },
  sadness:   { emoji: '😢', color: '#3B82F6', glowColor: '#DBEAFE', pulseSpeed: 1800, energyLabel: 'منخفض' },
  angry:     { emoji: '😠', color: '#EF4444', glowColor: '#FEE2E2', pulseSpeed: 700,  energyLabel: 'متوتر' },
  anger:     { emoji: '😠', color: '#EF4444', glowColor: '#FEE2E2', pulseSpeed: 700,  energyLabel: 'متوتر' },
  fear:      { emoji: '😨', color: '#A78BFA', glowColor: '#EDE9FE', pulseSpeed: 1000, energyLabel: 'قلق' },
  anxious:   { emoji: '😰', color: '#A78BFA', glowColor: '#EDE9FE', pulseSpeed: 1000, energyLabel: 'قلق' },
  love:      { emoji: '💕', color: '#EC4899', glowColor: '#FCE7F3', pulseSpeed: 900,  energyLabel: 'محب' },
  surprise:  { emoji: '😮', color: '#8B5CF6', glowColor: '#EDE9FE', pulseSpeed: 700,  energyLabel: 'مندهش' },
  neutral:   { emoji: '😌', color: '#6B7280', glowColor: '#F3F4F6', pulseSpeed: 1500, energyLabel: 'طبيعي' },
  calm:      { emoji: '😌', color: '#10B981', glowColor: '#D1FAE5', pulseSpeed: 2000, energyLabel: 'هادئ' },
  lonely:    { emoji: '🥺', color: '#6366F1', glowColor: '#E0E7FF', pulseSpeed: 1600, energyLabel: 'وحيد' },
  motivated: { emoji: '💪', color: '#10B981', glowColor: '#D1FAE5', pulseSpeed: 750,  energyLabel: 'متحمس' },
  grateful:  { emoji: '🙏', color: '#8B5CF6', glowColor: '#EDE9FE', pulseSpeed: 1000, energyLabel: 'ممتن' },
  confused:  { emoji: '😕', color: '#F59E0B', glowColor: '#FEF3C7', pulseSpeed: 900,  energyLabel: 'مشتت' },
  support:   { emoji: '🤝', color: '#6366F1', glowColor: '#E0E7FF', pulseSpeed: 1000, energyLabel: 'داعم' },
};

interface Props {
  emotion: string;
  size?: number;
  showGlow?: boolean;
  animated?: boolean;
}

export default function EmotionalAvatar({ emotion, size = 60, showGlow = true, animated = true }: Props) {
  const { theme, relationshipDims, energy } = useTwinStore();
  const isDark = theme === 'dark';

  const config = EMOTION_CONFIG[emotion] || EMOTION_CONFIG.neutral;
  const emoji = config.emoji;
  const color = config.color;
  const glowColor = config.glowColor;
  const pulseSpeed = config.pulseSpeed;

  const pulse = useRef(new Animated.Value(1)).current;
  const previousEmotion = useRef(emotion);

  useEffect(() => {
    // لا تقم بالأنيميشن إذا كان الشعور لم يتغير
    if (!animated || previousEmotion.current === emotion) {
      previousEmotion.current = emotion;
      return;
    }
    previousEmotion.current = emotion;

    // نبضة واحدة فقط بدلاً من حلقة لا نهائية
    const animation = Animated.sequence([
      Animated.timing(pulse, {
        toValue: 1.15,
        duration: pulseSpeed * 0.4,
        useNativeDriver: true,
      }),
      Animated.timing(pulse, {
        toValue: 1,
        duration: pulseSpeed * 0.6,
        useNativeDriver: true,
      }),
    ]);
    animation.start();

    return () => animation.stop();
  }, [emotion, pulseSpeed, animated]);

  // حجم الحلقة الخارجية يتناسب مع الطاقة
  const energyFactor = energy ? (energy / 100) * 0.3 + 0.85 : 1;
  const ringSize = size + 12;

  return (
    <View style={styles.outerContainer}>
      <Animated.View
        style={[
          styles.ring,
          {
            width: ringSize,
            height: ringSize,
            borderRadius: ringSize / 2,
            borderColor: isDark ? color + '80' : color + '30',
            backgroundColor: showGlow ? (isDark ? glowColor + '15' : glowColor + '80') : 'transparent',
            transform: [{ scale: pulse }],
            shadowColor: isDark ? 'transparent' : color,
            shadowOpacity: showGlow ? 0.2 : 0,
            shadowRadius: 12,
            shadowOffset: { width: 0, height: 4 },
            elevation: showGlow ? 4 : 0,
          },
        ]}
        accessibilityLabel={`الحالة العاطفية: ${emotion}`}
        accessibilityRole="image"
      >
        <Text style={[styles.emoji, { fontSize: size * 0.55 }]}>
          {emoji}
        </Text>
      </Animated.View>
      
      {/* مؤشرات إضافية من العلاقة */}
      <View style={[styles.indicators, isDark && { backgroundColor: '#FFFFFF10' }]}>
        <View style={[styles.indicatorDot, { backgroundColor: color }]} />
        <View style={[styles.indicatorDot, { backgroundColor: relationshipDims?.trust > 60 ? '#3B82F6' : '#6B7280' }]} />
        <View style={[styles.indicatorDot, { backgroundColor: relationshipDims?.affection > 60 ? '#EC4899' : '#6B7280' }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  outerContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  ring: {
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2.5,
  },
  emoji: {
    textAlign: 'center',
  },
  indicators: {
    flexDirection: 'row',
    gap: 6,
    marginTop: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
    backgroundColor: '#F3F4F6',
  },
  indicatorDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
});
