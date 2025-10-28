import asyncio
import websockets
from opcua import Client
import json
import datetime

async def handler(websocket):  # ВАЖНО: два аргумента!
    #print(f"Клиент подключился. Путь: {path}")
    try:
        client = Client("opc.tcp://192.168.20.50:4840")
        await asyncio.to_thread(client.connect)
        node = client.get_node("ns=4; s=|var|PLC210 OPC-UA.Application.GVL_Termodat.TERMODAT[1].PV")
        node1 = client.get_node("ns=4; s=|var|PLC210 OPC-UA.Application.GVL_Termodat.TERMODAT[2].PV")
        while True:
            value = await asyncio.to_thread(node.get_value)
            value1 = await asyncio.to_thread(node1.get_value)

            await websocket.send(json.dumps({
                    'value1': value,
                    'value2': value1,                    
                    'timestamp': datetime.datetime.now().isoformat()
                }))
            await asyncio.sleep(3)
    except Exception as e:
        print(f"Ошибка: {e}")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Сервер запущен: ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())