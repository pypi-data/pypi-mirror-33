from bson.objectid import ObjectId
from goodlens_lib_product_db.database import DataBase

class Products(DataBase):
  def __init__(self):
    super().__init__()
    self.products = self.db.products

  def add_product_common(self, product):
    try:
      query = {"host_code": product['host_code'],
               "product_no": product['product_no'],
               "version_id": product['version_id']}
      r = self.products.update_one(query,
                                 {"$set":product},
                                 upsert=True)
    except Exception as e:
      print(e)

    return r.raw_result

