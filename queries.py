import os
from flask import Flask, render_template, request, url_for, redirect
import pandas as pd
import mysql.connector

myConnection = mysql.connector.connect(
    user = 'root',
    password = 'Thisistp.4j!',
    host = 'localhost',
    database = 'Pokemon'
)
cursorObject = myConnection.cursor()

def region_filter(region_name):
    query = f"SELECT region_name FROM regions WHERE region_name = '{region_name}';"
    df = pd.read_sql(query, myConnection)
    return df

def pokemon_filter(moves, types, ability, region):
    query = f"SELECT pokemon_name FROM pokemon p JOIN pokemon_abilities pa ON pa.pokemon_id = p.pokemon_id JOIN regions r ON r.region_id = p.region_id WHERE pa.ability = '{moves}' AND p.type1 = '{types}'  AND r.region_name = '{region}'"
    df = pd.read_sql(query, myConnection)
    return df


