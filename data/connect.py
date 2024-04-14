import psycopg2

import os

from dotenv import load_dotenv, find_dotenv
import psycopg2

load_dotenv(find_dotenv())
                                                  
connection = psycopg2.connect(                                                  
    user = os.getenv("USER"),                               
    password = os.getenv("PASSWORD"),           
    host = os.getenv("HOST"),                                            
    port = os.getenv("PORT"),                                         
    database = os.getenv("DB")                                      
)