import { EExchange } from "@/global/types";
import { binanceClient } from "./_client";
import { APIError } from "@/global/exceptions";
import { ERROR_CODES } from "@/global/constants/errorLiterals";
import { StatusCodes } from "http-status-codes";

export async function price({ asset }: { asset: string }): Promise<string> {
  console.log(`Fetching price in ${EExchange.BINANCE} for symbol: ${asset}`);

  try {
    // Fetch price
    const priceResult = await binanceClient.prices({
      symbol: asset,
    });
    console.log(`Price fetched successfully: ${priceResult}`);

    if (!priceResult?.[asset]) {
      throw new APIError(
        ERROR_CODES.INTERNAL_SERVER_ERROR,
        StatusCodes.INTERNAL_SERVER_ERROR,
        "Error in fetching price"
      );
    }

    const price = priceResult?.[asset] || "";

    return price;
  } catch (error) {
    console.error("Error fetching price:", error);
    throw new APIError(ERROR_CODES.INTERNAL_SERVER_ERROR, StatusCodes.INTERNAL_SERVER_ERROR, "Error fetching price");
  }
}
