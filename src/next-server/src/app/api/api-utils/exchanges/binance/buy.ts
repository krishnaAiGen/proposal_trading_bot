import { EExchange, ESentiment, IBuyResponse } from "@/global/types";
import { binanceClient } from "./_client";
import { OrderType } from "binance-api-node";
import { consolePretty } from "@/app/api/api-utils/consolePretty";
import { STOP_LOSS_PERCENTAGE } from "@/app/api/constants/stopLossPercentage";
import { getAssetBalance } from "./getAssetBalance";
import { STABLE_ASSET } from "@/app/api/constants/stableAsset";
import { USEABLE_BALANCE_PERCENTAGE } from "@/app/api/constants/useableBalancePercentage";
import { LEVERAGE_MULTIPLIER } from "@/app/api/constants/leverageMultiplier";

export async function buy({ asset, sentiment }: { asset: string; sentiment: ESentiment }) {
  console.log(
    `Processing ${sentiment === ESentiment.BULLISH ? "Buy" : "Short"} in ${EExchange.BINANCE} for symbol: ${asset}`
  );

  const stableAssetBalance = await getAssetBalance({ asset: STABLE_ASSET });

  const quantity = (parseFloat(stableAssetBalance) * (USEABLE_BALANCE_PERCENTAGE / 100)).toString();

  try {
    await binanceClient.futuresLeverage({ symbol: asset, leverage: LEVERAGE_MULTIPLIER });
    await binanceClient.futuresMarginType({ symbol: asset, marginType: "CROSSED" });

    // Determine order side based on sentiment
    const side = sentiment === ESentiment.BULLISH ? "BUY" : "SELL";

    // Use futures API for both long and short positions
    const order = await binanceClient.futuresOrder({
      symbol: asset,
      side,
      type: "MARKET" as OrderType.MARKET,
      quantity,
    });

    console.log(`${sentiment === ESentiment.BULLISH ? "Buy" : "Short"} order executed successfully:`);
    consolePretty({ order });

    // Get the latest price
    const ticker = await binanceClient.futuresPrices({ symbol: asset });
    const currentPrice = parseFloat(ticker.price);

    // Calculate stop loss price
    const stopLossPrice =
      sentiment === ESentiment.BULLISH
        ? currentPrice * (1 - STOP_LOSS_PERCENTAGE / 100)
        : currentPrice * (1 + STOP_LOSS_PERCENTAGE / 100);

    // Place stop loss order
    const stopLossSide = sentiment === ESentiment.BULLISH ? "SELL" : "BUY";
    const stopLossOrder = await binanceClient.futuresOrder({
      symbol: asset,
      side: stopLossSide,
      type: "STOP_MARKET" as OrderType.STOP_MARKET,
      quantity,
      stopPrice: stopLossPrice.toFixed(8),
    });

    console.log("Stop loss order placed successfully:");
    consolePretty(stopLossOrder);

    return {
      buyOrderId: order.orderId,
      asset,
      stopLossOrderId: stopLossOrder.orderId,
      buyPrice: currentPrice.toString(),
      stopLossPrice: stopLossPrice.toString(),
      timestamp: new Date(),
      quantity,
    } as IBuyResponse;
  } catch (error) {
    console.error("Error executing order:", error);
  }
}
