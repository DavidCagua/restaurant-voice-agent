import validator from 'validator';

export function bodyPropsIsEmpty<T>(props: T): boolean {
  for (const value of Object.values(props as object)) {
    // Handle null, undefined, and empty values properly
    if (value === null || value === undefined) {
      return true;
    }

    if (typeof value === 'string' && validator.isEmpty(value)) {
      return true;
    }

    if (typeof value === 'number' && isNaN(value)) {
      return true;
    }
  }

  return false;
}
