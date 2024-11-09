from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def db_connect():
        conn = psycopg2.connect(host='127.0.0.1', database='Feedback', user='postgres', password='Ashish2903', cursor_factory= RealDictCursor)
        print("Connection Succesful!")
        return(conn)


#fastapi inizialization & resource mounting
app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

templates = Jinja2Templates(directory="../templates")


@app.get("/")
def read_root():
    return {"message": "Root Page"}




@app.get("/login", response_class=HTMLResponse)
def read_login(request:Request):
    return templates.TemplateResponse("login.html", {"request":request, "title":"Login Page"})


@app.post("/login-user")
def login_user(email:str=Form(...), password:str=Form(...)):
    lconn = db_connect()
    cursor = lconn.cursor()

    try:
        cursor.execute("""SELECT id FROM users WHERE email = %s AND password = %s;""", (str(email), str(password),))
        user_id = cursor.fetchone()
        if user_id:
            print(user_id)
            return RedirectResponse(url="/users/{id}", status_code=303)
        elif user_id == None:
            print("USER NOT FOUND")
            raise HTTPException(status_code=404, detail="Please check your credentials.")
    finally:
        cursor.close()
        lconn.close()



@app.get("/register",response_class=HTMLResponse)
def read_register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request, "title":"Register Page"})
    

@app.post("/register-user")
def register_user(
     fullname: str = Form(...),
     regno: str = Form(...),
     email: str = Form(...),
     phone_number: str = Form(...),
     password: str = Form(...)
):
    try:
          lconn = db_connect()
          cursor = lconn.cursor()

          cursor.execute("""
            INSERT INTO users (fullname, regno, email, phone, password) VALUES (%s, %s, %s, %s, %s)""",(fullname, regno, email, phone_number, password))
          lconn.commit()
    except psycopg2.IntegrityError:
         lconn.rollback()
         raise HTTPException(status_code=400, detail="User with this email or registration number already exists.")
    except Exception as e:
        print(e)
    finally:
         cursor.close()
         lconn.close()

    return RedirectResponse(url="/login", status_code=303)        




@app.get("/users", response_class=HTMLResponse)
def read_users(request:Request):
    try:
        lconn= db_connect()
        cursor = lconn.cursor()

        cursor.execute(""" SELECT id, fullname, regno, email FROM users """)
        users = cursor.fetchall()

        cursor.close()
        lconn.close()

        return templates.TemplateResponse("Users.html",{"request":request, "users": users})
    
    except Exception as er:
        raise HTTPException(status_code=500, detail=str(er))


@app.post("/fetch-one", response_class=HTMLResponse)
def interact_user(request: Request, id:int = Form(...), action:str=Form(...)):
    lconn = db_connect()
    cursor = lconn.cursor()

    if action == "Fetch":
        try:
            cursor.execute("""SELECT id, fullname, regno, phone FROM users WHERE id = %s""", (str(id),))
            one_user = cursor.fetchone()

            cursor.execute(""" SELECT id, fullname, regno, phone FROM users """)
            users = cursor.fetchall()
    
            if not one_user:
                return templates.TemplateResponse("Users.html",{"request":request, "users": users, "one_user":None})
            else:
                return templates.TemplateResponse("Users.html",{"request":request, "one_user":one_user, "users":users})
        except Exception as a:
            print(a)
        finally:
            cursor.close()
            lconn.close()

    elif action == "Delete":
        try:
            cursor.execute(""" DELETE FROM users WHERE id = %s RETURNING *""",   (str(id),))
            one_user = cursor.fetchone()
            lconn.commit()

            cursor.execute(""" SELECT id, fullname, regno, phone FROM users """)
            users = cursor.fetchall()

            if not one_user:
                return templates.TemplateResponse("Users.html",{"request":request, "users": users, "one_user":None})
            else:
                return templates.TemplateResponse("Users.html",{"request":request, "one_user":one_user, "users":users, "action":action})
        except Exception as a:
            print(a)
        finally:
            cursor.close()
            lconn.close()
    
    