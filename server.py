import asyncio
import websockets
from opcua import Client, ua
import json
import datetime



client = Client("opc.tcp://192.168.20.50:4840")
client.connect()

async def handler(websocket):  # ВАЖНО: два аргумента!
    #print(f"Клиент подключился. Путь: {path}")

    async def read_plc():
        while True:
            try:

                node = client.get_node("ns=4; s=|var|PLC210 OPC-UA.Application.GVL_Termodat.TERMODAT[1].PV")
                node1 = client.get_node("ns=4; s=|var|PLC210 OPC-UA.Application.GVL_Termodat.TERMODAT[2].PV")
                node3 = client.get_node("ns=4; s=|var|PLC210 OPC-UA.Application.GVL_Termodat.TERMODAT[1].SP")

                while True:
                    value = await asyncio.to_thread(node.get_value)
                    value1 = await asyncio.to_thread(node1.get_value)
                    value3 = await asyncio.to_thread(node3.get_value)
                    await websocket.send(json.dumps({
                            'value1': value,
                            'value2': value1,  
                            'value3': value3

                        }))
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Ошибка: {e}")

    async def write_plc():
        while True:
            message = await websocket.recv()
            cmd = json.loads(message)  

            if cmd.get("action") == "write":
                value = cmd["value"]
                node_write = client.get_node("ns=4; s=|var|PLC210 OPC-UA.Application.GVL_Termodat.TERMODAT[1].SP")
                # Запись в ПЛК
                node = client.get_node(node_write)
                variant_type = node.get_data_type_as_variant_type()
                # Приводим значение к типу узла
                if variant_type == ua.VariantType.Float:
                    value = float(value)
                elif variant_type == ua.VariantType.Double:
                    value = float(value)
                elif variant_type in (ua.VariantType.Int16, ua.VariantType.Int32, ua.VariantType.UInt32):
                    value = int(value)
                elif variant_type == ua.VariantType.String:
                    value = str(value)
                elif variant_type == ua.VariantType.Boolean:
                    value = bool(value)
                else:
                    raise ValueError(f"Неподдерживаемый тип: {variant_type}")
                # Записываем с явным указанием типа
                node.set_value(ua.Variant(value, variant_type))            
  

    await asyncio.gather(read_plc(), write_plc())

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Сервер запущен: ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())