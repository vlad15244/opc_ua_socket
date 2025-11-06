from opcua import Client, ua
import json

class VariablePLC:

    def __init__(self, name, opc_adr, plc : Client):
        self.name = name
        self.opc_adr = opc_adr
        self.plc = plc

    @property
    def value(self):
        return self.plc.get_node(self.opc_adr).get_value()
    
    @value.setter
    def value(self, new):
        node = self.plc.get_node(self.plc.get_node(self.opc_adr))
        variant_type = node.get_data_type_as_variant_type()
        # Приводим значение к типу узла
        if variant_type == ua.VariantType.Float:
            new = float(new)
        elif variant_type == ua.VariantType.Double:
            new = float(new)
        elif variant_type in (ua.VariantType.Int16, ua.VariantType.Int32, ua.VariantType.UInt32):
            new = int(new)
        elif variant_type == ua.VariantType.String:
            new = str(new)
        elif variant_type == ua.VariantType.Boolean:
            new = bool(new)
        else:
            raise ValueError(f"Неподдерживаемый тип: {variant_type}")
        # Записываем с явным указанием типа
        node.set_value(ua.Variant(new, variant_type)) 

    def __str__(self):
        return f'{str(self.value)}'
    



#"ns=4; s=|var|PLC210 OPC-UA.Application.GVL_Termodat.TERMODAT[1].PV"
ADR = "ns=4; s=|var|PLC210 OPC-UA.Application"

OPC_TERMODAT = {
    "PV1" : "GVL_Termodat.TERMODAT[1].PV",
    "PV2" : "GVL_Termodat.TERMODAT[2].PV",
    "PV3" : "GVL_Termodat.TERMODAT[3].PV", 
    "PV4" : "GVL_Termodat.TERMODAT[4].PV", 
    "SP1" : "GVL_Termodat.TERMODAT[1].SP",
    "SP2" : "GVL_Termodat.TERMODAT[2].SP",
    "SP3" : "GVL_Termodat.TERMODAT[3].SP", 
    "SP4" : "GVL_Termodat.TERMODAT[4].SP"            
}

class PLC:

    __client : Client = None
    __Variable_List = []

    def __init__(self, endpoint, port):
        self.endpoint = endpoint
        self.port = port

    def run(self):
        print(f"opc.tcp://{self.endpoint}:{self.port}")
        self.__client = Client(f"opc.tcp://{self.endpoint}:{self.port}")

        try:
            self.__client.connect() 

            for key, value in OPC_TERMODAT.items():
                self.__Variable_List.append(VariablePLC(key, f'{ADR}.{value}',self.__client))

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    @property
    def vars(self):
        return self.__Variable_List

    def list_json(self):

        keys = []
        values = []
        my_dict = {}
        for var in self.__Variable_List:
            keys.append(var.name)
            values.append(str(var.value))
        
        my_dict = dict(zip(keys, values))

        result = json.dumps(my_dict)
        return result
    

    def write(self, key, new):
        for var in self.__Variable_List:
            if key in var.name:
                var.value = new

    
if __name__ == '__main__':
    plc_1 = PLC('192.168.20.50', '4840')
    plc_1.run()
    plc_1.write('SP', int(100))



            
