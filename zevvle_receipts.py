import os, json, datetime, requests, base64
from dateutil.parser import parse
from monzo import Monzo

# Monzo initialization
MONZO_ACCESS_TOKEN = os.environ['MONZO_ACCESS_TOKEN']
monzo_client = Monzo(MONZO_ACCESS_TOKEN)

MONZO_ACCOUNT_ID = os.environ['MONZO_ACCOUNT_ID'] or monzo_client.get_first_account()['id']


### Receipts

MONZO_RECEIPTS_URL = 'https://api.monzo.com/transaction-receipts'

def register_receipt(receipt):
  request_headers = { 'Authorization': f'Bearer { MONZO_ACCESS_TOKEN }'}

  return requests.put(MONZO_RECEIPTS_URL, data = json.dumps(receipt), headers = request_headers)

def format_line_item(zevvle_item):
  return {
    "description": zevvle_item['description'],
    "quantity": zevvle_item['quantity'],
    "amount": zevvle_item['price'],
    "currency": "GBP"
  }

def build_receipt(tx_id, zevvle_charge):
  items = list(map(format_line_item, zevvle_charge['items']))

  receipt = {
    'transaction_id': tx_id,
    'external_id': zevvle_charge['id'],
    'total': zevvle_charge['amount'],
    'currency': 'GBP',
    'items': items
  }

  return receipt

# End receipts

### Zevvle transactions in Monzo

def filter_zevvle_txs(tx):
  return tx['merchant'] and tx['merchant']['name'] == 'Zevvle'

def latest_zevvle_transactions():
  try:
    one_day_ago = datetime.datetime.utcnow() + datetime.timedelta(days = -1)

    txs = monzo_client.get_transactions(MONZO_ACCOUNT_ID, since = one_day_ago)['transactions']

    txs.reverse()

    return list(filter(filter_zevvle_txs, txs))
  except Exception as err:
    print('OH GOODNESS NO:', err)

    return []

# Tolerance for the minor difference between Monzo's payment time and that of Zevvle's payment provider
PAYMENT_TIME_TOLERANCE = 3 # seconds

def find_zevvle_transaction(charge_event):
  txs = latest_zevvle_transactions()

  for tx in txs:
    seconds_difference = abs((parse(tx['created']) - parse(charge_event['paid_at'])).total_seconds())

    if charge_event['amount'] == -tx['amount'] and seconds_difference < PAYMENT_TIME_TOLERANCE:
      return tx

  return None

# End Zevvle transactions in Monzo

### Lambda function handler

def decode_event(event):
  event_bytes = base64.b64decode(event['body'])

  return json.loads(event_bytes.decode('utf-8'))['data']

def handler(event, context):
  try:
    charge_event = decode_event(event)

    zevvle_tx = find_zevvle_transaction(charge_event)

    if zevvle_tx:
      receipt = build_receipt(zevvle_tx['id'], charge_event)

      res = register_receipt(receipt)

    return {
      'statusCode': 200,
      'body': json.dumps('Successfully updated the Zevvle receipt in Monzo.')
    }
  except Exception as err:
    return {
      'statusCode': 500,
      'body': json.dumps('Failed with error: ' + str(err))
    }

# End Lambda function handler