import { Either, left, right } from 'core/logic/either';
import { PostalCodeInvalidError } from './errors';
import validator from 'validator';

export class PostalCode {
  constructor(private readonly postalCode: string) {
    this.postalCode = postalCode;
  }

  get value(): string {
    return this.postalCode;
  }

  static create(
    postalCode: string
  ): Either<PostalCodeInvalidError, PostalCode> {
    // Handle null/undefined cases
    if (!postalCode || typeof postalCode !== 'string') {
      return left(new PostalCodeInvalidError({}));
    }

    // Check for Brazilian postal code format (default)
    if (validator.isPostalCode(postalCode, 'BR')) {
      return right(new PostalCode(postalCode));
    }

    // Check for US postal code format
    if (validator.isPostalCode(postalCode, 'US')) {
      return right(new PostalCode(postalCode));
    }

    // Check for Colombian postal code format (5 digits)
    if (/^\d{5}$/.test(postalCode)) {
      return right(new PostalCode(postalCode));
    }

    // Check for general postal code patterns
    if (/^\d{4,6}$/.test(postalCode)) {
      return right(new PostalCode(postalCode));
    }

    return left(new PostalCodeInvalidError({}));
  }
}
