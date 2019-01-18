
import json
import requests

# [START gae_python37_app]
from flask import Flask, Response, request, jsonify
from pprint import pprint
from threading import Thread


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/top25', methods = ['GET','POST'])
def top25():
    """Posts top 25 rankings"""

    def delayed_response(form):
        """Sends a delatyed response back to the channel the slash command was invoked from."""

        params = form.get('text')
        rank_type = 'full' if params == 'full' else None
        if rank_type is None: 
            rank_title = 'TOP 25'
            sheets_values = 'Top 25!A1:G26'
        else: 
            rank_title = 'FULL'
            sheets_values = 'Full Rankings!A1:G87'
        
        sheet_id = '18HhjFkZ-Z7Iuafllkd8StHONbhdePcTQeKUTLFo3TrU'
        sheets_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}?key=AIzaSyD59KmdlMqgYpUcakIonO-yjaeg55D60hY'.format(sheet_id, sheets_values)

        # First call the Google Sheets API to retrieve our Top 25 rankings data
        r = requests.get(sheets_url)
        raw_json = r.json()
        results = raw_json['values']
        fields = []
         
        count = 0
        for rank,team,abbrv,record,score,delta,logo in results:
            if (count == 0):
                field_rank = {
                    'title': ('{} {}'.format('RK'.ljust(11),'TEAM'.ljust(24))),
                    'short': 'true'
                }
                field_trend = {
                    'title': ('{}'.format('TREND')),
                    'short': 'true'
                }
            else:
                rk_space = ' ' if int(rank) < 10 else ''
                bold_rank = '`#' + rk_space + rank + '`'
                team_display = logo + ' ' + abbrv.ljust(6)
                abbrv_display = abbrv.ljust(6)
                field_rank = {
                    'value': ('{} {} {}'.format(bold_rank.rjust(10),logo,abbrv_display)),
                    'short': 'true',
                }
                field_trend = {
                    'value': ('{}'.format(delta)),
                    'short': 'true'
                }
            fields.append(field_rank)
            fields.append(field_trend)
            count += 1
        
        title_text = ':ncff: {} RANKINGS'.format(rank_title)
        attachments = [
            {
                'fallback': ':ncff: Rankings',
                'title': title_text,
                'title_link': 'https://datastudio.google.com/open/1pUtKEQuveWvwqUMRloALhM2AovPVZJGp',
                'fields': fields,
                'mrkdwn_in': ['fields']
            }
        ]
        
        url = form.get('response_url')
        user_id = form.get('user_id')
        user_name = form.get('user_name')
        channel_name = form.get('channel_name')

        msg_text = '<@{}>, here you go!'.format(user_id)
        json_body = {
            'response_type': 'in_channel',
            'text': msg_text, 
            'attachments': attachments
        }
        
        r = requests.post(url, json = json_body)
        print('User {} requested top 25 rankings in channel {}'.format(user_name, channel_name))
        pprint(form)

    thread = Thread(target=delayed_response, kwargs={'form': request.form})
    thread.start()
    return '',200


@app.route('/grads', methods = ['GET','POST'])
def grads():
    """Posts information about graduating players. Default response shows all graduating players and the number of teams that had them."""
    """Optional conference parameters can be passed to just post the players for the given conference, which will include duplicates and list the teams."""

    def delayed_response(form):
        """Sends a delatyed response back to the channel the slash command was invoked from."""

        params = form.get('text')
        
        conf_list = [
                'ACC',
                'B10',
                'B12',
                'P12',
                'SEC',
                'N16'
        ]

        conf = params if params in conf_list else None
        rank_type = 'full' if params == 'full' else None
        if conf is None: 
            conf_title = 'All Graduating Players'
            sheets_values = 'Graduating-All!A:E'
        else: 
            conf_title = '{} Graduating Players'.format(conf)
            sheets_values = 'Graduating-{}!A:E'.format(conf)
        
        sheet_id = '18HhjFkZ-Z7Iuafllkd8StHONbhdePcTQeKUTLFo3TrU'
        sheets_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}?key=AIzaSyD59KmdlMqgYpUcakIonO-yjaeg55D60hY'.format(sheet_id, sheets_values)

        # First call the Google Sheets API to retrieve our graduating player data
        r = requests.get(sheets_url)
        raw_json = r.json()
        results = raw_json['values']
        fields = []
         
        col_gap = '    '
        count = 0
        if conf is None:
            for pos,player,teams in results:
                if (count == 0):
                    field_player = {
                            'title': ('{}{}{}'.format('POS'.rjust(3),col_gap,'PLAYER'.ljust(24))),
                            'short': 'true'
                    }
                    field_count = {
                            'title': '# TEAMS',
                            'short': 'true'
                    }
                else:
                    field_player = {
                            'value': ('`{}`{}{}'.format(pos.rjust(2),col_gap,player.ljust(24))),
                            'short': 'true'
                    }
                    field_count = {
                            'value': teams,
                            'short': 'true'
                    }
                fields.append(field_player)
                fields.append(field_count)
                count += 1
        else:
            for conference,div,team,pos,player in results:
                if (count == 0):
                    field_team = {
                            'title': 'TEAM',
                            'short': 'true'
                    }
                    field_player = {
                            'title': ('{}{}{}'.format('POS'.rjust(3),col_gap,'PLAYER'.ljust(24))),
                            'short': 'true'
                    }
                else:
                    field_team = {
                            'value': team,
                            'short': 'true',
                    }
                    field_player = {
                            'value': ('`{}`{}{}'.format(pos.rjust(2),col_gap,player.ljust(24))),
                            'short': 'true'
                    }
                fields.append(field_team)
                fields.append(field_player)
                count += 1
         
        title_text = ':ncff: {}'.format(conf_title)
        attachments = [
            {
                'fallback': ':ncff: Graduating Players',
                'title': title_text,
                'fields': fields,
                'mrkdwn_in': ['fields']
            }
        ]
        
        url = form.get('response_url')
        user_id = form.get('user_id')
        user_name = form.get('user_name')
        channel_name = form.get('channel_name')

        msg_text = '<@{}>, here you go!'.format(user_id)
        json_body = {
            'response_type': 'in_channel',
            'text': msg_text, 
            'attachments': attachments
        }
        
        r = requests.post(url, json = json_body)
        print('User {} requested report for "{}" in channel {}'.format(user_name, conf_title, channel_name))
        pprint(form)

    thread = Thread(target=delayed_response, kwargs={'form': request.form})
    thread.start()
    return '',200


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
