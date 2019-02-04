import json
import requests

# [START gae_python37_app]
from flask import Flask, Response, request, jsonify
from pprint import pprint
from threading import Thread

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


def conf_list():
    """Returns a list of valid conference abbreviations."""
    return ['ACC', 'B10', 'B12', 'P12', 'SEC', 'N16']


def pos_list():
    """Returns a list of valid positions"""
    return ['QB', 'RB', 'TE', 'WR']


@app.route('/subscribed_event', methods=['GET', 'POST'])
def subscribed_event():
    """Receives and responds to various event subscriptions"""
    pprint(request)
    raw_json = request.json
    form = json.dumps(raw_json)

    pprint(form)
    pprint(raw_json)

    event_type = form.get('type')

    print("Received event type {}. Challenge = {}".
          format(event_type, form.get('challenge')))
    if event_type == 'url_verification':
        """This is a verification event that we need to respond to with 
        the provided challenge."""
        challenge = form.get('challenge')
        return challenge, 200


@app.route('/carousel', methods=['GET', 'POST'])
def carousel():
    """Run the coach carousel"""

    def delayed_response(form):
        """Sends a delayed response back to the channel the slash command
        was invoked from."""

        sheet_id = '1lV8oDBBOzIgWuQKA_HGFbn0GPBgK0UqR812MMpQTuvo'
        sheets_values = 'Form Responses 1!C:U'
        sheets_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}?key=AIzaSyD59KmdlMqgYpUcakIonO-yjaeg55D60hY'.format(
                sheet_id, sheets_values)

        r = requests.get(sheets_url)
        raw_json = r.json()
        results = raw_json['values']

        pprint(results)

    thread = Thread(target=delayed_response, kwargs={'form': request.form})
    thread.start()
    return '', 200


