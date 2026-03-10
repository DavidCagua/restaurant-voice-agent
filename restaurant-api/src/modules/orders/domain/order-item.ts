import { v4 as uuid } from 'uuid';

export interface OrderItemProps {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
}

export class OrderItem {
  readonly id: string;
  readonly productId: string;
  readonly productName: string;
  readonly quantity: number;
  readonly unitPrice: number;

  constructor(props: OrderItemProps, id?: string) {
    Object.assign(this, {
      id: id || uuid(),
      ...props,
    });
  }
}
