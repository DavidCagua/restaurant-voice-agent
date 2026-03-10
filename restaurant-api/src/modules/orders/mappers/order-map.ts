import { Order } from '../domain/order';
import { OrderItem } from '../domain/order-item';

export interface PersistenceOrderItem {
  id: string;
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
}

export interface PersistenceOrder {
  id: string;
  customerName: string;
  customerLastName: string;
  customerPhone: string;
  deliveryAddress: string;
  district: string | null;
  city: string;
  state: string | null;
  postalCode: string;
  paymentMethod: string;
  totalAmount: number;
  status: string;
  created_at: string;
  items: PersistenceOrderItem[];
}

export class OrderMap {
  static toPersistence(order: Order): PersistenceOrder {
    return {
      id: order.id,
      customerName: order.customerName,
      customerLastName: order.customerLastName,
      customerPhone: order.customerPhone,
      deliveryAddress: order.deliveryAddress,
      district: order.district,
      city: order.city,
      state: order.state,
      postalCode: order.postalCode,
      paymentMethod: order.paymentMethod,
      totalAmount: order.totalAmount,
      status: order.status,
      created_at: order.createdAt,
      items: order.items.map((item) => ({
        id: item.id,
        productId: item.productId,
        productName: item.productName,
        quantity: item.quantity,
        unitPrice: item.unitPrice,
      })),
    };
  }
}
