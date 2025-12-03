from opcua import Client, ua
import json
import os

"""добавить еще что-то хотел"""

class VariablePLC:

    def __init__(self, name, opc_adr, plc : Client, scale : str, ID):
        self.name = name
        self.ID = ID
        self.opc_adr = opc_adr
        self.plc = plc


        self.scale = SCALE_LIST[scale]



    def archive(self, is_archive : bool):
        self._is_archive = is_archive
        
    @property
    def value(self):
        return self.plc.client.get_node(self.opc_adr).get_value()
    
    def __str__(self):
        try:
            return str(self.plc.client.get_node(self.opc_adr).get_value())
        except Exception as e:
            return ""
        
    def __int__(self):
        try:
            return int(self.plc.client.get_node(self.opc_adr).get_value())
        except Exception as e:
            return 0 
        
    def str_unit(self):
        try:
            return str(f"{self.plc.client.get_node(self.opc_adr).get_value()} {self.scale.unit}")
        except Exception as e:
            return ""        
        
    @value.setter
    def value(self, new):
        node = self.plc.client.get_node(self.plc.client.get_node(self.opc_adr))
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

class Scale:
    def __init__(self, value_min = 0, value_max = 100, unit = '%', is_Check = False):
        self.value_min = value_min
        self.value_max = value_max
        self.unit = unit
        self.is_Check = is_Check


""" Шкала """
Hardering = Scale(0,800,"°C", False)
Power = Scale(0,100,"%", False)
TwoState = Scale(0,1,"", False)
Default = Scale(0,100,"", False)

SCALE_LIST = {
    "Hardering": Hardering,
    "Power": Power,
    "TwoState": TwoState,
    "Default": Default
}

class VariableList:
    vars = []

    def __init__(self):
        pass

    def add(self, VariablePLC):
        self.vars.append(VariablePLC)

    def __iter__(self):
        return iter(self.vars)

    def __str__(self):
        keys = []
        values = []
        my_dict = {}
        for var in self.vars:
            keys.append(var.name)
            values.append(str(var.value))
        
        my_dict = dict(zip(keys, values))
        return my_dict  
    
    def list_json_with_Unit(self):

        keys = []
        values = []
        my_dict = {}
        for var in self.vars:
            keys.append(var.name)
            values.append(f"{var.str_unit()}")

        my_dict = dict(zip(keys, values))

        result = json.dumps(my_dict)
        return result

    def list_json_without_Unit(self):

        keys = []
        values = []
        my_dict = {}
        for var in self.vars:
            keys.append(var.name)
            values.append(f"{var.value}")

        my_dict = dict(zip(keys, values))

        result = json.dumps(my_dict)
        return result 

    def get_variable_by_ID(self, ID : int) -> VariablePLC:
        for var in self.vars:
            if var.ID == ID:
                return var
            
    def get_variable_by_Name(self, Name : str) -> VariablePLC:
        for var in self.vars:
            if var.name == Name:
                return var   
            
class PLC:

    __client : Client = None
    __Variable_List = []
    __Is_Connected = False
    
    def __init__(self, endpoint, port, ):
        self.endpoint = endpoint
        self.port = port

    def run(self):
        print(f"opc.tcp://{self.endpoint}:{self.port}")
        self.__client = Client(f"opc.tcp://{self.endpoint}:{self.port}")

        try:
            self.__client.connect() 
            self.__Is_Connected = True

            """for key, value in OPC_TERMODAT.items():
                self.__Variable_List.append(VariablePLC(key, f'{ADR}.{value}',self.__client))"""

        except Exception as e:
            self.__Is_Connected = False
            print(f"Произошла ошибка: {e}")

    @property
    def client(self):
        return self.__client
            

    @property
    def vars(self):
        return self.__Variable_List
    
    @property
    def Is_Connected(self):
        return self.__Is_Connected


    def write(self, key, new):
        for var in self.__Variable_List:
            if key in var.name:
                var.value = new

    
if __name__ == '__main__':

    plc_1 = PLC('192.168.20.50', '4840')    
    var_list = VariableList()

    file_path = os.path.join(os.path.dirname(__file__), "config.json")

    with open(file_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    for dt in data:
        var_list.add(VariablePLC(dt["name"], f'{ADR}.{dt["opc_adr"]}',plc_1, Default, dt["ID"]))       

    plc_1.run()
