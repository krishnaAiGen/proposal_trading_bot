/* eslint-disable @typescript-eslint/no-explicit-any */
import util from 'util';

/*
 * Pretty console log
 * @param data - data to be logged
 * @returns void
 * @example
 * pretty_console(data);
 * only use in server side code
 */
export function consolePretty(data: any) {
	console.log(util.inspect(data, false, null, true));
}
