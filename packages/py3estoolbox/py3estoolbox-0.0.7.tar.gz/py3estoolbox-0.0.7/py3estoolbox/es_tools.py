#!/usr/bin/python3 -W ignore
import os
import requests
import elasticsearch as es
import json
import py3toolbox as tb
import py3mproc   as mp
from elasticsearch import helpers
from elasticsearch_dsl import Search


class ES():
  def __init__(self, es_url):
    self.es_url  = es_url
    self.es_inst = es.Elasticsearch([self.es_url],scheme="https", verify_certs=False)
    self.indices = {}
    self.aliases = {}
    self.scanner = None
    self.batch_data = [] 
    self.get_es_info()
    self.scanner = None
  
  def _format_index_doc_id(self, index, doc_type,doc_id):
    return_str = '{0}|{1}|{2}'.format(index,doc_type,doc_id)
    return  return_str
    
  def _parse_index_doc_id(self, index_doc_id_str):
    m = re.match( r'^([^\|]+)\|([^\|]+)\|([^\|]+)$', index_doc_id_str, re.M|re.I)
    if m : return (m.group(1),m.group(2),m.group(3))
    else : return None   

  def init_scanner(self, index=None, alias=None, dsl_json=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    if dsl_json is None: # assume all records
      dsl_json = {"query": {"match_all": {}}}
    self.scanner = es.helpers.scan(self.es_inst, index=index, query=dsl_json)
    
  def get_es_info(self):
    self.indices  = { index_name: self.es_inst.indices.get('*')[index_name] for index_name in [ x for x in list( self.es_inst.indices.get('*').keys()) if not x.startswith('.') ]}
    self.aliases  = { index_name: self.es_inst.indices.get_alias('*')[index_name] for index_name in [ x for x in list( self.es_inst.indices.get_alias('*').keys()) if not x.startswith('.') ]}
    pass

  def get_index_by_alias(self, alias):
    result = []
    for k,v in self.aliases.items() :
      if alias in v['aliases']:
        result.append(k)
    if len(result) > 0: return  result[0]
    return None

  def set_alias(self, index, alias) :
    if self.es_inst.indices.exists_alias(name=alias):
      self.es_inst.indices.delete_alias(index = "*", name=alias)
    self.es_inst.indices.put_alias(index=index,      name=alias)       
    
  def get_doc_count(self, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    return int(self.es_inst.count(index=index)['count'])

  def get_ids(self, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    self.index_type_ids = []
    self.id_scanner = es.helpers.scan(self.es_inst, index=index, query={"stored_fields": ["_id"], "query": {"match_all": {}}})
    for doc in self.id_scanner :
      self.index_type_ids.append(self._format_index_doc_id(index,  doc['_type'] ,  doc['_id']))
    return (self.index_type_ids)
    
  def get_doc_by_id(self, doc_type, doc_id, index=None, alias=None) :
    if index is None: index = self.get_index_by_alias(alias=alias)
    doc = self.es_inst.search(index=index, doc_type=doc_type, body={"query": {"match": {"_id": doc_id}}})
    if int(doc['hits']['total']) == 0 : return None
    return (doc['hits']['hits'][0]['_source'])

  def bulk_exec(self, batch):
    helpers.bulk(self.es_inst, batch, request_timeout=120)
    
  def create_index(self, index, mapping_json):
    print (type(mapping_json))
    if 'creation_date' in mapping_json['settings']['index'] : mapping_json['settings']['index'].pop('creation_date', None)
    if 'provided_name' in mapping_json['settings']['index'] : mapping_json['settings']['index'].pop('provided_name', None)
    if 'uuid' in mapping_json['settings']['index']          : mapping_json['settings']['index'].pop('uuid', None)
    if 'version' in mapping_json['settings']['index']       : mapping_json['settings']['index'].pop('version', None)  
    
    self.es_inst.indices.create(index=index, body=mapping_json)
    self.get_es_info()
  
  def delete_index(self, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    self.es_inst.indices.delete(index=index, ignore=[400, 404])
    self.get_es_info()

  def delete_index_data(self, index=None, alias=None):
    batch = []
    item_count = 0
    doc_count = self.get_doc_count(index=index)
   
    self.init_scanner(index=index)
    try :
      start_time = time.time()
      for item in self.scanner:
        item_count +=1
        item.pop('_score', None)
        item['_index'] = index
        item_to_delete = {'_op_type' : "delete",  "_index" : item['_index'] , "_type" : item['_type'] , "_id" : item['_id'] } 
        batch.append(item_to_delete) 
        
        if (item_count % config['es_bulk_size']) == 0:  
          self.bulk_exec(batch)
          print (tb.show_progress_bar(current=item_count, total=doc_count, start_time=start_time), sep=' ', end='', flush=True)  
          batch = []
      self.bulk_exec(batch)
    except Exception as e:
      self.util.write_file(config['command_log'], 'Failed: ' + str(e) + + "\n")
    if (doc_count > 0) :
      print (self.util.show_progress_bar(current=item_count, total=doc_count, start_time=start_time), sep=' ', end='', flush=True)  
    
    print ("\n\n")
    return    
    
  def get_analyzer(self,index=None, alias=None):
    mapping_dic = self.get_mapping(json_fmt=False, index=index, alias=alias)
    analyzers    = mapping_dic['settings']['index']['analysis']['analyzer'].keys()
    return analyzers
    
  def get_mapping(self, json_fmt=True, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    mapping_dic = self.indices[index]
    if json_fmt :   mapping = json.dumps(mapping_dic, sort_keys=True, indent=2)
    else        :   mapping = mapping_dic
    return mapping

  def test_analyzer(self, index=None, alias=None, analyzer=None, text=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    url = self.es_url + '/' + alias + '/_analyze'
    headers = {"Accept": "application/json"}
    body_data = '{"analyzer": "' + analyzer + '", "text":    "' + text + '" }'    
    response = requests.get(url,data = body_data)
    return (response.text)

  def query_by_dsl(self, doc_type, dsl_json, return_data=True, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    if return_data == True :
      result = []
      result_page = self.es_inst.search(index=index, doc_type=doc_type, scroll = '5m', size=1000, body=dsl_json)
      scroll_id = result_page['_scroll_id']
      scroll_size = result_page['hits']['total']
      while (scroll_size > 0):
        result.extend(result_page['hits']['hits'])
        result_page = self.es_inst.scroll(scroll_id = scroll_id, scroll = '5m')
        scroll_id = result_page['_scroll_id']
        scroll_size = len(result_page['hits']['hits'])
      return (result)  
    else:
      result_page = self.es_inst.search(index=index, doc_type=doc_type, scroll = '5m', size=0, body=dsl_json) 
      return result_page['hits']['total']
  

  def update_index_refresh (self,  index=None, alias=None, refresh_interval_value='null') :
    if index is None: index = self.get_index_by_alias(alias=alias)
    put = self.es_inst.indices.put_settings(
        index=index,
        body='{"index": {"refresh_interval":' + refresh_interval_value + '}}',
        ignore_unavailable=True
    )

  
def copy_mapping(src_es_url, src_index, dst_es_url, dst_index):
  src_es = ES(src_es_url)
  mapping = src_es.get_mapping(json_fmt=False, index = src_index)
  dst_es = ES(dst_es_url)  
  #if dst_index in dst_es.indices:  dst_es.delete_index(dst_index)
  dst_es.create_index(index=dst_index, mapping_json=mapping)
   

   
def copy_index(src_es_url, src_index, dst_es_url, dst_index, batch_size=1000, option='overwrite') :
  src_es = ES(src_es_url)
  dst_es = ES(dst_es_url)
  
  if option=='fresh' :
    #dst_es.delete_index(dst_index)
    copy_mapping(src_es_url, src_index, dst_es_url, dst_index)
  
  src_count = src_es.get_doc_count(index=src_index)
  dst_count = 0
  src_es.init_scanner(index=src_index)
  dst_es.update_index_refresh(index=dst_index, refresh_interval_value='-1')
  batch = []
  for item in src_es.scanner:
    dst_count +=1
    item.pop('_score', None)
    item['_index'] = dst_index   
    batch.append(item) 
    if len(batch)>=batch_size:
      dst_es.bulk_exec(batch)
      tb.keep_print (tb.get_progress_bar(dst_count,src_count))
      batch = []
  dst_es.bulk_exec(batch)  
  dst_es.update_index_refresh(index=dst_index, refresh_interval_value='null')
  tb.keep_print (tb.get_progress_bar(dst_count,src_count))
    
if __name__ == "__main__": 
  src_es_url = 'https://search-tafe-search-dev-3jv2rifl7znw4hss5mmkq3occa.ap-southeast-2.es.amazonaws.com'
  dst_es_url = 'https://search-tafe-search-uat-w24pokccqdpapxgprypz55dxha.ap-southeast-2.es.amazonaws.com'
  
  #copy_index(url, 'products_data_v1', url, 'products_data_v2')
  #exit(1)
  dst_es = ES(dst_es_url)
  #dst_es.delete_index('products')
  #dst_es.delete_index('offerings')
  copy_mapping(src_es_url, 'products_data_v8',  dst_es_url,  'products_data_v2')
  copy_mapping(src_es_url, 'offerings_data_v8',  dst_es_url, 'offerings_data_v2')
  dst_es.set_alias(index='products_data_v2', alias='products')
  dst_es.set_alias(index='offerings_data_v2', alias='offerings')
  exit(1)
  #print (src_es.indices)
  #print (src_es.aliases)
  #print (src_es.get_index_by_alias('offerings'))
  #print (src_es.get_doc_count(alias='offerings')) 
  
  dsl_json =  {
        "_source" : ["learning_product.product_identifier"],
        "query": {
          "regexp": {
              "learning_product.product_identifier.keyword": "BSB50215.*" 
          }
      }
  }
  #print (src_es.get_analyzer(alias='products'))
  #result = src_es.query_by_dsl('detail', return_data=False, dsl_json=dsl_json, alias='offerings')
  #print (result)
  #print (result)
  
  #print (src_es.get_ids('products'))
  #print (src_es.get_doc_by_id(doc_type='detail', doc_id= 'UOS-SIT40212-15OTE-059' , alias='offerings')) 
 
  pass  