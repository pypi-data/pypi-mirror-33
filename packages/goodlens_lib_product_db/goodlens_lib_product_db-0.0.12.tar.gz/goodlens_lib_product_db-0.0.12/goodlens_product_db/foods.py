from bson.objectid import ObjectId
from goodlens_product_db.database import DataBase

class Foods(DataBase):
  def __init__(self):
    super().__init__()
    self.products = self.db.products
    self.foods = self.db.foods

  def add_product_food(self, product_food):
    food_id = None
    try:
      query = {"parent_product_id": product_food.parent_product_id}
      r = self.foods.update_one(query,
                                  {"$set": product_food.to_dict()},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      food_id = str(r.raw_result['upserted'])

    return food_id

  def update_product_food(self, food_id, product_food):
    try:
      query = {"_id": ObjectId(food_id)}
      r = self.foods.update_one(query,
                                   {"$set": product_food.to_dict()},
                                   upsert=False)
    except Exception as e:
      print(e)
      return None

    return r.raw_result
