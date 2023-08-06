# Channels-Redux

Channels-Redux is a package that notifies subscribers about changes in the database

It should be paired with the [npm package of the same name](https://www.npmjs.com/package/channels-redux). 
The pypi package [django-react-views](https://pypi.org/project/django-react-views/) is also useful for hydrating initial state

## Exposed Modules

### NotifyConsumer
This is an AsyncWebsocketConsumer that allows clients to subscribe to different models and objects and sends frames 
when subscribed objects are updated, created or deleted. Unless you plan on extending it's functionality you don't 
need to do anything with this.

### NotifyRouter
NotifyRouter is a channels.routing.URLRouter that defines a default URL that routes connections to NotifyConsumer

### NotifierMixin
Extending this mixin marks a model as being a 'Notifier' this means that it will send frames to subscribed clients
when changes happen on the server side.

This also defines a property that returns the name of the api url for the model. By default it assumes the namespace
of your api is 'api' this can be overridden by defining `API_APP_NAMESPACE` in your settings.

### HyperlinkedModelSerializer
A drop-in replacement for DRF's HyperlinkedModelSerializer that fixes some issues with URL fields and relationships 
in a namespaced api

### RestRouter
A drop-in replacement for DRF's DefaultRouter that should be used to assign the expected default base names for
your api urls.

## Quick Start

1. Add to installed apps
    ```python
    INSTALLED_APPS = [
       ...
       'channels_redux',
    ]
    ```

1. Models that you want clients to receive notifications about should extend the NotifierMixin

1. Setup your models with Django Rest Framework with the following exceptions:
    1. Instead of the DRF's HyperlinkedModelSerializer you should use 
channels_redux.rest.HyperlinkedModelSerializer. At minimum your serializers should include the `url` and the `pk` fields.
    1. User RestRouter instead of DefaultRouter for your api routes
        ```python
        router = RestRouter()
        router.register(r'appname/modelname', viewsets.ModelNameViewSet)
        ```

1. Setup django-channels. Follow their docs for this with the following exceptions:
    1. In routing.py use the NotifyRouter 
        ```python
        application = ProtocolTypeRouter({
            "websocket": AuthMiddlewareStack(NotifyRouter()),
        })
        ```
    1. channels-redux **requires** channel layers, so be sure to set those up.

1. Use django-react-views to provide the initial data to your frontend

1. On the frontend use channels-redux js to setup your redux state and WebsocketHandler before rendering any react components
    ```javascript
    // In the root component that your page loads.
    import {WebSocketHandler, store} from 'channels-redux';
    const webSocketHandler = new WebSocketHandler(store);
    webSocketHandler.subscribeAll();
    ```