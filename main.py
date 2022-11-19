from ensurepip import version
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from auth.authentication import auth_routes
# from users.routes import users_routes
# from tips.routes import tips_routes
# from categories.routes import categories_routes
# from articles.routes import articles_routes
from auth.token import auth_route

tags_metadata = [
    
    {
        "name" : "auth",
        "description" : "Users authentication Operation",
        "externalDocs" : {
            "description" : "Manage authentication",
            "url" : "https://qwiyi.com",
        }
    }
]

description = """
Qwiyi api for app
"""

app = FastAPI(
    title="Qwiyi App",
    description =description,
    version = "0.0.1",
    terms_of_service = "https://qwiyi.com",
    contact = {
        "name" : "qwiyi Ltd",
        "url" : "https://qwiyi.com",
        "email" : "info@qwiyi.com",
    },
    license_info = {
        "name": "Apache 2.0",
        "url" : "https://qwiyi.com"
    },
    openapi_tags = tags_metadata,
    docs_url="/documentation", 
    redoc_url=None
)


# app.include_router(users_routes)
app.include_router(auth_route)
# app.include_router(apply)
# app.include_router(tips_routes)
# app.include_router(categories_routes)
# app.include_router(articles_routes)

origins = [
    "https://qwivi.com",
    "https://www.qwivi.com",
    "http://localhost:3000",
    "localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000"
]


app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)


