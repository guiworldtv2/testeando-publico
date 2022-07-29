import numpy as np
import pandas as pd
import json

from bs4 import BeautifulSoup
from flask import session, redirect, url_for, render_template, request

import requests
from requests_oauthlib import OAuth2Session

from . import main
from ._const import CLIENT_ID,CLIENT_SECRET,REDIRECT_URI

scope=['public','private','stats']
oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI,scope=scope)

@main.route('/',methods=['GET'])
def index():
    print('route with GET')
    return render_template('index.html')

@main.route('/',methods=['POST'])
def index_post():
    print('route with POST')
    return render_template('index.html')

@main.route('/getviews',methods=['POST'])
def getviews():

    global df_ff
    print('trying without AUTH')

    email = request.form['email']
    pw = request.form['password']

    payload2 = {'user_account[email]': email,'user_account[password]': pw}

    with requests.Session() as s:
        p = s.post('https://filmfreeway.com/login',data=payload2)
        r = s.get('https://filmfreeway.com/submissions/my_submissions?project=&q=&per_page=500')
        soup = BeautifulSoup(r.text,'html.parser')

    df_ff = parse_ff(soup)

    # SOOOO, this is gonna do the authorization request every time...
    authorization_url, state = oauth.authorization_url('https://api.vimeo.com/oauth/authorize')
    return redirect(authorization_url)

@main.route('/authori',methods=['GET'])
def authori():
    global df_ff
    global df_v
    print('route with authorized')
    resp = request.url
    resp = resp.replace('http','https')
    token = oauth.fetch_token('https://api.vimeo.com/oauth/access_token',
                              authorization_response=resp,
                              client_secret=CLIENT_SECRET)

    start_date = '2019-07-29'
    end_date = '2019-08-29'

    rURL = 'https://api.vimeo.com/me/videos/stats?group_by=embed_path&start_date=2018-09-01&end_date=2019-09-01&per_page=50&filter_embed_domains=filmfreeway.com&sort=plays&direction=desc&fields=url%2Cplays%2Cfinishes%2Cloads%2Cdownloads%2Cwatched&csv=https%3A%2F%2Fapi.vimeo.com%2Fme%2Fvideos%2Fstats%3Fstart_date%3D2018-09-01%26end_date%3D2019-09-01%26fields%3Durl.domain%2Cplays%2Cfinishes%2Cloads%2Cdownloads%2Cwatched.mean_percent%26group_by%3Dembed_domain%26per_page%3D15000%26sort%3Dplays&page=1'

    r = oauth.get(rURL)
    data = r.json()['data']
    df_v = pd.read_json(json.dumps(data))
    df_v['subid']=df_v.url.apply(lambda x: x['path'].split('/')[-1])
    df_v = df_v.set_index('subid')

    df_ff = df_ff.set_index('subid')
    df_ff = df_ff.join(df_v)
    df_ff = df_ff.fillna(0).rename(columns={'loads': 'Loads', 'plays': 'Plays'})
    #df_ff = df_ff.dropna().reset_index()
    df_ff = df_ff[['Festival','Project','Notification Date','Loads','Plays']]

    return render_template('views.html',
                           output = [df_ff.to_html(classes=["table-bordered", "table-striped", "table-hover"],
                                                   header=True,float_format=lambda x: '%d' %x,
                                                   index=False)])

def parse_ff(soup):
    rows = soup.find_all("div", class_="tableRow")
    subid = []
    notifdate = []
    festival = []
    project = []

    for row in rows:
        subid.append(row.get('data-submission'))
        notifdate.append(row.find_all('div',class_='DateDesktop')[0].get_text().strip())
        festival.append(row.find_all('div',class_='Festival')[0].get_text().strip())
        project.append(row.find_all('div',class_='Project')[0].get_text().strip())

    return pd.DataFrame(np.array([subid,notifdate,festival,project]).T,columns=['subid','Notification Date','Festival','Project'])
