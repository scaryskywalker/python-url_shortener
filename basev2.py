from pydantic import BaseModel, AnyHttpUrl, ValidationError, field_validator
import secrets
import mysql.connector
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import base62
import hashlib

api = FastAPI()
api.mount("/static", StaticFiles(directory="static"), name="static")


class Links(BaseModel):
    originalLink: AnyHttpUrl

    @field_validator("originalLink", mode="before")
    @classmethod
    def add_https(cls, value):
        if isinstance(value, str) and not value.startswith(("http://", "https://")):
            value = "https://" + value
        return value

templates = Jinja2Templates(directory="templates")
@api.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")



@api.post("/genlink")
def gen_link(request: Request,original: str = Form(...), use_base62: bool = Form(False), use_hash: bool = Form(False)):
    cursor = None
    try:
        org_link = Links(originalLink = original)
        mydb = mysql.connector.connect(
        host="sql.freedb.tech",
        user="u_pmK7Fi",
        password="2B02yfeSPLWn",
        database="freedb_F5jF3SOu")

        if use_base62 == True:
            link_id = base62.encode(int(secrets.token_hex(8), 16))
            short_url = str(request.base_url) + link_id
            encoding = "base62"
        elif use_hash == True:
            link_id = hashlib.sha256(secrets.token_bytes(8)).hexdigest()
            short_url = str(request.base_url) + link_id
            encoding = "hash"
        else:
            link_id = secrets.token_hex(8)
            short_url = str(request.base_url) + link_id
            encoding = "hex"
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO users (id, originalLink, encoding) VALUES (%s, %s, %s)", (link_id, str(org_link.originalLink), encoding))
        mydb.commit()
    except mysql.connector.Error as err:
        return {"Database Error" : err}
    
    except ValidationError as e:
        return {"message" : "validation error"}

    finally:
        if cursor is not None:
            cursor.close()
            mydb.close()


    return templates.TemplateResponse(request=request, name="index.html", context={"short_link": short_url})



@api.get("/{retrieve_link}")
def redirect(retrieve_link: str):
    try:
        mydb = mysql.connector.connect(
        host="sql.freedb.tech",
        user="u_pmK7Fi",
        password="2B02yfeSPLWn",
        database="freedb_F5jF3SOu")



        cursor = mydb.cursor()
        cursor.execute("SELECT originalLink FROM users WHERE (id = %s)", (retrieve_link, ))
        link = cursor.fetchone()

        cursor.close()
        mydb.close()

    except mysql.connector.Error as err:
        return {"Database Error" : err}

    if link is None:
            return {"error" : "Invalid Link"}


    return RedirectResponse(url=link[0])