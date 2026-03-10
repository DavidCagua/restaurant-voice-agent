import { CreateOrderController } from '../controllers/create-order/create-order-controller';
import { PrismaOrdersRepository } from '../repositories/prisma/prisma-orders-repository';
import { CreateOrderUseCase } from '../use-cases/create-order/create-order-use-case';

export const createOrderFactory = () => {
  const ordersRepository = new PrismaOrdersRepository();
  const createOrderUseCase = new CreateOrderUseCase(ordersRepository);
  const createOrderController = new CreateOrderController(createOrderUseCase);

  return createOrderController;
};
