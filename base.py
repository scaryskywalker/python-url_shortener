from pydantic import BaseModel, AnyHttpUrl, ValidationError, field_validator
import secrets
import mysql.connector
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

api = FastAPI()

print("hello")

class links(BaseModel):
    originalLink: AnyHttpUrl

    @field_validator("originalLink", mode="before")
    @classmethod
    def add_https(cls, value):
        if isinstance(value, str) and not value.startswith(("http://", "https://")):
            value = "https://" + value
        return value



@api.get("/")
def root():
    return {"message": "Hello World"}


@api.post("/")
def gen_link(org_link: links):
    

    try:
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

    return {"Generated Short Link": link_id}

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