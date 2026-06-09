import { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import Svg, { Circle } from 'react-native-svg';
import React from 'react';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

interface Props {
  percentage: number;
  color: string;
  size?: number;
  label: string;
  icon?: React.ReactNode; // ✅ يقبل أيقونات Lucide أو نصوص
  trackColor?: string;    // ✅ لون المسار (للوضع الداكن)
}

export default function CircleProgress({
  percentage,
  color,
  size = 60,
  label,
  icon,
  trackColor = '#E8E8E3',
}: Props) {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  
  // ✅ حماية من القيم السالبة والزائدة
  const safePercentage = Math.max(0, Math.min(percentage, 100));
  const strokeDashoffset = circumference - (safePercentage / 100) * circumference;

  // ✅ تحريك القيمة عند التغيير
  const animatedOffset = useRef(new Animated.Value(strokeDashoffset)).current;

  useEffect(() => {
    Animated.timing(animatedOffset, {
      toValue: strokeDashoffset,
      duration: 600,
      useNativeDriver: true,
    }).start();
  }, [strokeDashoffset]);

  return (
    <View style={styles.container}>
      <Svg width={size} height={size}>
        {/* المسار الأساسي */}
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={trackColor}
          strokeWidth={4}
          fill="transparent"
        />
        {/* القوس المتحرك */}
        <AnimatedCircle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={4}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={animatedOffset}
          strokeLinecap="round"
          rotation="-90"
          origin={`${size / 2}, ${size / 2}`}
        />
      </Svg>
      {/* المحتوى في المنتصف */}
      <View style={[styles.center, { width: size, height: size }]}>
        {icon && <View style={styles.iconWrap}>{icon}</View>}
        <Text style={[styles.percent, { color }]}>
          {Math.round(safePercentage)}%
        </Text>
      </View>
      <Text style={[styles.label, { color }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center' },
  center: {
    position: 'absolute',
    top: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconWrap: { marginBottom: 1 },
  percent: { fontSize: 10, fontWeight: '700' },
  label: { fontSize: 10, fontWeight: '600', marginTop: 3 },
});
