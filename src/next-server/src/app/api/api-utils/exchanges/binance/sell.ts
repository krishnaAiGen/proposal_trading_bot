import { EExchange, ISellResponse } from "@/global/types";
import { binanceClient } from "./_client";
import { OrderType } from "binance-api-node";
import { consolePretty } from "@/app/api/api-utils/consolePretty";
import { getAssetBalance } from "./getAssetBalance";

export async function sell({ asset }: { asset: string }) {
  console.log(`Processing Sell in ${EExchange.BINANCE} for asset: ${asset}`);

  // fetch the current quantity of the asset
  const quantity = await getAssetBalance({ asset });

  try {
    // Market sell on Binance
    const order = await binanceClient.futuresOrder({
      symbol: asset,
      side: "SELL",
      type: "MARKET" as OrderType.MARKET,
      quantity,
    });

    console.log("Sell order executed successfully:");
    consolePretty({ order });

    return {
      sellOrderId: order.orderId,
      asset,
      sellPrice: order.price,
      timestamp: new Date(),
      quantity,
    } as ISellResponse;
  } catch (error) {
    console.error("Error executing order:", error);
  }
}
