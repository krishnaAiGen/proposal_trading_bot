export enum ETxAction {
  BUY = "buy",
  SELL = "sell",
}

export enum EExchange {
  BINANCE = "binance",
  // BYBIT = 'bybit', //TODO: add bybit
}

export enum ESentiment {
  BULLISH = "bullish",
  BEARISH = "bearish",
}

export interface IBuyResponse {
  buyOrderId: number;
  asset: string;
  buyPrice: string;
  stopLossOrderId: number;
  stopLossPrice: string;
  timestamp: Date;
  quantity: string;
}

export interface ISellResponse {
  sellOrderId: number;
  asset: string;
  sellPrice: string;
  timestamp: Date;
  quantity: string;
}
