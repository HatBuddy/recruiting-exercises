import copy
import argparse
import yaml

class Warehouse(object):
	def __init__(self,name,inventory={}):
		self.name = name
		self.inventory = inventory

	def remove_product(self,product_name, quantity):
		self.inventory[product_name] = max(self.inventory[product_name] - quantity, 0)
		if self.inventory[product_name] == 0:
			self.clear_product(product_name)

	def clear_product(self,product_name):
		del self.inventory[product_name]

class Order(object):
	def __init__(self, products_required={}):
		self.products_required = products_required

	def update(self, product_name, shipped_from_warehouse_count):
		self.products_required[product_name] -= shipped_from_warehouse_count

class WarehouseShipment(object):
	def __init__(self, shipment={}):
		self.shipment = shipment

	def update(self, warehouse, product_name, shipped_from_warehouse_count):
		if	self.shipment.get(warehouse.name,None) ==None:
			self.shipment[warehouse.name] = {product_name: shipped_from_warehouse_count}
		else:
			self.shipment[warehouse.name][product_name] = shipped_from_warehouse_count

class Shipment(object):
	def __init__(self, shipments=[]):
		self.shipments = []
	def add(self,shipment):
		self.shipments.append(shipment)

	def parse_shipment(self):
		return [warehouse_shipment.shipment for warehouse_shipment in self.shipments if warehouse_shipment]

class InventoryAllocator(object):

	def is_order_unfulfilled(self, orders_internal):
		return any(value !=0 for value in orders_internal.products_required.values())

	def create_warehouse_list(self, warehouse_list):
		parsed_warehouse_list = []
		for warehouse in warehouse_list:
				parsed_warehouse_list.append(Warehouse(warehouse['name'],warehouse['inventory']))
		return parsed_warehouse_list

	def compute_shipment(self, order: dict ={}, warehouse_list: list = []):
		orders_internal = Order(copy.deepcopy(order))
		shipment = Shipment()
		warehouses = self.create_warehouse_list(warehouse_list)
		#Go through warehouses in order
		for warehouse in warehouses:
			warehouse_shipment = WarehouseShipment({})
			#Check if product_name is at this warehouse
			for product_name in orders_internal.products_required:
				if product_name in warehouse.inventory:
					shipped_from_warehouse_count = min(orders_internal.products_required[product_name], warehouse.inventory[product_name])
					if shipped_from_warehouse_count >0:
						warehouse.remove_product(product_name, shipped_from_warehouse_count)
						warehouse_shipment.update(warehouse, product_name, shipped_from_warehouse_count)
						orders_internal.update(product_name, shipped_from_warehouse_count)
			if warehouse_shipment.shipment:  
				shipment.add(warehouse_shipment)
		if self.is_order_unfulfilled(orders_internal):
			return []
		else:
			return shipment.parse_shipment()



if __name__ == '__main__':
	

	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument('-o', '--order', type=yaml.load, required=True, help="order string is in dictionary format, i.e. \"{ \"apple\": 1 , \"orange\": 5}\"")
	parser.add_argument('-i', '--inventory', type=yaml.load, required=True, help="inventory string is a list of dictionarys, i.e. \
							\"[{\"name\": \"owd\", \"inventory\": { \"apple\": 5} }, { \"name\": \"dm\", \"inventory\": { \"orange\": 5 }}]\" \
							")
	try:
		args = parser.parse_args()
		s=InventoryAllocator()
		print(s.compute_shipment(args.order, args.inventory))
	except yaml.YAMLError as exc:
		print(exc , '\n') 
		print("ParserError")



	# input1 = { "apple": 1 , "orange": 5}
	# input2 = [{ "name": "owd", "inventory": { "apple": 5} }, { "name": "dm", "inventory": { "orange": 5 }}]
	# import pdb;pdb.set_trace()
	# s=InventoryAllocator()
	# print(s.compute_shipment(input1,input2))
	# print(s.compute_shipment(args.order, args.inventory))



