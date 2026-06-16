import { View, TouchableOpacity, StyleSheet } from 'react-native';
import { ChevronLeft } from 'lucide-react-native';
import { router } from 'expo-router';
import { useTwinStore } from '../store/useTwinStore';

export default function Header() {
  const isDark = useTwinStore(s => s.theme === 'dark');
  const primary = isDark ? '#D8B4FE' : '#7C3AED';

  return (
    <View style={[styles.container, { borderBottomColor: isDark ? '#333' : '#E5E5E5' }]}>
      <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
        <ChevronLeft size={24} stroke={primary} />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderBottomWidth: 0.5,
  },
  backBtn: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'flex-start',
  },
});
