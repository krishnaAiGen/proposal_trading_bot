import { BINANCE_API_KEY, BINANCE_SECRET_KEY } from "@/global/envVars";
import Binance from "binance-api-node";

export const binanceClient = Binance({
  apiKey: BINANCE_API_KEY,
  apiSecret: BINANCE_SECRET_KEY,
  httpBase: "https://api.binance.com",
  wsBase: "wss://stream.binance.com:443",
});
