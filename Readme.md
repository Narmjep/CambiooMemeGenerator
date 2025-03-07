# Cambioo Meme Generator

An application that allows you to create memes with your own images and text and share them with your colleges.
The application consists of a REST API that provides enpoints to create, read, upvote and downvote memes.\

## Building and Running the Application

### Docker

The project uses docker-compose to run the application. To build the application run the following command:

```bash
docker-compose build
```

To run the application run the following command:

```bash
docker-compose up
```
 By default, the API will be available at http://localhost:3000 and the database will be available at http://localhost:5432.

### Local

To run the API locally, install the python modules from the [requirements.txt](src/requirements.txt) file.
Run the API using uvicorn:

```bash
uvicorn src.main:app --reload
```


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
or
```json
{
  "image": "{base64 encoded image}",
  "caption": "{caption of the meme}"
}
```

If both the `url` and `image` fields are provided, the `url` field will be used and the `image` field will be overwritten.



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

To run the tests, install the python modules from the [requirements.txt](Tests/requirements.txt) file.
Run the tests using pytest:

```bash
pytest Tests
```


## Tools

Two additional tools are provided to interact with the API:

- getData.py: A python script that lists all the memes in the database but ignores the image.
- viewImage.py: A python script that downloads and displays the image of a meme and saves both the stored image and the original image form the url in the current directory.

To run the tools, install the python modules from the [requirements.txt](Tools/requirements.txt) file and run:

```bash
python -m Tools.getData
```
or
```bash
python -m Tools.viewImage {id}
```






