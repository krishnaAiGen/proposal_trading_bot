import { binanceClient } from "./_client";

export async function getAssetBalance({ asset }: { asset: string }) {
  const accountInfo = await binanceClient.accountInfo();
  const balance = accountInfo.balances.find((balance) => balance.asset === asset);
  return balance?.free || "0";
}
