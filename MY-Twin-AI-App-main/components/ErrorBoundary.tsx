import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import * as Clipboard from 'expo-clipboard';
import { AlertTriangle, RefreshCw, Copy, XCircle } from 'lucide-react-native';

interface Props {
  children: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundaryClass extends React.Component<Props & { isDark: boolean; isAr: boolean }, State> {
  constructor(props: Props & { isDark: boolean; isAr: boolean }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('❌ ErrorBoundary caught:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined });
  };

  handleCopyDetails = () => {
    const details = this.state.error
      ? `${this.state.error.name}: ${this.state.error.message}\n${this.state.error.stack}`
      : '';
    Clipboard.setStringAsync(details);
    Alert.alert(
      this.props.isAr ? 'تم النسخ' : 'Copied',
      this.props.isAr ? 'تم نسخ تفاصيل الخطأ.' : 'Error details copied to clipboard.',
    );
  };

  render() {
    const { isDark, isAr, children } = this.props;
    const t = (ar: string, en: string) => (isAr ? ar : en);

    if (this.state.hasError) {
      const bg = isDark ? '#1A1A1A' : '#F8F6F2';
      const txt = isDark ? '#FFF' : '#1A1A1A';
      const sub = isDark ? '#CCC' : '#666';
      const primary = isDark ? '#D8B4FE' : '#6B21A8';

      return (
        <View style={[styles.container, { backgroundColor: bg }]}>
          <AlertTriangle size={56} stroke={primary} style={{ marginBottom: 24 }} />
          <Text style={[styles.title, { color: txt }, isAr && { writingDirection: 'rtl', fontFamily: 'System' }]}>
            {t('حدث خطأ غير متوقع', 'An unexpected error occurred')}
          </Text>

          {this.state.error && (
            <ScrollView
              style={styles.errorScroll}
              contentContainerStyle={{ alignItems: 'center', paddingHorizontal: 20 }}
            >
              <View style={[styles.errorBox, { backgroundColor: isDark ? '#2A2A2A' : '#F0F0F0', borderColor: isDark ? '#444' : '#E5E5E5' }]}>
                <XCircle size={18} stroke={isDark ? '#EF4444' : '#DC2626'} style={{ marginBottom: 8 }} />
                <Text
                  style={[styles.errorText, { color: sub }, isAr && { writingDirection: 'rtl', fontFamily: 'System' }]}
                  selectable
                >
                  {this.state.error.message || t('خطأ غير معروف', 'Unknown error')}
                </Text>
              </View>
            </ScrollView>
          )}

          <View style={[styles.btnRow, isAr && { flexDirection: 'row-reverse' }]}>
            <TouchableOpacity
              style={[styles.button, { backgroundColor: primary }]}
              onPress={this.handleReset}
            >
              <RefreshCw size={18} stroke="#FFF" />
              <Text style={styles.buttonText}>
                {t('إعادة المحاولة', 'Retry')}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.copyButton, { borderColor: primary }]}
              onPress={this.handleCopyDetails}
            >
              <Copy size={18} stroke={primary} />
              <Text style={[styles.copyButtonText, { color: primary }]}>
                {t('نسخ التفاصيل', 'Copy Details')}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      );
    }

    return children;
  }
}

// ✅ غلاف يستخرج الثيم واللغة من المتجر
export function ErrorBoundary(props: Props) {
  const theme = useTwinStore((s) => s.theme);
  const lang = useTwinStore((s) => s.lang);
  const isDark = theme === 'dark';
  const isAr = lang === 'ar';

  return (
    <ErrorBoundaryClass
      {...props}
      isDark={isDark}
      isAr={isAr}
    />
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 20,
  },
  errorScroll: {
    maxHeight: 180,
    width: '100%',
    marginBottom: 28,
  },
  errorBox: {
    padding: 16,
    borderRadius: 14,
    borderWidth: 1,
    alignItems: 'center',
    width: '100%',
  },
  errorText: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 22,
  },
  btnRow: {
    flexDirection: 'row',
    gap: 12,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 10,
    minWidth: 140,
  },
  buttonText: {
    color: '#FFF',
    fontSize: 15,
    fontWeight: '600',
  },
  copyButton: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
  },
  copyButtonText: {
    fontSize: 15,
    fontWeight: '600',
  },
});
