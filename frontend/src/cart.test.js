import { expect, test } from 'vitest'

const calculateTotal = (items) => {
  return items.reduce((acc, item) => acc + (item.price * item.quantity), 0)
}

// Test 1: Cálculo normal
test('Calcular total del carrito correctamente', () => {
  const items = [
    { price: 10, quantity: 2 },
    { price: 5, quantity: 1 }
  ]
  expect(calculateTotal(items)).toBe(25)
})

// Test 2: Carrito vacío
test('El total de un carrito vacío debe ser 0', () => {
  expect(calculateTotal([])).toBe(0)
})

// Test 3: Un solo producto
test('El total con un solo producto debe ser igual a su precio', () => {
  const items = [{ price: 100, quantity: 1 }]
  expect(calculateTotal(items)).toBe(100)
})