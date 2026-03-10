import { SECRET } from 'config';
import { TokenError } from 'core/domain/errors';
import { NextFunction, Request, Response } from 'express';
import jwt from 'jsonwebtoken';

export interface CustomRequest extends Request {
  decoded: string | jwt.JwtPayload;
}

export async function authenticateToken(
  request: Request,
  response: Response,
  next: NextFunction
) {
  try {
    const authHeader = request.header('Authorization');
    let token = authHeader?.replace(/^Bearer\s+/i, '')?.trim();
    if (!token && request.cookies?.token) {
      token = request.cookies.token;
    }
    if (!token) {
      return response.status(401).json(new TokenError({}));
    }

    if (!SECRET) {
      return response.status(500).json({
        name: 'ConfigError',
        message: 'ACCESS_TOKEN_SECRET is not set. Ensure .env is loaded and the server was started from restaurant-api.',
      });
    }

    const decoded = jwt.verify(token, SECRET);

    (request as CustomRequest).decoded = decoded;

    next();
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unauthorized';
    const body = { ...(new TokenError({}) as object), debug: message };
    return response.status(401).json(body);
  }
}
