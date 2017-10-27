# Notemaker API

Simple API hosted on Google App Engine that uses Google+ OAuth2 to allow users to make/update/see notes, 
including a distinction between notes private to the user and notes by a user but visible to others.

### Prerequisites

Account on Google App Engine.

### Installing

Upload the project to GAE, use terminal on GAE console to deploy using a command like `gcloud app deploy --project [YOUR_PROJECT_ID]`. 
Use the GAE [deployment docs](https://cloud.google.com/appengine/docs/standard/python/tools/uploadinganapp) 
or a quick-start tutorial project on GAE for more info.


## Built With

* WebApp2 (python2.7)
* yaml for markup/configuration
* GooglePlus Oauth2 (little bit of re-inventing the wheel here)
* ndb for nonrelational database (see [here](https://cloud.google.com/appengine/docs/standard/python/ndb/))
* Google App Engine for hosting on the cloud

## Authors

Jon Hutter, github.com/jhutter

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file or [here](http://www.apache.org/licenses/LICENSE-2.0) for details

## Acknowledgments

* Thanks for GAE documentation (and Stack Overflow question-askers who came before me, ha)
* CS 496 coursework cited throughout
* Other sources cited where they are used
