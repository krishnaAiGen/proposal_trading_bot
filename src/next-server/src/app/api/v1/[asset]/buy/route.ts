import { withErrorHandling } from "@/app/api/api-utils/withErrorHandling";
import { ERROR_CODES } from "@/global/constants/errorLiterals";
import { APIError } from "@/global/exceptions";
import { StatusCodes } from "http-status-codes";
import { NextRequest, NextResponse } from "next/server";
import { getReqBody } from "@/app/api/api-utils/getReqBody";
import { EExchange, ETxAction } from "@/global/types";

export const maxDuration = 60;

export const POST = withErrorHandling(async (req: NextRequest) => {
  const { exchange, txAction, asset = "", amount = 0 } = await getReqBody(req);

  if (!exchange || !Object.values(EExchange).includes(exchange as EExchange)) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid exchange in request body");
  }

  if (!txAction || !Object.values(ETxAction).includes(txAction as ETxAction)) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid txAction in request body");
  }

  if (!asset) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid asset in request body");
  }

  if (!amount || amount <= 0 || isNaN(amount)) {
    throw new APIError(ERROR_CODES.BAD_REQUEST, StatusCodes.BAD_REQUEST, "Invalid amount in request body");
  }

  switch (txAction as ETxAction) {
    case ETxAction.BUY:
      await import(`./${exchange}/buy`).then(({ buy }) => buy({ asset, amount }));
      break;
    case ETxAction.SELL:
      await import(`./${exchange}/sell`).then(({ sell }) => sell({ asset, amount }));
      break;
  }

  return NextResponse.json({ message: "Success" });
});
