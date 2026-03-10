import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import { v4 as uuid } from 'uuid';

const prisma = new PrismaClient();

async function main() {
  const now = new Date().toISOString();

  // Hash password for john@example.com (@Test123)
  const hashedPassword = await bcrypt.hash('@Test123', await bcrypt.genSalt());
  const userId = 'fabd918b-13e8-4c2b-b92e-70bc59e90aa3'; // fixed id so agent's fallback token stays valid if needed

  // Permissions required for GET /v1/products (product:list::all and product:list::available)
  const defaultPermissions = ['product:list::all', 'product:list::available'];

  const user = await prisma.user.upsert({
    where: { email: 'john@example.com' },
    update: { permissions: defaultPermissions },
    create: {
      id: userId,
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@example.com',
      password: hashedPassword,
      phone: '+573001234567',
      emailIsVerified: true,
      permissions: defaultPermissions,
      created_at: now,
      updated_at: now,
    },
  });

  console.log('Seeded user:', user.email);

  // Clear existing products and seed Biela menu
  const deleted = await prisma.product.deleteMany({});
  console.log('Deleted', deleted.count, 'existing products');

  const products = [
    // BURGERS
    {
      name: 'Barracuda',
      category: 'Burgers',
      price: 28000,
      description:
        'Pan artesanal, 150 gramos de carne, tocineta, queso mozzarella, queso cheddar, cebolla caramelizada, mayonesa de cilantro, salsa BBQ, mostaza dulce y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Biela',
      category: 'Burgers',
      price: 28000,
      description:
        'Pan artesanal, 150 gramos de carne, jamón, queso mozzarella, tomate, lechuga, mayonesa de cilantro, salsa de ajo, salsa BBQ y papas fritas. Adicionales: uvilla caramelizada, pico de gallo, ceviche de cebolla, piña caramelizada, ripio triturado, jalapeños.',
      available: true,
      images: [],
    },
    {
      name: 'Beta',
      category: 'Burgers',
      price: 28000,
      description:
        'Pan artesanal, 150 gramos de carne, tocineta, queso mozzarella, queso cheddar, queso parmesano, queso crema, pepinillos caramelizados, mayonesa de cilantro, salsa BBQ y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Arrabbiata',
      category: 'Burgers',
      price: 27000,
      description:
        'Pan artesanal, 150 gramos de carne, tocineta, queso cheddar, crema griega, cebolla caramelizada en reducción de guayaba, mayonesa de cilantro, salsa BBQ y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Americana',
      category: 'Burgers',
      price: 22000,
      description:
        'Pan artesanal, 150 gramos de carne, queso cheddar, tomate, lechuga, pepinillos caramelizados, mayonesa de cilantro, salsa BBQ, mostaza artesanal y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Bimota',
      category: 'Burgers',
      price: 27000,
      description:
        'Pan artesanal, 150 gramos de carne, tocineta, queso crema, chimichurri, aros de cebolla morados, tomate, mayonesa de cilantro, salsa chipotle, reducción de maracuyá y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Montesa',
      category: 'Burgers',
      price: 30000,
      description:
        'Pan artesanal, 150 gramos de carne, tocineta, cebolla caramelizada, queso azul, tomate asado, aros de cebolla apanados, salsa chipotle, salsa BBQ y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Manhattan',
      category: 'Burgers',
      price: 28000,
      description:
        'Pan artesanal, 150 gramos de carne, tocineta, queso mozzarella, pepinillos caramelizados, cebolla crispy, salsa tártara, mostaza americana, salsa chipotle y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'La Vuelta',
      category: 'Burgers',
      price: 29000,
      description:
        'Pan artesanal, 150 gramos de carne, tocineta crispy de cebolla, caramelizado de chilacuan, queso quajada, salsa tártara, salsa chipotle, mostaza americana y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Honey Burger',
      category: 'Burgers',
      price: 28000,
      description:
        'Pan artesanal, 150 gramos de carne, tocineta, queso cheddar, cebolla caramelizada, cebolla crispy, salsa BBQ, salsa chipotle y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Montana',
      category: 'Burgers',
      price: 28000,
      description:
        'Pan artesanal, 150 gramos de carne, queso mozzarella, mermelada de tomate cherry, albahaca, salsa tatemada con concho de frito, salsa tártara, cebolla crispy y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Al Pastor',
      category: 'Burgers',
      price: 27000,
      description:
        'Pan artesanal, 150 gramos de carne, queso mozzarella, carne de cerdo al pastor acompañado con piña asada, cebolla crispy, salsa chipotle, crema agria, mayonesa de cilantro y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Mexican Burger',
      category: 'Burgers',
      price: 27000,
      description:
        'Pan artesanal, 150 gramos de carne, queso mozzarella, tocineta, pico de gallo, jalapeño, crema agria, salsa de tamarindo y papas fritas.',
      available: true,
      images: [],
    },
    // HOT DOGS
    {
      name: 'Pegoretti',
      category: 'Hot Dogs',
      price: 27000,
      description:
        'Pan artesanal, salchicha americana, queso mozzarella, trozos de pollo apanado, tomate cherry caramelizado, cebolla crispy, salsa tártara, salsa BBQ, mostaza y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Denver',
      category: 'Hot Dogs',
      price: 27000,
      description:
        'Pan artesanal, salchicha americana, queso mozzarella, queso cheddar, tocineta, cebolla caramelizada, mayonesa de cilantro, cebolla crispy y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Special Dog',
      category: 'Hot Dogs',
      price: 27000,
      description:
        'Pan artesanal, salchicha americana, trozos de costilla en salsa maracuyá, papas trituradas, crema griega, salsa chipotle, mayonesa de cilantro y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Nairobi',
      category: 'Hot Dogs',
      price: 27000,
      description:
        'Pan artesanal, salchicha americana, queso mozzarella, costilla en salsa BBQ, mayonesa de cilantro, cebolla morada encurtida, ripio triturado y papas fritas.',
      available: true,
      images: [],
    },
    // FRIES
    {
      name: 'Special Fries',
      category: 'Fries',
      price: 30000,
      description:
        'Papas fritas, salchicha americana, chorizo artesanal, plátano maduro, albahaca, queso parmesano y pico de gallo.',
      available: true,
      images: [],
    },
    {
      name: 'Salchipapa',
      category: 'Fries',
      price: 18000,
      description: 'Papas fritas y salchicha americana, acompañadas de tu salsa favorita.',
      available: true,
      images: [],
    },
    {
      name: 'Biela Fries',
      category: 'Fries',
      price: 28000,
      description:
        'Papas fritas con queso crema, queso parmesano, salchicha americana, tocineta caramelizada, mayonesa de cilantro, mermelada de tomate cherry y albahaca.',
      available: true,
      images: [],
    },
    {
      name: 'Cheese Fries',
      category: 'Fries',
      price: 27000,
      description:
        'Papas fritas con queso cheddar, tocineta caramelizada y queso parmesano.',
      available: true,
      images: [],
    },
    // CHICKEN BURGERS
    {
      name: 'Booster',
      category: 'Chicken Burgers',
      price: 28000,
      description:
        'Pan artesanal, filete de pollo apanado, cebolla caramelizada, tomate, lechuga, salsa tártara, salsa BBQ, mostaza y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Vittoria',
      category: 'Chicken Burgers',
      price: 28000,
      description:
        'Pan artesanal, filete de pollo apanado, albahaca, mermelada de tomate cherry, cebolla crispy, salsa tártara, mostaza y papas fritas.',
      available: true,
      images: [],
    },
    {
      name: 'Arizona',
      category: 'Chicken Burgers',
      price: 28000,
      description:
        'Pan artesanal, filete de pollo apanado, tocineta, pepinillos caramelizados, salsa chipotle, salsa tártara, cebolla crispy y papas fritas.',
      available: true,
      images: [],
    },
    // MENÚ INFANTIL
    {
      name: 'Menú Infantil',
      category: 'Menú Infantil',
      price: 40000,
      description:
        'Mini burger clásica, pops de pollo apanado, papas fritas, pastel de brownie, mermelada de frutos rojos y helado.',
      available: true,
      images: [],
    },
    // STEAK & RIBS
    {
      name: 'Costillas de Cerdo en Salsa BBQ',
      category: 'Steak & Ribs',
      price: 38000,
      description:
        'Costilla de cerdo acompañada de papas fritas, cebolla encurtida y guacamole.',
      available: true,
      images: [],
    },
    {
      name: 'Picada',
      category: 'Steak & Ribs',
      price: 55000,
      description:
        'Papas fritas, carne de cerdo con chimichurri, chorizo artesanal, crispetas de pollo, costillas de cerdo en salsa BBQ, salchicha americana, aborrajado de plátano maduro con queso y bocadillo.',
      available: true,
      images: [],
    },
    // BEBIDAS - Limonadas
    {
      name: 'Limonada de cereza',
      category: 'Bebidas',
      price: 12000,
      description: 'Limonada de cereza.',
      available: true,
      images: [],
    },
    {
      name: 'Limonada de fresa',
      category: 'Bebidas',
      price: 10000,
      description: 'Limonada de fresa.',
      available: true,
      images: [],
    },
    {
      name: 'Limonada de hierba buena',
      category: 'Bebidas',
      price: 9000,
      description: 'Limonada de hierba buena.',
      available: true,
      images: [],
    },
    {
      name: 'Limonada natural',
      category: 'Bebidas',
      price: 6500,
      description: 'Limonada natural.',
      available: true,
      images: [],
    },
    // Hervidos
    {
      name: 'Hervido Maracuyá',
      category: 'Bebidas',
      price: 9500,
      description: 'Hervido de maracuyá.',
      available: true,
      images: [],
    },
    {
      name: 'Hervido Mora',
      category: 'Bebidas',
      price: 9500,
      description: 'Hervido de mora.',
      available: true,
      images: [],
    },
    // Malteadas
    {
      name: 'Malteada Maracuyá y uvilla',
      category: 'Bebidas',
      price: 15000,
      description: 'Malteada de maracuyá y uvilla.',
      available: true,
      images: [],
    },
    {
      name: 'Malteada Brownie',
      category: 'Bebidas',
      price: 15000,
      description: 'Malteada de brownie.',
      available: true,
      images: [],
    },
    {
      name: 'Malteada Frutos rojos',
      category: 'Bebidas',
      price: 15000,
      description: 'Malteada de frutos rojos.',
      available: true,
      images: [],
    },
    // Jugos
    {
      name: 'Jugos en agua',
      category: 'Bebidas',
      price: 7500,
      description: 'Jugos naturales en agua.',
      available: true,
      images: [],
    },
    {
      name: 'Jugos en leche',
      category: 'Bebidas',
      price: 7500,
      description: 'Jugos naturales en leche.',
      available: true,
      images: [],
    },
    // Bebidas
    {
      name: 'Coca-Cola',
      category: 'Bebidas',
      price: 5500,
      description: 'Coca-Cola.',
      available: true,
      images: [],
    },
    {
      name: 'Coca-Cola Zero',
      category: 'Bebidas',
      price: 5500,
      description: 'Coca-Cola Zero.',
      available: true,
      images: [],
    },
    {
      name: 'Soda',
      category: 'Bebidas',
      price: 4500,
      description: 'Soda.',
      available: true,
      images: [],
    },
    {
      name: 'Agua',
      category: 'Bebidas',
      price: 4000,
      description: 'Agua.',
      available: true,
      images: [],
    },
    // Cervezas
    {
      name: 'Club Colombia',
      category: 'Bebidas',
      price: 7500,
      description: 'Cerveza Club Colombia.',
      available: true,
      images: [],
    },
    {
      name: 'Poker',
      category: 'Bebidas',
      price: 7500,
      description: 'Cerveza Poker.',
      available: true,
      images: [],
    },
    {
      name: 'Corona 355ml',
      category: 'Bebidas',
      price: 12000,
      description: 'Corona 355ml.',
      available: true,
      images: [],
    },
    {
      name: 'Corona michelada',
      category: 'Bebidas',
      price: 14500,
      description: 'Corona michelada.',
      available: true,
      images: [],
    },
    {
      name: 'Michelada',
      category: 'Bebidas',
      price: 12000,
      description: 'Michelada.',
      available: true,
      images: [],
    },
    // Sodas saborizadas
    {
      name: 'Soda saborizada Uvilla y maracuyá',
      category: 'Bebidas',
      price: 15000,
      description: 'Soda saborizada de uvilla y maracuyá.',
      available: true,
      images: [],
    },
    {
      name: 'Soda saborizada Frutos rojos',
      category: 'Bebidas',
      price: 15000,
      description: 'Soda saborizada de frutos rojos.',
      available: true,
      images: [],
    },
  ];

  for (const p of products) {
    await prisma.product.create({
      data: {
        id: uuid(),
        name: p.name,
        category: p.category,
        price: p.price,
        description: p.description,
        available: p.available,
        images: p.images,
        created_at: now,
        updated_at: now,
        created_by: user.id,
      },
    });
  }
  console.log('Seeded', products.length, 'Biela menu products');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
