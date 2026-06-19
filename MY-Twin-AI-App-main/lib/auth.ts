import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

const TOKEN_KEY = 'mytwin_auth_token';
let memoryToken: string | null = null;

export async function storeToken(token: string): Promise<void> {
  try {
    if (Platform.OS === 'web') { memoryToken = token; return; }
    await SecureStore.setItemAsync(TOKEN_KEY, token);
  } catch { memoryToken = token; }
}

export async function getToken(): Promise<string | null> {
  try {
    if (Platform.OS === 'web') return memoryToken;
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch { return memoryToken; }
}

export async function removeToken(): Promise<void> {
  try {
    if (Platform.OS === 'web') { memoryToken = null; return; }
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  } catch { memoryToken = null; }
}

export function setTokenSync(token: string): void {
  memoryToken = token;
  if (Platform.OS !== 'web') {
    SecureStore.setItemAsync(TOKEN_KEY, token).catch(() => {});
  }
}
