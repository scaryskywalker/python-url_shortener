from pydantic import BaseModel, AnyHttpUrl, ValidationError, field_validator
import secrets
import mysql.connector
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import base62
import hashlib
from hash_verification import is_sha256

api = FastAPI()
api.mount("/static", StaticFiles(directory="static"), name="static")
suffix = "~"

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
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        user="3vMCMeyHyb8v8vs.root",
        password="99Y9B9VKR3i339kD",
        database="url_shortener")
        
        if use_base62 == True:
            link_id = secrets.token_hex(8)
            encrypted_id = base62.encode(int(link_id, 16)) + suffix
            short_url = str(request.base_url) + encrypted_id
            print(link_id)
            encoding = "base62"

        elif use_hash == True:
            link_id = secrets.token_hex(8)
            encrypted_id = hashlib.sha256(link_id.encode()).hexdigest()
            short_url = str(request.base_url) + encrypted_id
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
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        user="3vMCMeyHyb8v8vs.root",
        password="99Y9B9VKR3i339kD",
        database="url_shortener")

        cursor = mydb.cursor()

        if retrieve_link.endswith(suffix):
            encoded_part = retrieve_link[:-len(suffix)]
            
            base_cursor = mydb.cursor()
            base_cursor.execute("SELECT id FROM users WHERE (encoding = %s)", ("base62", ))

            baseLinks = [row[0] for row in base_cursor.fetchall()]
            for i in baseLinks:
                j = base62.encode(int(i, 16))
                if j == encoded_part:
                    retrieve_link = i
                else: continue
            

        elif is_sha256(retrieve_link):
            hash_cursor = mydb.cursor()
            hash_cursor.execute("SELECT id FROM users WHERE (encoding = %s)", ("hash",))

            hash_link = [row[0] for row in hash_cursor.fetchall()]
            for i in hash_link:
                j = hashlib.sha256(i.encode()).hexdigest()
                if j == retrieve_link:
                    retrieve_link = i
                else:
                    continue

            hash_cursor.close()
        else:
            retrieve_link = retrieve_link

        cursor.execute("SELECT originalLink FROM users WHERE (id = %s)", (retrieve_link, ))
        link = cursor.fetchone()

        cursor.close()
        mydb.close()

    except mysql.connector.Error as err:
        return {"Database Error" : err}

    if link is None:
            return {"error" : "Invalid Link"}


    return RedirectResponse(url=link[0])