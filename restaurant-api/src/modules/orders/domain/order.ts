import { v4 as uuid } from 'uuid';
import { OrderItem } from './order-item';

export interface OrderProps {
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
  items: OrderItem[];
}

export class Order {
  readonly id: string;
  readonly customerName: string;
  readonly customerLastName: string;
  readonly customerPhone: string;
  readonly deliveryAddress: string;
  readonly district: string | null;
  readonly city: string;
  readonly state: string | null;
  readonly postalCode: string;
  readonly paymentMethod: string;
  readonly totalAmount: number;
  readonly status: string;
  readonly createdAt: string;
  readonly items: OrderItem[];

  constructor(props: Omit<Order, 'id' | 'createdAt'>, id?: string) {
    Object.assign(this, {
      id: id || uuid(),
      createdAt: new Date().toJSON(),
      ...props,
    });
  }
}
