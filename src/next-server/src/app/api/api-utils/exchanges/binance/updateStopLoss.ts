import { APIError } from "@/global/exceptions";
import { binanceClient } from "./_client";
import { ERROR_CODES } from "@/global/constants/errorLiterals";
import { StatusCodes } from "http-status-codes";
import { OrderType } from "binance-api-node";
import { ESentiment } from "@/global/types";
import { STOP_LOSS_PERCENTAGE } from "@/app/api/constants/stopLossPercentage";
import { consolePretty } from "../../consolePretty";

export async function updateStopLoss({
  asset,
  stopLossOrderId,
  sentiment,
}: {
  asset: string;
  stopLossOrderId: string;
  sentiment: ESentiment;
}) {
  const stopLossOrder = await binanceClient.futuresGetOrder({ symbol: asset, orderId: parseInt(stopLossOrderId) });

  if (!stopLossOrder) {
    throw new APIError(ERROR_CODES.NOT_FOUND, StatusCodes.NOT_FOUND, "Stop loss order not found");
  }

  const quantity = stopLossOrder.origQty;

  // cancel the stop loss order
  await binanceClient.futuresCancelOrder({ symbol: asset, orderId: parseInt(stopLossOrderId) });

  // Get the latest price
  const ticker = await binanceClient.futuresPrices({ symbol: asset });
  const currentPrice = parseFloat(ticker[asset]);

  // Calculate new stop loss price
  const newStopLossPrice =
    sentiment === ESentiment.BULLISH
      ? currentPrice * (1 + STOP_LOSS_PERCENTAGE / 100)
      : currentPrice * (1 - STOP_LOSS_PERCENTAGE / 100);

  console.log("New stop loss price:", newStopLossPrice);

  // Place new stop loss order
  const stopLossSide = sentiment === ESentiment.BULLISH ? "SELL" : "BUY";

  const newStopLossOrder = await binanceClient.futuresOrder({
    symbol: asset,
    side: stopLossSide,
    type: "STOP_MARKET" as OrderType.STOP_MARKET,
    quantity,
    stopPrice: newStopLossPrice.toFixed(8),
  });

  console.log("New stop loss order placed successfully:");
  consolePretty({ newStopLossOrder });

  return newStopLossOrder;
}
