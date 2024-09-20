import { EExchange } from "@/global/types";
import { binanceClient } from "./_client";
import { OrderType } from "binance-api-node";
import { consolePretty } from "@/app/api/api-utils/consolePretty";

export async function sell({ asset, amount }: { asset: string; amount: number }) {
  console.log(`Processing Sell in ${EExchange.BINANCE} for symbol: ${asset} and amount: ${amount}`);

  try {
    // Market buy on Binance
    const order = await binanceClient.order({
      symbol: asset,
      side: "SELL",
      type: "MARKET" as OrderType.MARKET,
      quantity: amount.toString(),
    });

    console.log("Order executed successfully:");
    consolePretty(order);
  } catch (error) {
    console.error("Error executing order:", error);
  }
}
