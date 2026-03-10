import { prisma } from 'infra/prisma/client';
import { PersistenceOrder } from 'modules/orders/mappers/order-map';
import { IOrdersRepository } from '../orders-repository';

export class PrismaOrdersRepository implements IOrdersRepository {
  async save({
    id,
    customerName,
    customerLastName,
    customerPhone,
    deliveryAddress,
    district,
    city,
    state,
    postalCode,
    paymentMethod,
    totalAmount,
    status,
    created_at,
    items,
  }: PersistenceOrder): Promise<void> {
    await prisma.order.create({
      data: {
        id,
        customerName,
        customerLastName,
        customerPhone,
        deliveryAddress,
        district,
        city,
        state,
        postalCode,
        paymentMethod,
        totalAmount,
        status,
        created_at,
        items: {
          create: items.map((item) => ({
            id: item.id,
            productId: item.productId,
            productName: item.productName,
            quantity: item.quantity,
            unitPrice: item.unitPrice,
          })),
        },
      },
    });
  }
}
