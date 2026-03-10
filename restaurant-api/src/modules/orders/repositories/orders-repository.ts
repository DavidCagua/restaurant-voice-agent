import { PersistenceOrder } from '../mappers/order-map';

export interface IOrdersRepository {
  save(order: PersistenceOrder): Promise<void>;
}
