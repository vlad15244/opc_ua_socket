import asyncio
import websockets
import json
import datetime
import opc_config 

plc_1 = opc_config.PLC('192.168.20.50', '4840')
plc_1.run()

"""def add(node):
        try:
            cur = float(node.get_value())      
            cur = cur + 5
            cur = float(cur)
            variant_type = node.get_data_type_as_variant_type()
            node.set_value(ua.Variant(cur, variant_type))
            print(cur)
        except Exception as e:
            print(f"Ошибка: {e}") 


def toogle(node):
        try:
            cur = int(node.get_value()) 
            if cur == 0:
                new_value = 1
            elif cur == 1:
                new_value = 0            
            variant_type = node.get_data_type_as_variant_type()
            node.set_value(ua.Variant(new_value, variant_type))

        except Exception as e:
            print(f"Ошибка: {e}")"""


def set_point(opc : opc_config.PLC, value):
    """Записывает по нажатию кнопки уствки"""
    for var in plc_1.vars:
        if 'SP' in var.name:
            var.value = value

async def handler(websocket):  # ВАЖНО: два аргумента!
    #print(f"Клиент подключился. Путь: {path}")

    async def read_plc():
        while True:
            try:

                while True:
                    data = await asyncio.to_thread(plc_1.list_json)
                    await websocket.send(data)
                    await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Ошибка1: {e}")

    async def write_plc():
        while True:
            message = await websocket.recv()
            cmd = json.loads(message)  

            if cmd.get("action") == "set_point":
                print("fdgdfgh")
                set_point(plc_1, 250)

    await asyncio.gather(read_plc(), write_plc())

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Сервер запущен: ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())