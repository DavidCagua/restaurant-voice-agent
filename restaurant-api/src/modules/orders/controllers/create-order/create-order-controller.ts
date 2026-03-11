import { Response } from 'express';
import { InternalServerError, ValidationError } from 'core/domain/errors';
import { bodyPropsIsEmpty } from 'core/controller/utils/body-props-is-empty';
import { CreateOrderUseCase } from 'modules/orders/use-cases/create-order/create-order-use-case';
import { CustomRequest } from 'infra/http/middleware/auth';

export interface CreateOrderBodyProps {
  customerName: string;
  customerLastName: string;
  customerPhone: string;
  deliveryAddress: string;
  district?: string | null;
  city: string;
  state?: string | null;
  postalCode: string;
  paymentMethod: string;
  items: Array<{
    productId: string;
    productName: string;
    quantity: number;
    unitPrice: number;
  }>;
}

export class CreateOrderController {
  constructor(private createOrderUseCase: CreateOrderUseCase) {}

  async handle(request: CustomRequest, response: Response) {
    const body = request.body as CreateOrderBodyProps;
    const {
      customerName,
      customerLastName,
      customerPhone,
      deliveryAddress,
      district,
      city,
      state,
      postalCode,
      paymentMethod,
      items,
    } = body;

    const processedDistrict = district ?? null;
    const processedState = state ?? null;

    if (
      bodyPropsIsEmpty({
        customerName,
        customerLastName,
        customerPhone,
        deliveryAddress,
        city,
        postalCode,
        paymentMethod,
      })
    ) {
      console.warn('[create-order] Validation failed: some required field is empty', {
        hasCustomerName: !!customerName,
        hasCustomerLastName: !!customerLastName,
        hasCustomerPhone: !!customerPhone,
        hasDeliveryAddress: !!deliveryAddress,
        hasCity: !!city,
        hasPostalCode: !!postalCode,
        hasPaymentMethod: !!paymentMethod,
      });
      return response.status(400).json(
        new ValidationError({
          message: 'Some required field is empty',
          action: 'Verify all fields and try again',
        })
      );
    }

    if (!items || !Array.isArray(items) || items.length === 0) {
      return response.status(400).json(
        new ValidationError({
          message: 'At least one order item is required',
          action: 'Add items to the order',
        })
      );
    }

    const invalidItems = items.filter(
      (item) =>
        !item.productId ||
        !item.productName ||
        typeof item.quantity !== 'number' ||
        item.quantity < 1 ||
        typeof item.unitPrice !== 'number' ||
        item.unitPrice < 0
    );
    if (invalidItems.length > 0) {
      console.warn('[create-order] Invalid order items:', { items, invalidCount: invalidItems.length });
      return response.status(400).json(
        new ValidationError({
          message: 'Invalid order items',
          action: 'Each item must have productId, productName, quantity (>0), and unitPrice (>=0)',
        })
      );
    }

    try {
      const resultOrError = await this.createOrderUseCase.execute({
        customerName,
        customerLastName,
        customerPhone,
        deliveryAddress,
        district: processedDistrict,
        city,
        state: processedState,
        postalCode,
        paymentMethod,
        items,
      });

      return response.status(201).json({
        id: resultOrError.value.id,
        message: 'Order created successfully',
      });
    } catch (err) {
      const message = (err as Error).message;
      console.error('[create-order] Error creating order:', message);
      return response
        .status(500)
        .json(new InternalServerError({ message }));
    }
  }
}
