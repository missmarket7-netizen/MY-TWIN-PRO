import React, { useEffect, useRef } from 'react';
import { View, Animated, StyleSheet } from 'react-native';

export function SkeletonLoader({ width = '100%', height = 20, borderRadius = 8, style }: any) {
  const shimmer = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(shimmer, { toValue: 1, duration: 1000, useNativeDriver: true }),
        Animated.timing(shimmer, { toValue: 0, duration: 1000, useNativeDriver: true }),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, []);

  const opacity = shimmer.interpolate({ inputRange: [0, 1], outputRange: [0.3, 0.7] });

  return (
    <Animated.View style={[{ width, height, borderRadius, backgroundColor: '#E5E7EB', opacity }, style]} />
  );
}

export function SkeletonCard() {
  return (
    <View style={st.card}>
      <SkeletonLoader width={44} height={44} borderRadius={14} />
      <View style={{ flex: 1, gap: 8 }}>
        <SkeletonLoader width="70%" height={18} />
        <SkeletonLoader width="50%" height={14} />
      </View>
    </View>
  );
}

const st = StyleSheet.create({
  card: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 16, borderRadius: 16, backgroundColor: '#FAFAFE', marginBottom: 8 },
});
