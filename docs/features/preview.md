# Preview in Docflow

Let's see how preview feature of DocFlow works. 🚀

- 🎯 Endpoint:
`GET /api/document/preview/:document`
- ⚙️ Params:
`{document: <docuent_id_or_name>}`
- 🔐 Authorization:
`Bearer <token>`

Here in Preview we use two important models, `fastapi.response`'s `FileResponse` amd `tempfile`'s `NamedTemporaryFile`.

`FileResponse` is used to return files.

`NamedTemporaryFile` is a function in Python's `tempfile` module that creates a temporary file with a unique name in the 
system's default location for temporary files. This function returns a file-like object that can be used in similar way 
to other file objects.

Here is the brief explanation on how it works:
- When we call `NameTemporaryFile()`, it creates a new file in you system's temporary directory.
- The temporary file is opened in binary mode (`wb+`) by default, and it can be read from and written to like any other
file object.
- The temporary file is deleted as soon as it is closed. This is controlled by the `delete` parameter, which is `True` 
by default. This is important to set it `True`, as if not done then it could fill up the server's storage.

The following figure describes how Preview in DocFlow works. 
