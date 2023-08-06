import json
import  yaml


class  Dag:

  class Cat:
    def __init__(self):
      self.containerP=8080

  def __init__(self):
    self.apiVersion="apps/v1beta1"
    self.kind='Deployment'
    wifi_arr=['geo','tmtl','father']
    self.metadata=wifi_arr
    cat=self.Cat()
    ports_Arr=[cat.__dict__]
    self.ports=ports_Arr

    dic={'app': {
        "containers": [
          {
            "name": "springboot-demo",
            "image": "springboot-demo",
            "imagePullPolicy": "IfNotPresent",
            "ports": [
              {
                "containerPort": 8080
              }
            ]
          }
        ]
      }}
    #print(str(dic))
    self.di=dic
    meta_Dict={'name':'springboot-demo-deployment','labels':dic}
    self.metadata=meta_Dict



  def set_default(obj):
    if isinstance(obj, set):
      return list(obj)
    raise TypeError

  def obj2json(self):


    objdict=vars(self)
    data=json.dumps(objdict)
    ya=yaml.load(data)
    filey='/Users/geo/Documents/etl_ml/etl_ml/data/demo.yaml'
    stream = open(filey, 'w')
    #yaml.safe_dump(ya,stream,default_flow_style=False)


    yaml_file = yaml.load(data)
    json_file='/Users/geo/Documents/etl_ml/etl_ml/data/demo.json'
    #json持久化 1
    # with open(json_file,'w') as fp:
    #   fp.write(json.dumps(yaml_file,indent=1))
    # # json持久化 2
    # with open(json_file, 'w') as fp:
    #   json.dump(yaml_file, fp,indent=1)


    k=yaml.safe_dump(ya,default_flow_style=False)
    #print(k)

    objdict = vars(self)
    data = json.dumps(objdict)
    yaml_file = yaml.load(data)
    fl=json.dumps(yaml_file,indent=1)
    dict=json.loads(fl)
    print(fl)
   # print(dict(json.load(yaml.dump(yaml_file))))
    # js=json.dump(yaml.safe_load(k))
    # print(js)
    # with open(filey, 'wb') as  f:
    #   f.write(str(k))


    # print(type(ya))
    # return  k


if __name__ == '__main__':
    da=Dag()
    filey = '/Users/geo/Documents/etl_ml/etl_ml/data/demo2.yaml'
    stream = open(filey, 'w')

   # yaml.safe_dump(da.__dict__, stream=stream,default_flow_style=False)

    yaml_format=yaml.safe_dump(da.__dict__,default_flow_style=False)

    print( yaml_format)

    # print()
    # yaml.dump(da,stream=filey)
   # yaml.safe_dump(da, stream, default_flow_style=False)
    #print(str(vars(da)))
    #da.obj2json()

    # print(res)

    sdf={"bejing",'tianjin',34}
    for  i in  sdf:
      print(i)