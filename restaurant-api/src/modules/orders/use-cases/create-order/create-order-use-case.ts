import { UseCase } from 'core/domain/UseCase';
import { Either, right } from 'core/logic/either';
import { Order } from 'modules/orders/domain/order';
import { OrderItem } from 'modules/orders/domain/order-item';
import { OrderMap } from 'modules/orders/mappers/order-map';
import { IOrdersRepository } from 'modules/orders/repositories/orders-repository';

export interface OrderItemRequest {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
}

export interface CreateOrderRequest {
  customerName: string;
  customerLastName: string;
  customerPhone: string;
  deliveryAddress: string;
  district: string | null;
  city: string;
  state: string | null;
  postalCode: string;
  paymentMethod: string;
  items: OrderItemRequest[];
}

type CreateOrderResponse = Either<never, { id: string }>;

export class CreateOrderUseCase
  implements UseCase<CreateOrderRequest, CreateOrderResponse>
{
  constructor(private ordersRepository: IOrdersRepository) {}

  async execute(request: CreateOrderRequest): Promise<CreateOrderResponse> {
    const totalAmount = request.items.reduce(
      (sum, item) => sum + item.quantity * item.unitPrice,
      0
    );

    const orderItems = request.items.map(
      (item) =>
        new OrderItem({
          productId: item.productId,
          productName: item.productName,
          quantity: item.quantity,
          unitPrice: item.unitPrice,
        })
    );

    const order = new Order({
      customerName: request.customerName,
      customerLastName: request.customerLastName,
      customerPhone: request.customerPhone,
      deliveryAddress: request.deliveryAddress,
      district: request.district,
      city: request.city,
      state: request.state,
      postalCode: request.postalCode,
      paymentMethod: request.paymentMethod,
      totalAmount,
      status: 'pending',
      items: orderItems,
    });

    const persistenceOrder = OrderMap.toPersistence(order);
    await this.ordersRepository.save(persistenceOrder);

    return right({ id: order.id });
  }
}
