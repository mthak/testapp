from flask import Flask,request,jsonify,abort
from pymongo import MongoClient
import hashlib
import logging
app = Flask(__name__)
@app.route('/messages', methods=['POST'])
def main_handler():
   '''
      Main routing for requests
   '''
   if request.method == 'POST':
      return parse_message(request.get_json())
   else:
       return message_retrieve(hash_val)


def parse_message(msg):
    data = msg['message']
    shasum_msg = hashlib.sha256(data).hexdigest()
    msgdict = {}
    msgdict['message'] = data
    msgdict['digest'] = shasum_msg
    logging.info( " print message stored in db is %s ", msgdict) 
    result = db.collection.find_one({'message':data})
    print " result is " , result
    if result is None:
       db.collection.insert_one(msgdict)
       return msgdict['digest']
    else:
        exception = dict({"message": "A message with this value arelady exist"})
        raise Exception(exception)

@app.route('/messages/<hash_val>', methods = ['GET'])
def message_retrieve(hash_val):
    print hash_val
    result = db.collection.find_one({"digest": hash_val},{"message":1,"_id":0})
    print "result is " , result
    if result is not None:
       return jsonify(**result)
    else:
        return abort(404)
if __name__ == "__main__":
    LOG_FORMAT = '[%(asctime)s] %(process)d %(module)-12s %(levelname)-8s %(message)s'
    DATE_FORMAT = '%d/%b/%Y %H:%M:%S %z'
    logging.basicConfig(level=logging.INFO,
                        format=LOG_FORMAT, datefmt=DATE_FORMAT)
    client = MongoClient('mongodb://localhost/27017/')
    db = client['messages']
    collection = db['message-info']
    app.run(debug=True)


