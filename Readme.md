# Cambioo Meme Generator

An application that allows you to create memes with your own images and text and share them with your colleges.
The application consists of a REST API that provides enpoints to create, read, upvote and downvote memes.\

## Building and Running the Application

The project uses docker-compose to run the application. To build the application run the following command:

```bash
docker-compose build
```

To run the application run the following command:

```bash
docker-compose up
```
 By default, the API will be available at http://localhost:3000 and the database will be available at http://localhost:5432.


## API Endpoints

The API provides the following endpoints:
- POST /api/meme/
- GET /api/meme/{id}
- POST /api/meme/{id}/vote/
- GET /api/meme/top/
- GET /api/meme/random/

### POST /api/meme/

This endpoint allows you to create a meme. The request body should be a JSON object with the following fields:
```json
{
  "url": "{url to an image}",
  "caption": "{caption of the meme}"
}
```

On success, the api will return a JSON object with the following fields:
```json
{
    "status": "success",
}
```

#### Errors

The `url` field should be a valid url to an image, otherwise the api will return the following JSON object:
```json
{
    "status": "error",
    "error": "Invalid url"
}
```

If any error occurs, such as if a field is invalid, a standard HTTP error will be returned.

---

### GET /api/meme/{id}

This endpoint allows you to get a meme by its id. The api will return a JSON object with the following fields:
```json
{
    "id": "{id of the meme}",
    "url": "{url to an image}",
    "caption": "{caption of the meme}",
    "upvotes": "{number of upvotes}",
    "image": "{base64 encoded image}"
}
```

#### Errors

If the meme does not exist, the api will return the following JSON object:
```json
{
    "status": "error",
    "error": "Meme not found"
}
```

If any other error occurs, a standard HTTP error will be returned.

---

### POST /api/meme/{id}/vote/

This endpoint allows you to upvote or downvote a meme. The request body should be a JSON object with the following fields:
```json
{
  "type": "{'upvote' or 'downvote'}"
}
```

On success, the api will return a JSON object with the following fields:
```json
{
    "status": "success",
}
```

#### Errors

If the type field is not 'upvote' or 'downvote', the api will return the following JSON object:
```json
{
    "status": "error",
    "error": "Invalid vote type"
}
```

If the meme does not exist, the api will return the following JSON object:
```json
{
    "status": "error",
    "error": "Meme not found"
}
```

If any other error occurs, a standard HTTP error will be returned.

---

### GET /api/meme/top/

This endpoint allows you to get the top 10 memes by upvotes. The api will return a JSON object with the following fields:
```json
{
    "status": "success",
    "data": [
        {
            "id": "{id of the meme}",
            "url": "{url to an image}",
            "caption": "{caption of the meme}",
            "upvotes": "{number of upvotes}",
            "image": "{base64 encoded image}"
        },
        ...
    ]
}
```

#### Errors

If there was an error with the database, the api will return the following JSON object:
```json
{
    "status": "error",
    "error": "Error fetching memes"
}
```

If any other error occurs, a standard HTTP error will be returned.

---

### GET /api/meme/random/

This endpoint allows you to get a random meme. The api will return a JSON object with the following fields:
```json
{
    "id": "{id of the meme}",
    "url": "{url to an image}",
    "caption": "{caption of the meme}",
    "upvotes": "{number of upvotes}",
    "image": "{base64 encoded image}"
}
```

#### Errors

If there was an error with the database, the api will return the following JSON object:
```json
{
    "status": "error",
    "error": "Error fetching meme"
}
```

If any other error occurs, a standard HTTP error will be returned.

---

## Testing





