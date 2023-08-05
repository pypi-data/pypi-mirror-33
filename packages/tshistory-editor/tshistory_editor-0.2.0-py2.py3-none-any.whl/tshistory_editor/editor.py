import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from flask_caching import Cache
import plotly.graph_objs as go
import pandas as pd
import numpy as np

from urllib.parse import urlparse, parse_qs

from tshistory.util import tojson, fromjson
from tshistory.tsio import TimeSerie as Tsh
from data_hub.tsio import TimeSerie



def serie_names(engine):
    sql = 'select seriename from tsh.registry order by seriename'
    return [name for name, in engine.execute(sql).fetchall()]


def unpack_dates(graphdata):
    fromdate = None
    todate = None
    if graphdata and 'xaxis.range[0]' in graphdata:
        fromdate = pd.to_datetime(graphdata['xaxis.range[0]'])
    if graphdata and 'xaxis.range[1]' in graphdata:
        todate = pd.to_datetime(graphdata['xaxis.range[1]'])
    return fromdate, todate


def editor(app, engine,
           url_base_pathname='/tseditor/',
           request_pathname_prefix='/',
           additional_info=None):

    if request_pathname_prefix != '/':
        request_pathname_prefix_adv = request_pathname_prefix + url_base_pathname
    else:
        request_pathname_prefix_adv = request_pathname_prefix

    dashboard = dash.Dash('tsview',
                          server=app,
                          url_base_pathname=url_base_pathname,
                          request_pathname_prefix= request_pathname_prefix_adv)

    dashboard.css.append_css({
        "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
    })

    dashboard.config['suppress_callback_exceptions'] = True
    if request_pathname_prefix != '/':
        dashboard.config.requests_pathname_prefix = request_pathname_prefix_adv
    cache = Cache(dashboard.server, config={'CACHE_TYPE': 'simple'})
    cache.init_app(dashboard.server)

    dashboard.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(dcc.Dropdown(id='ts_selector',
                 value=None,
                 # options=formated_names
                ),
                style={'display': 'none'}),
        html.Div(id='dropdown-container', style={'width': '50%', 'float': 'right'}),
        html.Div(html.Button(id='tse_refresh_snapshot', n_clicks=0, children='refresh graph')),
        dcc.Graph(id='ts_snapshot'),
        html.Div(html.Button(id='refresh_data', n_clicks=0, children='Refresh data'), style={'display': 'none'}),
        html.Div(id='rev_id', style={'display': 'none'}),
        html.Div(id='diff', style={'display': 'none'}),
        html.Div(id='tse_var_id_serie', style={'display': 'none'}),
        html.Div(id='button-container',
                 style={'float': 'left'}
        ),
        html.Div(
            html.Button(id='send_diff', n_clicks=0, children='Save diff'),
            style={'width': '50%', 'float': 'right'}
        ),
        html.Div(dt.DataTable(id='table',  rows=[{}], row_selectable=True), style={'display': 'none'}),
        html.Div(id='table_container', className='six columns',
                 style={'float': 'left'}),
        html.Div([html.Div(id='info'),
                  html.Br(),
                  html.Br(),
                  html.Div(id='display_diff'),
                  html.Div(id='log_result'),
                  ],
                 style={'float': 'right'},),

    ])

    @dashboard.callback(dash.dependencies.Output('dropdown-container', 'children'),
                        [dash.dependencies.Input('url', 'href')])
    def adaptable_dropdown(href):
        if href is None:
            return dcc.Dropdown(id='ts_selector')
        query = parse_qs(urlparse(href).query)
        if not len(query):
            initial_value = None
        else:
            initial_value = query['name'][0] if 'name' in query else None
        all_names = serie_names(engine)
        formated_names = [{'label': name, 'value': name} for name in all_names]
        dropdown = dcc.Dropdown(
            id='ts_selector',
            options=formated_names,
            value=initial_value
            ),
        return dropdown

    @dashboard.callback(dash.dependencies.Output('tse_var_id_serie', 'children'),
                        [dash.dependencies.Input('url', 'href'),
                        dash.dependencies.Input('ts_selector', 'value')])
    def ts_div_id_serie(href, dd_value):
        if href is None:
            return {
                'name': '', #formated_names[0]['value'],
                'startdate': None,
                'enddate': None,
                'author': None
            }

        startdate = None
        enddate = None
        author = None
        query = parse_qs(urlparse(href).query)

        if not len(query):
            id_serie = '' #    formated_names[0]['value']
        else:
            id_serie = query['name'][0] if 'name' in query else None
            startdate = query['startdate'][0] if 'startdate' in query else None
            enddate = query['enddate'][0]  if 'enddate' in query else None
            author = query['author'][0] if 'author' in query else None

        if dd_value is not None and dd_value != id_serie:
            # i.e. the user has changed the selected series
            id_serie = dd_value

        return json.dumps({
            'name': id_serie,
            'startdate': startdate,
            'enddate': enddate,
            'author': author
        })

    @dashboard.callback(dash.dependencies.Output('info', 'children'),
                        [dash.dependencies.Input('tse_var_id_serie', 'children')])
    def display_info(info_serie):
        if info_serie is None:
            return ''
        info_serie = json.loads(info_serie)
        id_serie = info_serie['name']
        if additional_info is not None:
            info_metadata = additional_info(engine, id_serie)
            if not info_metadata:
                return ''
            data = list(info_metadata.items())
            return [html.Tr([html.Td(elt) for elt in tuple]) for tuple in data]

    @dashboard.callback(dash.dependencies.Output('button-container', 'children'),
                        [dash.dependencies.Input('tse_var_id_serie', 'children')])
    def dynamic_button(_):
        return  html.Button(id='refresh_data', n_clicks=0, children='Refresh data'),

    @dashboard.callback(dash.dependencies.Output('ts_snapshot', 'figure'),
                        [dash.dependencies.Input('tse_var_id_serie', 'children'),
                         dash.dependencies.Input('tse_refresh_snapshot', 'n_clicks')])
    def snapshot_display(info_serie, n_clicks):
        if info_serie is None:
            return {'data': [], 'layout': {}}

        info_serie = json.loads(info_serie)
        id_serie = info_serie['name']
        startdate = info_serie['startdate']
        enddate = info_serie['enddate']
        if startdate and enddate:
            range = [pd.to_datetime(startdate), pd.to_datetime(enddate)]
        else:
            range = 'autorange'

        tsh = TimeSerie()
        if not tsh.exists(engine, id_serie):
            return  {'data': [], 'layout': {}}

        ts = tsh.get(engine, id_serie)
        trace = [
            go.Scatter(
            x=ts.index,
            y=ts.values,
            name= id_serie,
            mode='lines',
            line={'color': ('rgb(255, 127, 80)')},)
        ]
        layout = go.Layout({'yaxis': {'fixedrange' : True},
                            'xaxis': {'range': range},
                            'showlegend': False,
                            'height': 300,
                            'margin': go.Margin(b=30, t=0),
                            })
        return {
            'data': trace,
            'layout': layout
        }

    @dashboard.callback(dash.dependencies.Output('table_container', 'children'),
                        [dash.dependencies.Input('refresh_data', 'n_clicks')],
                        [dash.dependencies.State('tse_var_id_serie', 'children'),
                         dash.dependencies.State('ts_snapshot', 'relayoutData')])
    def dynamic_table(n_clicks, info_serie, graphdata):
        if not info_serie:
            return dt.DataTable(id='table', rows=[{}], columns=['Index', 'Value'], row_selectable=True)

        info_serie = json.loads(info_serie)
        id_serie = info_serie['name']

        if graphdata :
            fromdate, todate = unpack_dates(graphdata)
        else:
            fromdate = info_serie['startdate']
            todate = info_serie['enddate']

        if info_serie['startdate'] is None and info_serie['enddate'] is None and n_clicks==0:
            # i.e. the serie is not bounded by the url parameters
            # we want that the user bound it before showing the data
            return  dt.DataTable(id='table', rows=[{}], columns=['Index', 'Value'], row_selectable=True)

        tsh = TimeSerie()
        ts, marker = tsh.get_ts_marker(engine, id_serie)
        if len(ts) != len(marker): # Some na have been inserted
            new_ts = pd.Series(index = marker.index)
            new_ts[ts.index] = ts
            ts = new_ts
        if fromdate and todate:
            mask = (ts.index >= fromdate) & (ts.index <= todate)
            ts = ts[mask]
            marker = marker[mask]
        idx_marker = np.arange(len(marker))[marker.values]
        htmldiv = dt.DataTable(
            rows=[{'Index':elt[0], 'Value': elt[1]}
                  for elt in ts.to_frame().itertuples()],
            id='table',
            columns=['Index', 'Value'],
            editable=True,
            max_rows_in_viewport=30,
            row_selectable=True,
            selected_row_indices = idx_marker.tolist()
        )
        return  htmldiv

    @dashboard.callback(dash.dependencies.Output('rev_id', 'children'),
                        [dash.dependencies.Input('refresh_data', 'n_clicks')],
                        [dash.dependencies.State('tse_var_id_serie', 'children')])
    def store_id_rev(n_clicks, info_serie):
        if not info_serie:
            return ''

        id_serie = json.loads(info_serie)['name']
        tsh = Tsh()
        if not tsh.exists(engine, id_serie):
            return ''

        rev_id = tsh.last_id(engine, id_serie)
        return rev_id

    @dashboard.callback(dash.dependencies.Output('diff', 'children'),
                        [dash.dependencies.Input('table', 'rows')],
                        [dash.dependencies.State('tse_var_id_serie', 'children')])
    def calculate_diff(rows, info_serie):
        tso = TimeSerie()
        df_modif = pd.DataFrame(rows)
        info_diff = {'msg': None, 'diff': None}
        if not info_serie or rows == [{}]:
            return json.dumps(info_diff)

        id_serie = json.loads(info_serie)['name']
        try:
            ts_modif = df_modif.set_index('Index')['Value']
            ts_modif.index = pd.to_datetime(ts_modif.index)
        except Exception as error:
            return json.dumps({'msg':'Error :' + str(error), 'diff': None})
        try:
            ts_modif = pd.to_numeric(ts_modif)
        except:
            pass

        ts_base = tso.get(engine, id_serie)
        try:
            diff = tso.diff(ts_base, ts_modif)
            info_diff['diff'] = diff
        except Exception as error:
            return json.dumps({'msg':'Error :' + str(error), 'diff': None})

        if not len(diff):
            return json.dumps({'msg': 'No differences', 'diff': None})
        return json.dumps({'msg': None, 'diff': tojson(diff)})

    @dashboard.callback(dash.dependencies.Output('display_diff', 'children'),
                        [dash.dependencies.Input('diff', 'children')])
    def display_diff(info_diff):
        if not info_diff:
            return ''

        info_diff = json.loads(info_diff)
        if info_diff['msg']:
            return info_diff['msg']

        if info_diff['diff']:
            tudiff = fromjson(info_diff['diff'], 'name').to_frame().itertuples()
            return [html.Tr('{} : {}'.format(*elt)) for elt in tudiff]

        # might be redundant with 1 branch
        return ''

    @dashboard.callback(dash.dependencies.Output('log_result', 'children'),
                        [dash.dependencies.Input('send_diff', 'n_clicks'),],
                         [dash.dependencies.State('tse_var_id_serie', 'children'),
                         dash.dependencies.State('diff', 'children'),
                         dash.dependencies.State('rev_id', 'children')
                         ])
    def insert_diff(n_clicks, info_serie, info_diff, rev_id_stored):
        if not info_serie:
            return ''

        id_serie = json.loads(info_serie)['name']
        author = json.loads(info_serie)['author']
        author = 'webui' if author is None else author
        if info_diff:
            info_diff = json.loads(info_diff)
        if info_diff['diff'] is None:
            return ''

        ts = fromjson(info_diff['diff'], tsname=id_serie)
        tso = TimeSerie()
        rev_id = tso.last_id(engine, id_serie)
        if str(rev_id) != str(rev_id_stored):
            return 'Updating aborted: version conflict! Please reload the data and redo the manual edition'

        try:
            diff = tso.insert(engine, ts, id_serie, author, dict(manual=True))
        except Exception as error:
            return error
        if len(diff):
            msg = 'Series {} has been succefuly updated by {} with {} new values'.format(id_serie, author, len(diff))
        else:
            msg = 'No changes'
        return msg
