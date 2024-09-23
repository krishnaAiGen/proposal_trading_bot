import { withErrorHandling } from "@/app/api/api-utils/withErrorHandling";
import { ERROR_CODES } from "@/global/constants/errorLiterals";
import { APIError } from "@/global/exceptions";
import { StatusCodes } from "http-status-codes";
import { NextRequest, NextResponse } from "next/server";
import { getReqBody } from "@/app/api/api-utils/getReqBody";
import { EExchange } from "@/global/types";

export const maxDuration = 60;

export const POST = withErrorHandling(async (req: NextRequest) => {
  const { asset, exchange = EExchange.BINANCE } = await getReqBody(req);

  if (!asset) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid asset in request body");
  }

  if (!exchange || !Object.values(EExchange).includes(exchange as EExchange)) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid exchange in request body");
  }

  const sellResponse = await import(`./api-utils/exchanges/${exchange}/sell`).then(({ sell }) => sell({ asset }));

  if (!sellResponse) {
    throw new APIError(ERROR_CODES.INTERNAL_SERVER_ERROR, StatusCodes.INTERNAL_SERVER_ERROR, "Error selling asset");
  }

  return NextResponse.json({ sellResponse });
});
