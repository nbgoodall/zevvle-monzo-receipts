# Zevvle Receipts in Monzo

This AWS Lambda function adds receipt data to Zevvle's Monzo transactions. It listens for charge events from the Zevvle API, finds the related Monzo transaction and uploads the data.

## Setup

1. Get your Monzo credentials

Login to the [Monzo developer portal](https://developers.monzo.com) and get your access token and  your account ID. You'll need to verify the API playground from the Monzo mobile app.

2. Deploy the Lambda function

   1. Login to the [AWS Lambda console](https://console.aws.amazon.com/lambda).
   2. Create a new function, call it whatever you like (e.g. `zevvle-monzo-receipts`) and select the Python 3.8 runtime.
   3. Upload the deployment package under `Function code` > `Actions` > `Upload a .zip file`. You can either download the premade one [from S3](https://nbgoodall.s3.eu-west-2.amazonaws.com/zevvle-monzo-receipts-aws-lambda.zip) or clone this repository, run `sh create_package.sh` and upload `function.zip`.
   4. In the `Environment variables` pane add your `MONZO_ACCESS_TOKEN` AND `MONZO_ACCOUNT_ID` from above.
   5. In the `Basic settings` pane, change the Handler to `zevvle_receipts.handler`.
   6. In the `Designer` pane, click 'Add Trigger' and select API Gateway. Select the HTTP API and set the Security to Open. Once saved, expand the details below and copy the 'API endpoint'.

3. Register the Zevvle webhook

Login to the [Zevvle developer portal](https://developers.zevvle.com). You'll need a Zevvle account with an active SIM card.

Copy the secret token and register a webhook to receive charge events:
```
  curl -G -X POST https://api.zevvle.com/webhooks \
  -H "Authorization: Bearer $ZEVVLE_SECRET_TOKEN" \
  -d "url=$LAMBDA_FUNCTION_INVOKE_URL" \
  -d "type=charge.created"
```

And you're done! Zevvle receipts will now show in Monzo. ☎️ 💳

## The future

- Add data/call/sms usage to transaction notes
- PDF receipt attachments

And a generic integration with e.g. Flux for multi-bank Zevvle receipts...