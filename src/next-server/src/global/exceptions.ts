/* eslint-disable max-classes-per-file */

import { StatusCodes } from 'http-status-codes';
import { ERROR_CODES, ERROR_MESSAGES } from './constants/errorLiterals';

/**
 * @param {string} name
 * @param {string} [message]
 * @description Custom error class for client-side (react server component) errors
 * @returns {Error}
 *
 * Throws a client error with the given message and name
 * If no message is provided, it will default to the message associated with the name
 * If no name is provided, it will default to the CLIENT_ERROR name
 *
 * @example
 * throw new ClientError();
 * // is equivalent to
 * throw new ClientError(ERROR_CODES.API_FETCH_ERROR);
 * // is equivalent to
 * throw new ClientError(ERROR_CODES.API_FETCH_ERROR, ERROR_MESSAGES.API_FETCH_ERROR);
 *
 * // Always try to use a message from the ERROR_MESSAGES object
 * throw new ClientError(ERROR_CODES.API_FETCH_ERROR, ERROR_MESSAGES.INVALID_SEARCH_PARAMS_ERROR);
 *
 * // Or you can provide a custom message in scenarios like this :
 * const addressRes = await fetch(`https://example.com`).catch((e) => {
 *  throw new ClientError(ERROR_CODES.API_FETCH_ERROR, `${e?.message}`,);
	});
 */
export class ClientError extends Error {
	constructor(name?: string, message?: string) {
		super(message || ERROR_MESSAGES[String(name)] || ERROR_MESSAGES.CLIENT_ERROR);
		this.name = name || ERROR_CODES.CLIENT_ERROR;
	}
}

/**
 *
 * @param {string} name
 * @param {number} [status]
 * @param {string} [message]
 *
 * @description Custom error class for server-side (api backend) errors
 *
 * @returns {Error}
 * Throws a server error with the given name, status code and message
 * If no message is provided, it will default to the message associated with the name
 * If no name is provided, it will default to the API_FETCH_ERROR name
 * If no status is provided, it will default to the INTERNAL_SERVER_ERROR(500) status
 *
 * @example
 * throw new APIError();
 * // is equivalent to
 * throw new APIError(ERROR_CODES.API_FETCH_ERROR);
 * // is equivalent to
 * throw new APIError(ERROR_CODES.API_FETCH_ERROR, StatusCodes.INTERNAL_SERVER_ERROR, ERROR_MESSAGES.API_FETCH_ERROR);
 *
 * //Always use status code from the http-status-codes package
 * throw new APIError(ERROR_CODES.API_FETCH_ERROR, StatusCodes.INTERNAL_SERVER_ERROR);
 *
 * // Always try to use a message from the ERROR_MESSAGES object
 * throw new APIError(ERROR_CODES.API_FETCH_ERROR, StatusCodes.INTERNAL_SERVER_ERROR, ERROR_MESSAGES.INVALID_SEARCH_PARAMS_ERROR);
 *
 * // Or you can provide a custom message in scenarios like this :
 * const addressRes = await fetch(`https://example.com`).catch((e) => {
 *  throw new APIError(ERROR_CODES.API_FETCH_ERROR, StatusCodes.INTERNAL_SERVER_ERROR, `${e?.message}`,);
 * });
 */
export class APIError extends Error {
	status: StatusCodes;

	constructor(name?: string, status?: StatusCodes, message?: string) {
		super(message || ERROR_MESSAGES[String(name)] || ERROR_MESSAGES.API_FETCH_ERROR);
		this.name = name || ERROR_CODES.API_FETCH_ERROR;
		this.status = status || StatusCodes.INTERNAL_SERVER_ERROR;
	}
}
