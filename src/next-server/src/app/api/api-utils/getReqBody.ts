import { ERROR_CODES, ERROR_MESSAGES } from '@/global/constants/errorLiterals';

export async function getReqBody(req: Request) {
	try {
		return await req.json();
	} catch (error) {
		console.log(ERROR_MESSAGES.REQ_BODY_ERROR, 500, ERROR_CODES.REQ_BODY_ERROR);
		return {};
	}
}
