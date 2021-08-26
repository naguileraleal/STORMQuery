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


navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src='./assets/images/aphos_logo.png', height="30px")),
                    dbc.Col(dbc.NavbarBrand("STOrM", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/",
        ),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavLink(
                        "Consulta de Datos",
                        href="/",
                        active="exact",
                        className='nav-link'
                        ),
                    dbc.NavLink(
                        "Aphos",
                        href="http://aphos.com.uy/",
                        active="exact",
                        className='nav-link'
                        )
                ],
                vertical=True,
                pills=False,
                fill=False,
                className='navbar-nav',
                horizontal='start'
            ),
            id="navbar-collapse",
            navbar=True,
            is_open=False
        ),
    ],
    
    className='navbar navbar-expand-lg navbar-light bg-light'
)


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

    html.Div(style={
        'textAlign': 'left',
        'color': colors['text']
    }, children=[
        html.Div(
            children=[
                navbar,
                html.H2(
                    children='Consulta de datos',
                    id='app-subheader-label',
                    hidden=True
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
                    className='datepicker dash-bootstrap',
                    min_date_allowed=date(2010, 1, 1),
                    max_date_allowed=date.today(),
                    initial_visible_month=date.today()
                ),
                html.Br(),
                dbc.Button(
                    'Generar Gráfico',
                    id='generar-consulta-button',
                    n_clicks=0,
                    className='btn btn-outline-info'
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

    duracionAlertas = 7000 # Milisegundos

    hidden = True

    logging.debug('Generar consulta n_clicks: {} ultimoNClicks: {}'.format(n_clicks,ultimoNClicks))

    if (ultimoNClicks != n_clicks and n_clicks > 0):
        ultimoNClicks = n_clicks
        ok = False
        ok = (muestra != None) and (subMuestra != None)
        if (ok):
            res = query_sin_lector(
                    muestra,
                    subMuestra,
                    fechaInicio,
                    fechaFin,
                    plot
                )
            
            logging.debug('plot: {}'.format(plot))

            if res == CodigosError.NO_HAY_DATOS:
                alertasContainerChildren.append(
                    dbc.Alert(
                        'No hay datos para la muestra {0}:{1} en el rango de fechas {2} -> {3}'.format(
                            muestra,
                            subMuestra,
                            fechaInicio,
                            fechaFin
                        ),
                        color='warning',
                        duration=duracionAlertas,
                        className='alerta',
                        dismissable=True
                    )
                )
            elif res == CodigosError.NO_EXISTE_MUESTRA:
                alertasContainerChildren.append(
                    dbc.Alert(
                        'No existe una muestra con los codigos {0}:{1}'.format(
                            muestra,
                            subMuestra
                        ),
                        color='danger',
                        className='alerta',
                        dismissable=True
                    )
                )

            elif plot != None:
                
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
                        duration=duracionAlertas,
                        className='alerta',
                        dismissable=True
                    )
                )
            if (subMuestra == None):
                alertasContainerChildren.append(
                    dbc.Alert(
                        'Codigo de submuestra inválido',
                        color='danger',
                        duration=duracionAlertas,
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