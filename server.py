import asyncio
import websockets
import json
import datetime
import opc_config 
import os

plc_1 = opc_config.PLC('192.168.20.50', '4840')
var_list = opc_config.VariableList()

file_path = os.path.join(os.path.dirname(__file__), "config.json")

with open(file_path, "r", encoding='utf-8') as f:
    data = json.load(f)

for dt in data:
    var_list.add(opc_config.VariablePLC(dt["name"], f'{opc_config.ADR}.{dt["opc_adr"]}',plc_1,dt["scale"], dt["ID"]))  

"""Переменным"""
for var in var_list:
    if "PV" in var.name:
        var.archive(True)

OPC_DATA_QUEUE = asyncio.Queue(maxsize=10)

plc_1.run()

async def buffer():
    buffer = []
    while True:
        data = await OPC_DATA_QUEUE.get()
        # Добавляем в локальный буфер
        buffer.append(data)
        print(buffer)
        # Ограничиваем размер буфера
        if len(buffer) > 50:
            buffer.pop(0)  # удаляем старый элемент
        OPC_DATA_QUEUE.task_done()  # отмечаем обработку

def toogle():
    try:

        var = var_list.get_variable_by_Name('xRegul')
        cur = var.value
        new_value = not cur
        var.value = new_value
    except Exception as e:
        print(f"Ошибка: {e}")

def write(value, name):
    try:
        var = var_list.get_variable_by_Name(name)
        var.value = value

    except Exception as e:
        print(f"Ошибка: {e}")


async def handler(websocket):  # ВАЖНО: два аргумента!
    #print(f"Клиент подключился. Путь: {path}")

    async def read_plc():
        while True:
            try:
                while True:
                    data = await asyncio.to_thread(var_list.list_json_with_Unit)
                    """await OPC_DATA_QUEUE.put({
                        "timestamp": asyncio.get_event_loop().time(),
                        "value": var_list.value_by_name("PV1")
                    })"""
                    await websocket.send(data)
                    await asyncio.sleep(0.05)
            except Exception as e:
                print(f"Ошибка1: {e}")

    async def write_plc():
        while True:
            message = await websocket.recv()
            cmd = json.loads(message)  

            if cmd.get("action") == "regulswitch":
                toogle()
            elif cmd.get("action") == "setpoint":
                set_point = int(cmd.get("value"))
                write(set_point, "SP_Regule")
                
    await asyncio.gather(read_plc(), write_plc())

async def main():

    async with websockets.serve(handler, "localhost", 8765):
        print("Сервер запущен: ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())