from pydantic import BaseModel, AnyHttpUrl, ValidationError, field_validator
import secrets
import mysql.connector
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

api = FastAPI()


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
def gen_link(request: Request,original: str = Form(...)):
    try:
        org_link = Links(originalLink = original)
        mydb = mysql.connector.connect(
        host="sql.freedb.tech",
        user="u_pmK7Fi",
        password="2B02yfeSPLWn",
        database="freedb_F5jF3SOu")
        link_id = secrets.token_hex(8)
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO users (id, originalLink) VALUES (%s, %s)", (link_id, str(org_link.originalLink)))
        mydb.commit()
    except mysql.connector.Error as err:
        return {"Database Error" : err}
    
    except ValidationError as e:
        return {"message" : "validation error"}

    finally:
        cursor.close()
        mydb.close()

    short_url = str(request.base_url) + link_id

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