@app.route('/top25', methods=['GET', 'POST'])
def top25():
    """Posts top 25 rankings"""

    def delayed_response(form):
        """Sends a delayed response back to the channel the slash command
        was invoked from."""

        params = form.get('text')
        rank_type = 'full' if params == 'full' else None
        if rank_type is None:
            rank_title = 'TOP 25'
            sheets_values = 'Top 25!A1:G26'
        else:
            rank_title = 'FULL'
            sheets_values = 'Full Rankings!A1:G87'

        sheet_id = '18HhjFkZ-Z7Iuafllkd8StHONbhdePcTQeKUTLFo3TrU'
        sheets_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}?key=AIzaSyD59KmdlMqgYpUcakIonO-yjaeg55D60hY'.format(
                sheet_id, sheets_values)

        # First call the Google Sheets API to retrieve our Top 25 rankings data
        r = requests.get(sheets_url)
        raw_json = r.json()
        results = raw_json['values']
        fields = []

        count = 0
        for rank, team, abbrv, record, score, delta, logo in results:
            if count == 0:
                field_rank = {
                    'title': ('{} {}'.format('RK'.ljust(11), 'TEAM'.ljust(24))),
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
                    'value': ('{} {} {}'.format(
                            bold_rank.rjust(10),
                            logo,
                            abbrv_display
                    )),
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

        r = requests.post(url, json=json_body)
        print('User {} requested top 25 rankings in channel {}'.
              format(user_name, channel_name))
        pprint(form)

    thread = Thread(target=delayed_response, kwargs={'form': request.form})
    thread.start()
    return '', 200


@app.route('/grads', methods=['GET', 'POST'])
def grads():
    """Posts information about graduating players. Default response shows
    all graduating players and the number of teams that had them."""
    """Optional conference parameters can be passed to just post the players for 
    the given conference, which will include duplicates and list the teams."""

    def delayed_response(form):
        """Sends a delayed response back to the channel the slash command
        was invoked from."""

        params = form.get('text')
        uparams = params.upper() if params is not None else None

        conf = uparams if uparams in conf_list() else None
        if conf is None:
            conf_title = 'All Graduating Players'
            sheets_values = 'Graduating-All!A:E'
        else:
            conf_title = '{} Graduating Players'.format(conf)
            sheets_values = 'Graduating-{}!A:F'.format(conf)

        sheet_id = '18HhjFkZ-Z7Iuafllkd8StHONbhdePcTQeKUTLFo3TrU'
        sheets_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}?key=AIzaSyD59KmdlMqgYpUcakIonO-yjaeg55D60hY'.format(
                sheet_id, sheets_values)

        # First call the Google Sheets API to retrieve our graduating player data
        r = requests.get(sheets_url)
        raw_json = r.json()
        results = raw_json['values']
        fields = []

        col_gap = '    '
        count = 0
        if conf is None:
            for pos, player, teams in results:
                if count == 0:
                    field_player = {
                        'title': ('{}{}{}'.format(
                                'POS'.rjust(3),
                                col_gap,
                                'PLAYER'.ljust(24)
                        )),
                        'short': 'true'
                    }
                    field_count = {
                        'title': '# TEAMS',
                        'short': 'true'
                    }
                else:
                    field_player = {
                        'value': ('`{}`{}{}'.format(
                                pos.rjust(2),
                                col_gap,
                                player.ljust(24)
                        )),
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
            for conference, div, logo, team, pos, player in results:
                if count == 0:
                    field_team = {
                        'title': 'TEAM',
                        'short': 'true'
                    }
                    field_player = {
                        'title': ('{}{}{}'.format(
                                'POS'.rjust(3),
                                col_gap,
                                'PLAYER'.ljust(24)
                        )),
                        'short': 'true'
                    }
                else:
                    field_team = {
                        'value': '{} {}'.format(logo, team),
                        'short': 'true',
                    }
                    field_player = {
                        'value': ('`{}`{}{}'.format(
                                pos.rjust(2),
                                col_gap,
                                player.ljust(24)
                        )),
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

        r = requests.post(url, json=json_body)
        print('User {} requested report for "{}" in channel {}'.
              format(user_name, conf_title, channel_name))
        pprint(form)

    thread = Thread(target=delayed_response, kwargs={'form': request.form})
    thread.start()
    return '', 200


@app.route('/topstarters', methods=['GET', 'POST'])
def top_starters():
    """Returns the top starters from a given conference at a given position,
    based on career points while starting."""

    def delayed_response(form):
        """Sends a delayed response to the channel the slash command
        was invoked from."""

        raw_params = form.get('text')
        params = raw_params.split()

        url = form.get('response_url')
        user_id = form.get('user_id')
        user_name = form.get('user_name')
        channel_name = form.get('channel_name')

        if len(params) != 2 or params[0].upper() not in conf_list() or params[
            1].upper() not in pos_list():
            msg_text = 'Invalid usage: `/topstarters {}`. Please provide the conference and position group, e.g. `/topstarters ACC QB`'.format(
                    raw_params)
            json_body = {
                'response_type': 'ephemeral',
                'text': msg_text
            }

            r = requests.post(url, json=json_body)
            print('User {} requested report for {} in channel {}'.
                  format(user_name, 'Top Starters', channel_name))
            pprint(form)
            return

        PLAYER_LIMIT = 20

        input_conf = params[0].upper()
        input_pos = params[1].upper()

        report_title = '{} Top {} Starters'.format(input_conf, input_pos)
        sheets_values = '{}-{}!A1:G{}'.format(
                input_conf,
                input_pos,
                PLAYER_LIMIT
        )

        sheet_id = '1P8HcDL-aPLeJktgp7CDJqbw-sj-ws9UwifDmXcw56K8'
        sheets_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}?key=AIzaSyD59KmdlMqgYpUcakIonO-yjaeg55D60hY'.format(
                sheet_id, sheets_values)

        # First call the Google Sheets API to retrieve graduating player data
        r = requests.get(sheets_url)
        raw_json = r.json()
        results = raw_json['values']
        fields = []

        col_gap = '    '
        count = 0
        for rank, player, logo, abbrv, pos, pts, gs in results:
            if count == 0:
                field_player = {
                    'title': ('{}       {}'.format('RK', 'PLAYER')),
                    'short': 'true'
                }

                field_stats = {
                    'title': '{}    {}    {}'.format('TM', 'GS', 'POINTS'),
                    'short': 'true'
                }
            else:
                field_player = {
                    'value': ('`#{:>2}`    {}'.format(rank, player)),
                    'short': 'true'
                }
                field_stats = {
                    'value': ('{}    `{:>2}`    {}'.format(logo, gs, pts)),
                    'short': 'true'
                }
            fields.append(field_player)
            fields.append(field_stats)
            count += 1

        title_text = ':ncff: {}'.format(report_title)
        attachments = [
            {
                'fallback': ':ncff: Top  Players',
                'title': title_text,
                'fields': fields,
                'mrkdwn_in': ['fields']
            }
        ]

        msg_text = '<@{}>, here you go!'.format(user_id)
        json_body = {
            'response_type': 'in_channel',
            'text': msg_text,
            'attachments': attachments
        }

        r = requests.post(url, json=json_body)
        print('User {} requested report for "{}" in channel {}'.
              format(user_name, report_title, channel_name))
        pprint(form)

    thread = Thread(target=delayed_response, kwargs={'form': request.form})
    thread.start()

    return '', 200


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
