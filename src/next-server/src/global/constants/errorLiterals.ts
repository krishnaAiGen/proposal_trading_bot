export const ERROR_CODES = {
	API_FETCH_ERROR: 'API_FETCH_ERROR',
	INVALID_PARAMS_ERROR: 'INVALID_PARAMS_ERROR',
	REQ_BODY_ERROR: 'REQ_BODY_ERROR',
	CLIENT_ERROR: 'CLIENT_ERROR',
	INTERNAL_SERVER_ERROR: 'INTERNAL_SERVER_ERROR',
	UNAUTHORIZED: 'UNAUTHORIZED',
	NOT_FOUND: 'NOT_FOUND',
	BAD_REQUEST: 'BAD_REQUEST',
	MISSING_REQUIRED_FIELDS: 'MISSING_REQUIRED_FIELDS',
	INVALID_REQUIRED_FIELDS: 'INVALID_REQUIRED_FIELDS',
};

export const ERROR_MESSAGES = {
	[ERROR_CODES.API_FETCH_ERROR]: 'Something went wrong while fetching data. Please try again later.',
	[ERROR_CODES.INVALID_PARAMS_ERROR]: 'Invalid parameters passed to the url.',
	[ERROR_CODES.REQ_BODY_ERROR]: 'Something went wrong while parsing the request body.',
	[ERROR_CODES.CLIENT_ERROR]: 'Something went wrong while fetching data on the client. Please try again later.',
	[ERROR_CODES.INTERNAL_SERVER_ERROR]: 'Something went wrong on the server. Please try again later.',
	[ERROR_CODES.UNAUTHORIZED]: 'Unauthorized request.',
	[ERROR_CODES.NOT_FOUND]: 'Resource not found.',
	[ERROR_CODES.BAD_REQUEST]: 'Bad request.',
	[ERROR_CODES.MISSING_REQUIRED_FIELDS]: 'Missing required fields.',
	[ERROR_CODES.INVALID_REQUIRED_FIELDS]: 'Invalid required fields.',
};
