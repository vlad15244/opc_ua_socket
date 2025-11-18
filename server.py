import asyncio
import websockets
import json
import datetime
import opc_config 

plc_1 = opc_config.PLC('192.168.20.50', '4840')
var_list = opc_config.VariableList()

for key, value in opc_config.OPC_TERMODAT.items():
    if "PV" in key:
        scale = opc_config.Hardering
    elif "SP" in key:
        scale = opc_config.Hardering 
    elif "MV" in key:
        scale = opc_config.Power 
    else:
        scale = opc_config.Default                    

    var_list.add(opc_config.VariablePLC(key, f'{opc_config.ADR}.{value}',plc_1, scale))

"""Переменным"""
for var in var_list:
    if "PV" in var.name:
        var.archive(True)

OPC_DATA_QUEUE = asyncio.Queue(maxsize=10)

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

"""
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
        for var in var_list:
            if 'xRegul' == var.name:
                cur = var.value
                new_value = not cur
                var.value = new_value
    except Exception as e:
        print(f"Ошибка: {e}")

def write(value, name):
    try:
        for var in var_list:
            if name == var.name:
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
                    await OPC_DATA_QUEUE.put({
                        "timestamp": asyncio.get_event_loop().time(),
                        "value": var_list.value_by_name("PV1")
                    })
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
    
    save_task = asyncio.create_task(buffer())
    async with websockets.serve(handler, "localhost", 8765):
        print("Сервер запущен: ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())