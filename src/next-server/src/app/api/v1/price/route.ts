import { withErrorHandling } from "@/app/api/api-utils/withErrorHandling";
import { ERROR_CODES } from "@/global/constants/errorLiterals";
import { APIError } from "@/global/exceptions";
import { StatusCodes } from "http-status-codes";
import { NextRequest, NextResponse } from "next/server";
import { EExchange } from "@/global/types";

export const maxDuration = 60;

export const GET = withErrorHandling(async (req: NextRequest) => {
  const asset = req.nextUrl.searchParams.get("asset");

  if (!asset) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid asset in request query params");
  }

  const exchange = req.nextUrl.searchParams.get("exchange") || EExchange.BINANCE;

  if (!exchange || !Object.values(EExchange).includes(exchange as EExchange)) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid exchange in request query params");
  }

  const price =
    (await import(`@/app/api/api-utils/exchanges/${exchange}/price`).then(({ price }) => price({ asset }))) || "";

  if (!price) {
    throw new APIError(
      ERROR_CODES.INTERNAL_SERVER_ERROR,
      StatusCodes.INTERNAL_SERVER_ERROR,
      "Error fetching price from exchange"
    );
  }

  return NextResponse.json({ price });
});
