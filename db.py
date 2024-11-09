from prisma import Prisma

prisma = Prisma()

async def connect_db():
      prisma.connect()

async def disconnect_db():
     prisma.disconnect()
