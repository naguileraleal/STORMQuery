import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_core_components as dcc
from dash_html_components.Div import Div
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objs as go
from datetime import date

from funciones.stormLib import *
from plotly.offline.offline import plot


# Variables Globales
ultimoNClicks = 0

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

external_stylesheets = [
    'https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/flatly/bootstrap.min.css'
    ]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

    html.Div(style={
        'textAlign': 'left',
        'color': colors['text']
    }, children=[
        html.Div(
            children=[
                html.H1(
                    children='STOrM',
                    id='app-header-label'
                ),

                html.H2(
                    children='Consulta de datos',
                    id='app-subheader-label'
                )
        ],
        id='header-container'
        ),

        html.Div(
            children=[
                html.Label(
                    'Muestra',
                    className='label',
                    id='muestra-label'
                ),
                dcc.Input(
                    type='number',
                    className='text-input',
                    id='codigo-muestra-input',
                    placeholder=''
                ),
                html.Label(
                    'Submuestra',
                    className='label',
                    id='submuestra-label'
                ),
                dcc.Input(
                    type='number',
                    className='text-input',
                    id='codigo-submuestra-input',
                    placeholder=''
                ),
                html.Label(
                    'Rango de fechas de la consulta',
                    className='label',
                    id='rango-fechas-label'
                ),
                dcc.DatePickerRange(
                    id='rango-fechas-consulta-datepicker',
                    className='datepicker',
                    min_date_allowed=date(2010, 1, 1),
                    max_date_allowed=date.today(),
                    initial_visible_month=date.today()
                ),
                html.Br(),
                dbc.Button(
                    'Generar Gráfico',
                    id='generar-consulta-button',
                    n_clicks=0,
                    className='btn btn-outline-primary'
                )
            ],
            id='inputs-container'
        ),
        html.Div(children=[
            dcc.Graph(
                figure=go.Figure(),
                id='consulta-graph',
                className='dash-bootstrap'
                )
        ],
            id='graph-container',
            hidden=True
        ),
        html.Div(
            id='alertas-container',
            children=[]
        )
    ],
        id='global-container'
    )

])

@app.callback(
    [Output('graph-container', 'children'),
    Output('alertas-container', 'children'),
    Output('graph-container','hidden')
    ],
    [Input('generar-consulta-button', 'n_clicks')],
    [State('codigo-muestra-input', 'value'),
    State('codigo-submuestra-input', 'value'),
    State('rango-fechas-consulta-datepicker', 'start_date'),
    State('rango-fechas-consulta-datepicker', 'end_date'),
    State('graph-container', 'children'),
    State('alertas-container','children')
    ]
)

def callbackGenerarConsulta(
    n_clicks,
    muestra,
    subMuestra,
    fechaInicio,
    fechaFin,
    contenedorGraficaChildren,
    alertasContainerChildren
    ):

    global ultimoNClicks

    plot = go.Figure()

    hidden = True

    logging.debug('Generar consulta n_clicks: {} ultimoNClicks: {}'.format(n_clicks,ultimoNClicks))

    if (ultimoNClicks != n_clicks and n_clicks > 0):
        ultimoNClicks = n_clicks
        ok = False
        ok = (muestra != None) and (subMuestra != None)
        if (ok):
            query_sin_lector(
                muestra,
                subMuestra,
                fechaInicio,
                fechaFin,
                plot
            )
            logging.debug('plot: {}'.format(plot))
            if plot != None:
                
                contenedorGraficaChildren[0] = dcc.Graph(
                    figure=plot,
                    id='consulta-graph'
                    )
                hidden = False
        else:
            if (muestra == None):
                alertasContainerChildren.append(
                    dbc.Alert(
                        'Codigo de muestra inválido',
                        color='danger',
                        className='alerta',
                        dismissable=True
                    )
                )
            if (subMuestra == None):
                alertasContainerChildren.append(
                    dbc.Alert(
                        'Codigo de submuestra inválido',
                        color='danger',
                        className='alerta',
                        dismissable=True
                    )
                )

    return (contenedorGraficaChildren, alertasContainerChildren, hidden)

if __name__ == '__main__':
    logging.basicConfig(
    filename='./log/main-dash-{}.log'.format(
        datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        ),
    level=logging.DEBUG,
    encoding='utf-8',
    format='%(levelname)s: %(filename)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
    )
    app.run_server(port=1111, debug=True)