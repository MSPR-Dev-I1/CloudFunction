## Repo des cloud functions

Pour connecter le cli : 
``` 
gcloud init
```
```
gcloud functions deploy python-pubsub-function --gen2 --runtime=python312 --set-secrets Github_user=Github_user:1  --set-secrets Github_token=Github_token:1 --set-secrets Github_user_email=Github_user_email:1  --region=europe-west9 --entry-point=detect_new_image --source=. --trigger-topic="gcr"
```