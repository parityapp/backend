# Parity (Backend)
> Backend JSON API for Parity App

Parity is a text summarization and analytics platform that works on top of the messaging systems used internally at CERN. As will be demonstrated in the demo, they can also be applied outside of CERN, considering that they are integrated with Mattermost and Slack (primarily).

## Technologies
* 🐍 **Python** - Python 3 came out with asynchronous IO features, which will allow us to take greater advantage of concurrency and serve more requests for a given server.
* 🐋 **Docker** - Containerization and easy development/production environment bootstrapping

## Getting Started
Make sure to have Docker and Docker-Compose installed. Then, follow through the following steps:
1. `cd` to the base of the project directory
2. Rename `backend_sample.env` to `backend.env`
3. Fill in the appropriate information in both `backend.env`
4. Run `docker-compose build`
5. Run `docker-compose up` and now, you should be able to access the API routes at the localhost or whatever hostname your copy of Docker is working on!
6. To shut containers down, run `docker-compose down`

## API Routes
The API routes are accessible under the `hostname/api/` URL namespace. Output is in JSON format.

An access token can be obtained by hitting the '/auth' route. Subsequent routes needing the user being logged in, can be accessed by providing an Authorization header with the value `Bearer <token>`.

Responses have the structure `{status, data, message, errors}`, where the `errors` prop is provided for ONLY whenever the `status` denotes an HTTP error status. (>=400 status codes). Responses will be nested under the `data` prop

* `/auth`
  * `POST /` - Login a user
    * Request: `{username, password}`
    * Response: `{token, channels: [{id, name}...], pulse: [{rate, time}...]}`
* `/stats`
  * `GET /pulse` - Get the activity pulse based on all channels the user is in
    * Response: `[{rate, time}...]`
      * `rate` is a float between [0,1] inclusive
      * `time` is a string that could be passed to a Javascript Date constructor
  * `GET /pulse/{channels_id}` - Get the activity pulse of a channel based on the posts
    * Response: `[{rate, time}...]`
      * `rate` is a float between [0,1] inclusive
      * `time` is a string that could be passed to a Javascript Date constructor
  * `GET /most_active/{channel_id}` - Get the most active users of a specific channel
    * Response: `[...]`
      * a list of strings
  * `GET /hot_topics/{channel_id}` - Get the "hot topics" of a channel
    * Response: `[...]`
      * a list of strings
  * `GET /representative_messages/{channel_id}` - Get past day's representative messages for the entire channel
    * Response: `[{username, message}]`
  * `POST /representative_messages/{channel_id}`
    * Request: `{time}`
      * `time` must be an ISO string
    * Response: `[{username, message}]`
  * `GET /summary/{channel_id}` - Get past day's summary for the entire channel
    * Response: `{summary}`
  * `POST /summary/{channel_id}`
    * Request: `{time}`
      * `time` must be an ISO string
    * Response: `{summary}`
