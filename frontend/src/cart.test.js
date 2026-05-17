import { expect, test } from 'vitest'

const calculateTotal = (items) => {
  return items.reduce((acc, item) => acc + (item.price * item.quantity), 0)
}

test('Calcular total del carrito correctamente', () => {
  const items = [
    { price: 10, quantity: 2 },
    { price: 5, quantity: 1 }
  ]
  expect(calculateTotal(items)).toBe(25)
})