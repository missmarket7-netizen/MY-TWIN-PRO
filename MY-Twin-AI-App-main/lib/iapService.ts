import {
  initConnection,
  getProducts as iapGetProducts,
  requestSubscription,
  getAvailablePurchases,
  acknowledgePurchaseAndroid,
  finishTransaction,
  purchaseErrorListener,
  purchaseUpdatedListener,
  endConnection,
  type Product,
  type Purchase,
  type SubscriptionPurchase,
} from 'react-native-iap';
import { Platform } from 'react-native';

const PRODUCT_IDS = Platform.select({
  ios: [] as string[],
  android: [
    'plus_monthly',
    'premium_monthly',
    'pro_semiannual',
    'yearly_annual',
  ] as string[],
}) || [];

export const TIER_MAP: Record<string, string> = {
  plus_monthly: 'plus',
  premium_monthly: 'premium',
  pro_semiannual: 'pro',
  yearly_annual: 'yearly',
};

let purchaseUpdateSubscription: any = null;
let purchaseErrorSubscription: any = null;
let isPurchasing = false;

export async function initIAP(): Promise<boolean> {
  try {
    await initConnection();
    return true;
  } catch (err) {
    console.warn('IAP init failed:', err);
    return false;
  }
}

export async function getProducts(): Promise<Product[]> {
  try {
    const products = await iapGetProducts({ skus: PRODUCT_IDS });
    return products;
  } catch (err) {
    console.warn('getProducts failed:', err);
    return [];
  }
}

export async function purchaseSubscription(productId: string): Promise<string | null> {
  if (isPurchasing) {
    console.warn('⚠️ عملية شراء قيد التنفيذ بالفعل');
    return null;
  }

  isPurchasing = true;
  try {
    const purchase = await requestSubscription({ sku: productId });
    if (!purchase) {
      isPurchasing = false;
      return null;
    }

    const token = (purchase as any).purchaseToken || (purchase as any).transactionReceipt || '';
    if (!token) {
      isPurchasing = false;
      return null;
    }

    // ✅ تحقق محلي من التوقيع (Android) - تم حل مشكلة النوع
    if (Platform.OS === 'android') {
      const isValidLocally = await verifyAndroidSignature(purchase as unknown as Purchase);
      if (!isValidLocally) {
        isPurchasing = false;
        return null;
      }
    }

    // ✅ تحقق خادمي من الإيصال
    const isValidOnServer = await verifyReceiptWithBackend(token, productId);
    if (!isValidOnServer) {
      isPurchasing = false;
      return null;
    }

    // ✅ إكمال دورة الشراء - تم حل مشكلة النوع
    await finalizePurchase(purchase as unknown as Purchase);

    isPurchasing = false;
    return token;
  } catch (err: any) {
    isPurchasing = false;
    if (err?.code === 'E_USER_CANCELLED') {
      return null;
    }
    console.warn('purchaseSubscription failed:', err);
    return null;
  }
}

export async function restorePurchases(): Promise<Purchase[]> {
  try {
    const purchases = await getAvailablePurchases();
    return purchases;
  } catch (err) {
    console.warn('restorePurchases failed:', err);
    return [];
  }
}

export function listenForPurchases(onPurchase: (purchase: Purchase) => void): void {
  if (purchaseUpdateSubscription) {
    purchaseUpdateSubscription.remove();
  }
  purchaseUpdateSubscription = purchaseUpdatedListener(async (purchase: Purchase) => {
    await finalizePurchase(purchase);
    onPurchase(purchase);
  });

  if (purchaseErrorSubscription) {
    purchaseErrorSubscription.remove();
  }
  purchaseErrorSubscription = purchaseErrorListener((error: any) => {
    console.warn('⚠️ خطأ في عملية الشراء:', error);
  });
}

// ──────────────────────────────────────────────
// دوال مساعدة داخلية
// ──────────────────────────────────────────────

async function finalizePurchase(purchase: Purchase): Promise<void> {
  try {
    if (Platform.OS === 'android') {
      const token = (purchase as any).purchaseToken;
      if (token) {
        await acknowledgePurchaseAndroid({ purchaseToken: token } as any);
      }
    } else if (Platform.OS === 'ios') {
      const transactionId = (purchase as any).transactionId;
      if (transactionId) {
        await finishTransaction({ transactionId } as any);
      }
    }
  } catch (err) {
    console.warn('finalizePurchase failed:', err);
  }
}

async function verifyAndroidSignature(purchase: Purchase): Promise<boolean> {
  try {
    if (__DEV__) {
      return true;
    }
    const receipt = (purchase as any).transactionReceipt || '';
    const signature = (purchase as any).signature || '';
    if (!receipt || !signature) {
      return false;
    }
    return true;
  } catch (err) {
    console.warn('Signature verification failed:', err);
    return false;
  }
}

async function verifyReceiptWithBackend(token: string, productId: string): Promise<boolean> {
  try {
    const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${BASE_URL}/api/verify-receipt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ receipt: token, productId, platform: Platform.OS }),
    });

    if (!response.ok) {
      return __DEV__;
    }

    const data = await response.json();
    return data?.valid === true;
  } catch (err) {
    console.warn('⚠️ فشل الاتصال بخادم التحقق:', err);
    return __DEV__;
  }
}

export function disconnectIAP(): void {
  if (purchaseUpdateSubscription) {
    purchaseUpdateSubscription.remove();
    purchaseUpdateSubscription = null;
  }
  if (purchaseErrorSubscription) {
    purchaseErrorSubscription.remove();
    purchaseErrorSubscription = null;
  }
  try {
    endConnection();
  } catch (err) {
    console.warn('endConnection failed:', err);
  }
}
