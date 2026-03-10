import { Router } from 'express';
import { CustomRequest, authenticateToken } from 'infra/http/middleware/auth';
import { createOrderFactory } from 'modules/orders/factories/create-order-factory';

const orderRouter = Router();

orderRouter.post('/orders', authenticateToken, (request, response) => {
  return createOrderFactory().handle(request as CustomRequest, response);
});

export { orderRouter };
