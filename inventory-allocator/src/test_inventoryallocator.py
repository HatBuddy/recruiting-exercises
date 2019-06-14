import unittest

from inventoryallocator import *


class Test(unittest.TestCase):

	def test_empty_order_return_empty_shipment(self):
		order = { }
		warehouse_list=[{ "name": "owd", "inventory": { "apple": 5} }, { "name": "dm", "inventory": { "orange": 5 }}]

		expected = []
		self.assertEqual(InventoryAllocator().compute_shipment(order,warehouse_list),expected)

	def test_unfulfillable_order_return_empty_shipment(self):
		order = { "apple": 40 , "orange": 5}
		warehouse_list=[{ "name": "owd", "inventory": { "apple": 5, "orange": 30} }, { "name": "dm", "inventory": { "orange": 5 }}]

		expected = []
		self.assertEqual(InventoryAllocator().compute_shipment(order,warehouse_list),expected)

	def test_fulfillable_order_one_warehouse(self):
		order = { "apple": 1 , "orange": 5}
		warehouse_list=[{ "name": "owd", "inventory": { "apple": 5, "orange": 30} }, { "name": "dm", "inventory": { "orange": 5 }}]

		expected = [{'owd': {'apple': 1, 'orange': 5}}]
		self.assertEqual(InventoryAllocator().compute_shipment(order,warehouse_list),expected)

	def test_fulfillable_order_many_warehouses(self):
		order = { "apple": 1 , "orange": 32}
		warehouse_list=[{ "name": "owd", "inventory": { "apple": 5, "orange": 30} }, { "name": "dm", "inventory": { "orange": 5 }}]

		expected = [{'owd': {'apple': 1, 'orange': 30}}, {'dm': {'orange': 2}}]
		self.assertEqual(InventoryAllocator().compute_shipment(order,warehouse_list),expected)

	def test_fulfillable_order_skip_first_warehouses(self):
		order = { "apple": 1 , "orange": 1}
		warehouse_list=[{ "name": "owd", "inventory": { "triangles": 5, "squares": 30} }, { "name": "dm", "inventory": { "orange": 47 , "apple":12 }}]

		expected = [{'dm': {'apple': 1, 'orange': 1}}]
		self.assertEqual(InventoryAllocator().compute_shipment(order,warehouse_list),expected)

	def test_warehouse_delete(self):
		w = Warehouse("wh1", {"apple":1, "orange":2})
		w.clear_product("orange")

		with self.assertRaises(KeyError):  w.inventory["orange"]

	def test_warehouse_remove_product_some_remaining(self):
		w = Warehouse("wh1", {"apple":1, "orange":2})
		w.remove_product("orange", 1)
		
		expected = 1
		self.assertEqual(w.inventory["orange"], expected)

	def test_warehouse_remove_product_none_remaining(self):
		w = Warehouse("wh1", {"apple":1, "orange":2})
		w.remove_product("orange", 2)
		
		with self.assertRaises(KeyError):  w.inventory["orange"]

	def test_order_update(self):
		o = Order({ "apple": 1 , "orange": 5})
		o.update("apple", 1)

		expected = 0
		self.assertEqual(o.products_required["apple"], expected)

	def test_warehouse_shipment_update(self):
		w1 = Warehouse("wh1", {"apple":1, "orange":2})
		w2 = Warehouse("wh2", {"apple": 2, "orange": 3})
		ws = WarehouseShipment({})

		ws.update(w1, "apple",1)
		ws.update(w1, "orange",2)
		ws.update(w2, "orange",1)

		expected = {'wh1': {'apple': 1, 'orange': 2}, 'wh2': {'orange': 1}}
		self.assertEqual(ws.shipment, expected)

	def test_shipment_add(self):
		s = Shipment([])
		w = Warehouse("wh1", {"apple":1, "orange":2})

		s.add(w)
		expected = [w]
		self.assertEqual(s.shipments, expected)

	def test_parse_shipment(self):
		s = Shipment([])
		w1 = Warehouse("wh1", {"apple":1, "orange":2})
		w2 = Warehouse("wh2", {"apple": 2, "orange": 3})
		ws = WarehouseShipment({})

		ws.update(w1, "apple",1)
		ws.update(w2, "orange",1)
		s.add(ws)

		expected =[{'wh1': {'apple': 1}, 'wh2': {'orange': 1}}]
		self.assertEqual(s.parse_shipment(), expected)

	def test_inventory_allocater_is_order_unfulfilled(self):
		i = InventoryAllocator()

		o = Order({ "apple": 1 , "orange": 5})
		self.assertTrue(i.is_order_unfulfilled(o))

		o = Order({ "apple": 0 , "orange": 0})
		self.assertFalse(i.is_order_unfulfilled(o))


if __name__ == '__main__':
    unittest.main()