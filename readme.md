# EVE Market Toolkit


This library contains several functions to access and plot market data from the EVE ESI

# EVE Online

Eve Online is a space-based, persistent world massively multiplayer online role-playing game developed and published by CCP Games. 
Players of Eve Online can participate in a number of in-game professions and activities, including mining, piracy, manufacturing, trading, exploration, and combat.

### The EVE ESI

In the last few years, the rest of the software industry has been busy making various APIs and considering their designs. Out of the chaos of custom made nonsense arose the JSON schema standards, and from that, the Swagger specification. This is a core concept of ESI, and the Swagger Specification has this to say about itself:

Swagger™ is a project used to describe and document RESTful APIs.

The Swagger specification defines a set of files required to describe such an API. These files can then be used by the Swagger-UI project to display the API and Swagger-Codegen to generate clients in various languages. Additional utilities can also take advantage of the resulting files, such as testing tools.

Swagger is a widely adopted API description standard, and is backed by quite a few reputable organisations, which gives us confidence in its longevity and support for client libraries, user interfaces and other tooling. Choosing to adopt the Swagger specification (now known as OpenAPI) removes a bunch of work from our plates, and gives a clear reference point to build any custom integrations against.

It is on this foundation that we've chosen to build the EVE Swagger Interface, a framework which aggregates partial specs from multiple Kubernetes services into a cohesive front facing spec, while also handling the routing, authentication, input/output validation, and more. The EVE Swagger Interface (ESI for short and pronounced "easy") uses Flask and Python 3.4+ internally, and should be generic enough to power any oauth-backed (or unauthed), multi-tenant API running in a Kubernetes cluster. There are also options for running ESI locally with either Docker or directly with local Python.


