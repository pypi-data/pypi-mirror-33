from bson.objectid import ObjectId
from goodlens_product_db.database import DataBase

class Products(DataBase):
  def __init__(self):
    super().__init__()
    self.products = self.db.products

  def add_product_common(self, product_common):
    product_id = None
    try:
      query = {"gtin": product_common.gtin}
      r = self.products.update_one(query,
                                  {"$set": product_common.to_dict()},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      product_id = str(r.raw_result['upserted'])

    return product_id
