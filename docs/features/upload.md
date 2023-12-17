# Document Upload in DocFlow

- 🎯 Endpoint:
`GET /api/document/upload`
- ⚙️ Params:
`{
    folder: <folder_name>,
    file=@"/path/to/file
}`
- 🔐 Authorization:
`Bearer <token>`

➰ cURL:
```commandline
curl --location 'localhost:8000/api/document/upload?folder=' \
--header 'Content-Type: multipart/form-data' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer <token>' \
--form 'file=@"/path/to/file"'
```

So the following API, upload the file to s3 and adds the metadata to the database, so how this works:

The endpoint returns a `DocumentMetadataRead` object, which contains metadata about the uploaded document, or a 
Dict[str, str] object in case of an error or other non-standard situation. The response of `DocumentRepository.upload`
has two cases, `file_added` and `file_updated`. `file_added` is the case when the uploaded file does not exist for that
user. And `file_updated`, when the file with the same name, exits and the new version of the file is added (details about
versioning is mentioned [here]()).
