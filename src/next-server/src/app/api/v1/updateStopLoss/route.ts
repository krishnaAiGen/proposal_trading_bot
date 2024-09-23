import { withErrorHandling } from "@/app/api/api-utils/withErrorHandling";
import { ERROR_CODES } from "@/global/constants/errorLiterals";
import { APIError } from "@/global/exceptions";
import { StatusCodes } from "http-status-codes";
import { NextRequest, NextResponse } from "next/server";
import { getReqBody } from "@/app/api/api-utils/getReqBody";
import { EExchange, ESentiment } from "@/global/types";

export const maxDuration = 60;

export const POST = withErrorHandling(async (req: NextRequest) => {
  const { exchange = EExchange.BINANCE, asset, stopLossOrderId, sentiment } = await getReqBody(req);

  if (!asset) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid asset in request body");
  }

  if (!stopLossOrderId) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid stop loss order id in request body");
  }

  if (!exchange || !Object.values(EExchange).includes(exchange as EExchange)) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid exchange in request body");
  }

  if (!sentiment || !Object.values(ESentiment).includes(sentiment as ESentiment)) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid sentiment in request body");
  }

  const updateStopLossResponse = await import(`./api-utils/exchanges/${exchange}/updateStopLoss`).then(
    ({ updateStopLoss }) => updateStopLoss({ asset, stopLossOrderId, sentiment })
  );

  if (!updateStopLossResponse) {
    throw new APIError(
      ERROR_CODES.INTERNAL_SERVER_ERROR,
      StatusCodes.INTERNAL_SERVER_ERROR,
      "Error updating stop loss"
    );
  }

  return NextResponse.json({ updateStopLossResponse });
});
