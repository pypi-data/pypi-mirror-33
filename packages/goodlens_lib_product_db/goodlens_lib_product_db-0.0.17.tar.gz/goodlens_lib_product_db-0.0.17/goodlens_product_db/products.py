from datetime import datetime
from bson.objectid import ObjectId
from goodlens_product_db.database import DataBase

class Products(DataBase):
  def __init__(self):
    super().__init__()
    self.products = self.db.products

  def add_product_common(self, product_common):
    res = {'product_id': None,
           'message': None}
    try:
      if product_common.gtin is None:
        gtin = str(datetime.now())
      else:
        gtin = product_common.gtin
      query = {"gtin": gtin,
               "seller_code": product_common.seller_code}

      r = self.products.update_one(query,
                                  {"$set": product_common.to_dict()},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      res['product_id'] = str(r.raw_result['upserted'])
      res['message'] = "created"
    else:
      r = self.products.find_one(query)
      res['product_id'] = str(r['_id'])
      res['message'] = "existing"

    return res

  def update_product_common(self, product_id, product_common):
    try:
      data = product_common.to_dict()
      new_data = {}
      for key in data:
        if data[key] is not None:
          new_data[key] = data[key]
      query = {"_id": ObjectId(product_id)}
      r = self.products.update_one(query,
                                   {"$set": new_data},
                                   upsert=False)
    except Exception as e:
      print(e)
      return None

    return r.raw_result
