import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { useTwinStore } from '../store/useTwinStore';
import * as Clipboard from 'expo-clipboard';
import { AlertTriangle, RefreshCw, Copy } from 'lucide-react-native';

interface Props { children: React.ReactNode; featureName: string; }

interface State { hasError: boolean; error?: Error; }

export class FeatureErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error(`❌ ${this.props.featureName}:`, error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined });
  };

  handleCopyDetails = () => {
    const details = this.state.error ? `${this.state.error.name}: ${this.state.error.message}` : '';
    Clipboard.setStringAsync(details);
  };

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.container}>
          <AlertTriangle size={48} stroke="#EF4444" style={{ marginBottom: 16 }} />
          <Text style={styles.title}>حدث خطأ في {this.props.featureName}</Text>
          <Text style={styles.message}>{this.state.error?.message || 'خطأ غير معروف'}</Text>
          <TouchableOpacity style={styles.retryBtn} onPress={this.handleReset}>
            <RefreshCw size={18} stroke="#FFF" />
            <Text style={styles.retryText}>إعادة المحاولة</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.copyBtn} onPress={this.handleCopyDetails}>
            <Copy size={16} stroke="#6B7280" />
            <Text style={styles.copyText}>نسخ التفاصيل</Text>
          </TouchableOpacity>
        </View>
      );
    }
    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, backgroundColor: '#FFFFFF' },
  title: { fontSize: 18, fontWeight: '700', color: '#1A1226', textAlign: 'center', marginBottom: 8 },
  message: { fontSize: 14, color: '#6B7280', textAlign: 'center', marginBottom: 24 },
  retryBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#6B21A8', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 12 },
  retryText: { color: '#FFF', fontWeight: '600', fontSize: 15 },
  copyBtn: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 16, padding: 8 },
  copyText: { color: '#6B7280', fontSize: 13 },
});
