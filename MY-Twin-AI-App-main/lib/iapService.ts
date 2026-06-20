import { Platform, Linking, Alert } from "react-native";
import { apiPost } from "./httpClient";

const DEEP_LINK_BASE = "https://mytwin.app/subscribe";

const PRODUCT_IDS: string[] = [
  "plus_monthly", "premium_monthly", "pro_semiannual", "yearly_annual",
];

export const TIER_MAP: Record<string, string> = {
  plus_monthly: "plus",
  premium_monthly: "premium",
  pro_semiannual: "pro",
  yearly_annual: "yearly",
};

export async function initIAP(): Promise<boolean> {
  return true;
}

export async function getProducts(): Promise<any[]> {
  return PRODUCT_IDS.map(id => ({
    productId: id,
    localizedPrice: getPriceForProduct(id),
    price: getNumericPrice(id),
    currency: "USD",
    title: id,
    description: "",
  }));
}

export async function purchaseSubscription(productId: string, userId: string): Promise<void> {
  const url = `${DEEP_LINK_BASE}?product=${productId}&user=${userId}`;
  
  try {
    await Linking.openURL(url);
  } catch (error) {
    Alert.alert("Error", "Could not open subscription page. Please try again.");
  }
}

export async function restorePurchases(): Promise<any[]> {
  return [];
}

export function disconnectIAP(): void {}

export function getTierFromProductId(productId: string): string {
  return TIER_MAP[productId] || "free";
}

function getPriceForProduct(id: string): string {
  const prices: Record<string, string> = {
    plus_monthly: "$5.99",
    premium_monthly: "$14.99", 
    pro_semiannual: "$110",
    yearly_annual: "$199",
  };
  return prices[id] || "$0";
}

function getNumericPrice(id: string): number {
  const prices: Record<string, number> = {
    plus_monthly: 5.99,
    premium_monthly: 14.99,
    pro_semiannual: 110,
    yearly_annual: 199,
  };
  return prices[id] || 0;
}
