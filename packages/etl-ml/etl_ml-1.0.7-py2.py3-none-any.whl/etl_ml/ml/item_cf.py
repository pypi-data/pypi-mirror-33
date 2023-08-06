import  pandas as pd
#import math

class Item_CF:
  def __init__(self):
    self.data_path='/Users/geo/Documents/etl_ml/etl_ml/data/uid_score_bid.dat'
    self.raw_data=pd.read_csv(self.data_path,sep=',',header=0,encoding='utf=8')
    print(self.raw_data.head(3))
    self.user_Yitems_scoreY_dict=dict()
    self.item_Yitems_numsY_dict=dict()
    self.item_Yitems_similarityY_dict=dict()
    self.item_Yitems_scoreY_dict=dict()
    self.N=dict()


  # def compute_similarity(self,AB_same_view_count,itemAcount,itemBcount):
  #   similar=AB_same_view_count/math.sqrt(itemAcount*itemBcount)
  #   return similar

  def append_row_to_dict(self,row):

    user=str(row['uid'])
    score=str(row['score'])
    item=str(row['bid'])
    self.user_Yitems_scoreY_dict.setdefault(user,{})
    self.user_Yitems_scoreY_dict[user][item]=int(float(score))
  # {itemA:{item1:num1,item2:num2,item3:num3},itemB:{item1:num1,item2:num2}...}
  #{ user1:{item1:score1,item2:score2,item3:score3},user2:{item4:score4,item5:score5}..}
  #{
  def load_data_to_user_Yitems_scoreY_dict(self):
    self.raw_data.apply(lambda  row:self.append_row_to_dict(row),axis=1)
    for k,v in self.user_Yitems_scoreY_dict.items():
      print(k)
      for item,score in v.items():
        print("item: %s,score: %s"%(item,score))

    # N
  def user_Yitems_scoreY_dict_compute_item_Yitems_numsY_dict(self):
    for user,it_sc in self.user_Yitems_scoreY_dict.items:
      for item  in it_sc.keys():
        self.N[item]+=1
        for item in it_sc.keys():
         self.item_Yitems_numsY_dict.setdefault(item,{})
       # self.item_Yitems_numsY_dict[item][]
  def  load_data_to_df(self):
    print("log")

  def  compute_similarity(self):
    print("log")

  def  recommend(self):
    print("")


if __name__ == '__main__':
    ic=Item_CF()
    ic.load_data_to_user_Yitems_scoreY_dict()