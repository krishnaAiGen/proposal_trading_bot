// import { BYBIT_API_KEY, BYBIT_SECRET_KEY } from "@/global/envVars";
import { SpotClientV3 } from "bybit-api";

export const bybitClient = new SpotClientV3({
  key: "BYBIT_API_KEY",
  secret: "BYBIT_SECRET_KEY",
  testnet: false,
});
