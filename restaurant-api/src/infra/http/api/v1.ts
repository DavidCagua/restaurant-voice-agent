import { Router } from 'express';
import { addressRouter } from 'modules/addresses/infra/http/routes';
import { orderRouter } from 'modules/orders/infra/http/routes';
import { productRouter } from 'modules/products/infra/http/routes';
import { userRouter } from 'modules/users/infra/http/routes';

const router = Router();

router.use(userRouter);
router.use(addressRouter);
router.use(productRouter);
router.use(orderRouter);

export { router };
