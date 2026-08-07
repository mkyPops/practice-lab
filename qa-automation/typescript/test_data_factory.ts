/**
 * Test data factory
 *
 * Provides typed builder functions backed by Faker to produce realistic,
 * randomized fixtures for common QA scenarios (users, addresses, products,
 * orders). Each factory accepts a partial override object so individual
 * tests can pin down specific fields while letting the rest be randomized.
 */

import { faker } from '@faker-js/faker';

export interface Address {
  street: string;
  city: string;
  postalCode: string;
  country: string;
}

export interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  address: Address;
  createdAt: Date;
}

export interface Product {
  id: string;
  name: string;
  price: number;
  sku: string;
  inStock: boolean;
}

export interface OrderItem {
  product: Product;
  quantity: number;
}

export interface Order {
  id: string;
  user: User;
  items: OrderItem[];
  total: number;
  placedAt: Date;
}

// Allow deterministic runs when a seed is provided (e.g. from CI env var).
export function seedFactory(seed: number): void {
  faker.seed(seed);
}

export function createAddress(overrides: Partial<Address> = {}): Address {
  return {
    street: faker.location.streetAddress(),
    city: faker.location.city(),
    postalCode: faker.location.zipCode(),
    country: faker.location.country(),
    ...overrides,
  };
}

export function createUser(overrides: Partial<User> = {}): User {
  const firstName = faker.person.firstName();
  const lastName = faker.person.lastName();
  return {
    id: faker.string.uuid(),
    firstName,
    lastName,
    email: faker.internet.email({ firstName, lastName }).toLowerCase(),
    address: createAddress(),
    createdAt: faker.date.past(),
    ...overrides,
  };
}

export function createProduct(overrides: Partial<Product> = {}): Product {
  return {
    id: faker.string.uuid(),
    name: faker.commerce.productName(),
    price: Number(faker.commerce.price({ min: 1, max: 500 })),
    sku: faker.string.alphanumeric(8).toUpperCase(),
    inStock: faker.datatype.boolean(),
    ...overrides,
  };
}

export function createOrder(overrides: Partial<Order> = {}): Order {
  const items: OrderItem[] = Array.from(
    { length: faker.number.int({ min: 1, max: 5 }) },
    () => ({ product: createProduct(), quantity: faker.number.int({ min: 1, max: 3 }) }),
  );
  const total = items.reduce((sum, item) => sum + item.product.price * item.quantity, 0);

  return {
    id: faker.string.uuid(),
    user: createUser(),
    items,
    total: Number(total.toFixed(2)),
    placedAt: faker.date.recent(),
    ...overrides,
  };
}

// Convenience helper for bulk fixture generation, e.g. seeding a test DB.
export function createMany<T>(
  factory: (overrides?: Partial<T>) => T,
  count: number,
  overrides: Partial<T> = {},
): T[] {
  return Array.from({ length: count }, () => factory(overrides));
}
