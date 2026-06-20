import { Platform } from "react-native";
import {
  initConnection,
  getProducts as iapGetProducts,
  requestSubscription,
  getAvailablePurchases,
  acknowledgePurchaseAndroid,
  finishTransaction,
  endConnection,
  type Product,
  type Purchase,
} from "react-native-iap";

const PRODUCT_IDS: string[] = [
  "plus_monthly",
  "premium_monthly",
  "pro_semiannual",
  "yearly_annual",
];

export const TIER_MAP: Record<string, string> = {
  plus_monthly:    "plus",
  premium_monthly: "premium",
  pro_semiannual:  "pro",
  yearly_annual:   "yearly",
};

let isPurchasing = false;

export async function initIAP(): Promise<boolean> {
  try {
    await initConnection();
    console.log("Google Play Billing connected");
    return true;
  } catch (e) {
    console.error("initIAP error:", e);
    return false;
  }
}

export async function getProducts(): Promise<Product[]> {
  try {
    return await iapGetProducts({ skus: PRODUCT_IDS });
  } catch (e) {
    console.error("getProducts error:", e);
    return [];
  }
}

export async function purchaseSubscription(productId: string): Promise<string | null> {
  if (isPurchasing) return null;
  isPurchasing = true;
  try {
    const purchase = await requestSubscription({ sku: productId });
    if (!purchase) return null;

    const p = purchase as any;
    const token = p.purchaseToken || p.transactionReceipt || "";
    if (!token) return null;

    // Android: acknowledge
    if (Platform.OS === "android" && p.purchaseToken) {
      try {
        await acknowledgePurchaseAndroid({ purchaseToken: p.purchaseToken });
      } catch (e) {
        console.warn("acknowledge error:", e);
      }
    }

    // iOS: finish
    if (Platform.OS === "ios" && p.transactionId) {
      try {
        await finishTransaction({ transactionId: p.transactionId });
      } catch (e) {
        console.warn("finishTransaction error:", e);
      }
    }

    return token;
  } catch (err: any) {
    if (err?.code === "E_USER_CANCELLED") return null;
    console.error("purchase error:", err);
    return null;
  } finally {
    isPurchasing = false;
  }
}

export async function restorePurchases(): Promise<Purchase[]> {
  try {
    return await getAvailablePurchases();
  } catch (e) {
    console.error("restorePurchases error:", e);
    return [];
  }
}

export function disconnectIAP(): void {
  try { endConnection(); } catch {}
}

export function getTierFromProductId(productId: string): string {
  return TIER_MAP[productId] || "free";
}
