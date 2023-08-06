#Idées Job Manager v3

### General

   - Serializer la classe et le code
   - Avoir un json pour declarer des arguments
   - Separer input et output pour rendre ces 2 parties seulement modifiables
   - Creer un job == definition input + definition output + method process
    
### API

   - Notion de client/host à revoir avec K8s
   - Client page à revoir
    

### Client

   - Coté client, n'accéder à la BDD non plus avec mongoengine mais seulement via l'API (update status, update output) 
   - Si pas d'accès à la BDD, possibilité de créer l'objet dynamiquement et d'appeler process dessus?
   - Quid du debug temps reel? et du code?
   - Déplacer les dependances pip dans un attribut de classe : Les dependances sont importées au debut de la creation de l'objet job et un reporting est fait si problème.
    

### Logging

   - Logging via BDD si besoin ? logstash => mongo  on perd les metadonnées liées aux lignes job id, client id, etc.
   - Logging par batch via api ou via websocket upload, stream json objects => mieux

    
### Idées

   - Docker build par classe de job
   - k8s horizontal scale basé sur nombre de jobs en attente