import { APIError } from "@/global/exceptions";
import { NextRequest, NextResponse } from "next/server";
import { consolePretty } from "./consolePretty";
import { API_KEY, BINANCE_API_KEY, BINANCE_SECRET_KEY } from "@/global/envVars";
import { ERROR_CODES } from "@/global/constants/errorLiterals";
import { StatusCodes } from "http-status-codes";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const withErrorHandling = (handler: { (req: NextRequest, options?: any): Promise<NextResponse> }) => {
  return async (req: NextRequest, options: object) => {
    try {
      if (!API_KEY || !BINANCE_API_KEY || !BINANCE_SECRET_KEY) {
        throw new APIError(
          ERROR_CODES.INTERNAL_SERVER_ERROR,
          StatusCodes.INTERNAL_SERVER_ERROR,
          "Env not configured. Please check env vars"
        );
      }

      // check if api key is valid
      const headerApiKey = req.headers.get("x-api-key") || "";
      if (headerApiKey !== API_KEY) {
        throw new APIError(ERROR_CODES.UNAUTHORIZED, StatusCodes.UNAUTHORIZED, "Invalid API Key");
      }

      return await handler(req, options);
    } catch (error) {
      const err = error as APIError;
      console.log("Error in API call : ", req.nextUrl);
      consolePretty({ err });
      return NextResponse.json({ ...err, message: err.message }, { status: err.status });
    }
  };
};
