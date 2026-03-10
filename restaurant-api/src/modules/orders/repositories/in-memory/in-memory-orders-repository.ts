import { PersistenceOrder } from 'modules/orders/mappers/order-map';
import { IOrdersRepository } from '../orders-repository';

export class InMemoryOrdersRepository implements IOrdersRepository {
  public orders: PersistenceOrder[] = [];

  async save(order: PersistenceOrder): Promise<void> {
    this.orders.push(order);
  }
}
