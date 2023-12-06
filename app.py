from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import base64
import os
from google.cloud import dialogflow_v2 as dialogflow_v2
import uuid

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

client = MongoClient('')
db = client['voiceassistance']  # Replace with your database name
collection = db['brand']  # Replace with your collection name
app = Flask(__name__)


@app.route('/')
def serve_image():

  return render_template('home.html')


@app.route('/model')
def serve_model():
  # brand =data.queryResult.parameters.brand;
  documents = collection.find({"brandname": "BMW"})
  images = []
  for document in documents:
    image_data = document['data']
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    images.append({
        'brand': document['brandname'],
        'image_data': image_base64,
        'model': document['modelname'],
        'color': document['color']
    })
  return render_template('model_container.html', cars=images)


@app.route('/dialog', methods=['POST'])
def receive_text_data():

  data = request.get_json()
  text_data = data.get('text')
  response = send_text_to_dialogflow(text_data)
  intent_name = response.query_result.intent.display_name
  fullfilment_text = response.query_result.fulfillment_text
  if intent_name == "Welcome Intent" or intent_name == "Default Fallback Intent":
    return jsonify({
        'fullfilment_text': fullfilment_text,
        'intent_name': intent_name
    })
  elif intent_name == "brand-collections":
    documents = collection.find({'brands': {'$exists': True}})
    images = []
    for document in documents:
      image_data = document['data']
      image_base64 = base64.b64encode(image_data).decode('utf-8')
      images.append({'brand': document['brands'], 'image_data': image_base64})
    return render_template('image_container.html', cars=images)
  elif intent_name == "brand_selection":
    print(response.query_result.parameters['brand'])
    if len(response.query_result.parameters['brand']) != 0:
      brand = response.query_result.parameters['brand'][0]

      documents = collection.find({"brandname": brand})
      images = []
      for document in documents:
        image_data = document['data']
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        images.append({
            'brand': document['brandname'],
            'image_data': image_base64,
            'model': document['modelname']
        })
      return render_template('model_container.html', cars=images)
    else:
      return jsonify({
          'fullfilment_text': fullfilment_text,
          'intent_name': intent_name
      })
  elif intent_name == "model_selection":
    print(response.query_result.parameters['models'])
    if len(response.query_result.parameters['models']) != 0:
      model = response.query_result.parameters['models']
      documents = collection.find({"modelspecific": model})
      images = []
      for document in documents:
        image_data = document['data']
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        images.append({
            # 'brand': document['brandname'],
            'image_data': image_base64,
            'model': document['modelspecific'],
            'color': document['color'],
            'year': document['year'],
            'mileage': document['mileage'],
            'fuel': document['fuel'],
            'HP': document['HP'],
            'cc': document['cc'],
            'price': document['price']
        })
      return render_template('All_details_container.html', cars=images)
    else:
      return jsonify({
          'fullfilment_text': fullfilment_text,
          'intent_name': intent_name
      })
  else:
    return jsonify(fullfilment_text)


def send_text_to_dialogflow(text):
  project_id = "chat-bot-ejku"

  # Generate a random session ID
  session_id = str(uuid.uuid4())

  session_client = dialogflow_v2.SessionsClient()
  session = session_client.session_path(project_id, session_id)

  text_input = dialogflow_v2.TextInput(text=text, language_code="en-US")
  query_input = dialogflow_v2.QueryInput(text=text_input)

  response = session_client.detect_intent(session=session,
                                          query_input=query_input)
  return response


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
