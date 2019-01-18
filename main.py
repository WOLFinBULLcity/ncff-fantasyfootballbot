
import json
import requests

# [START gae_python37_app]
from flask import Flask


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello NCFF!'

@app.route('/test')
def testing():
    """Return a fifferent HTTP message."""
    return 'This has been a test.'

@app.route('/rcmessage', methods = ['POST'])
def rcmessage():
    """Test sending message to Slack webhook."""
    r = requests.post('https://hooks.slack.com/services/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', json = {'text':'this is a test message.'})
    return 'message sent to slack. '

@app.route('/top25', methods = ['GET','POST'])
def top25():
    """Posts top 25 rankings"""   
    r = requests.get('https://sheets.googleapis.com/v4/spreadsheets/18HhjFkZ-Z7Iuafllkd8StHONbhdePcTQeKUTLFo3TrU/values/A1:G26?key=AIzaSyD59KmdlMqgYpUcakIonO-yjaeg55D60hY')
    raw_json = r.json()

    rankings = raw_json['values']

    message_body = ""
    fields = []

    count = 0
    for rank,team,abbrv,record,score,delta,logo in rankings:
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
            bold_rank = '#' + rk_space + rank + ''
            team_display = logo + ' ' + abbrv.ljust(6)
            abbrv_display = abbrv.ljust(6)
            field_rank = {
                    'value': ('{} {} {}'.format(bold_rank.ljust(10),logo,abbrv_display)),
                    'short': 'true'
            }
            field_trend = {
                    'value': ('{}'.format(delta)),
                    'short': 'true'
            }
        fields.append(field_rank)
        fields.append(field_trend)
        count += 1


    attachments = [
            {
                'fallback': ':ncff: Top 25 Rankings',
                'title': ':ncff: TOP 25 RANKINGS',
                'title_link': 'https://datastudio.google.com/open/1pUtKEQuveWvwqUMRloALhM2AovPVZJGp',
                'fields': fields
            }
    ]

    r = requests.post('https://hooks.slack.com/services/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', json = {'text': '', 'attachments': attachments})
    return 'rankings posted'

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
