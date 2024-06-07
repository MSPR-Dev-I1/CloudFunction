## Repo des cloud functions

Pour connecter le cli : 
``` 
gcloud init
```
```
gcloud functions deploy NOM_CLOUD_FUNCTION --gen2 --runtime=python312 --region=europe-west9 --entry-point=NOM_DE_LA_FONCTION --source=.  (--trigger-topic="gcr")
```