import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

# Placeholder data
recommendations_table = pd.DataFrame({
    'Action': ['Action Movie 1', 'Action Movie 2', 'Action Movie 3', 'Action Movie 4', 'Action Movie 5',
               'Action Movie 6', 'Action Movie 7', 'Action Movie 8', 'Action Movie 9', 'Action Movie 10'],
    'Comedy': ['Comedy Movie 1', 'Comedy Movie 2', 'Comedy Movie 3', 'Comedy Movie 4', 'Comedy Movie 5',
               'Comedy Movie 6', 'Comedy Movie 7', 'Comedy Movie 8', 'Comedy Movie 9', 'Comedy Movie 10'],
})

sample_movies = [
    {'title': 'Toy Story (1995)', 'id': 'toy-story'},
    {'title': 'Jumanji (1995)', 'id': 'jumanji'},
    {'title': 'Heat (1995)', 'id': 'heat'},
    {'title': 'GoldenEye (1995)', 'id': 'goldeneye'},
    {'title': 'Sabrina (1995)', 'id': 'sabrina'},
    {'title': 'Tom and Huck (1995)', 'id': 'tom-and-huck'},
    {'title': 'Sudden Death (1995)', 'id': 'sudden-death'},
    {'title': 'Grumpier Old Men (1995)', 'id': 'grumpier-old-men'},
    {'title': 'Waiting to Exhale (1995)', 'id': 'waiting-to-exhale'},
    {'title': 'Father of the Bride Part II (1995)', 'id': 'father-of-the-bride-part-ii'},
    {'title': 'Pocahontas (1995)', 'id': 'pocahontas'},
    {'title': 'Apollo 13 (1995)', 'id': 'apollo-13'},
    {'title': 'Casper (1995)', 'id': 'casper'},
    {'title': 'Batman Forever (1995)', 'id': 'batman-forever'},
    {'title': 'Seven (1995)', 'id': 'seven'},
]

# Assuming this is our Item-Based Collaborative Filtering function that returns recommendations
def myIBCF(ratings):
    return [{'title': f'Recommended Movie {i+1}', 'rank': i+1} for i in range(10)]

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css"
], suppress_callback_exceptions=True)
server = app.server

# Define the layout of the app
app.layout = html.Div([
    # Header
    dbc.NavbarSimple(
        brand="Movie Recommender",
        brand_href="#",
        color="primary",
        dark=True,
        fluid=True,
        className="mb-0"
    ),
    # Main content with sidebar navigation
    dbc.Row([
        # Sidebar with black background and full page height
        dbc.Col(
            dbc.Nav(
                [
                    # Using icons with text for the links
                    dbc.NavLink(
                        [html.I(className="bi bi-film"), " Recommender by Genre"],
                        href="/",
                        active="exact",
                        className="nav-link",
                        id="nav-genre",
                        style={'color': 'white'}
                    ),
                    dbc.NavLink(
                        [html.I(className="bi bi-star-fill"), " Recommender by Rating"],
                        href="/rating",
                        active="exact",
                        className="nav-link",
                        id="nav-rating",
                        style={'color': 'white'}
                    ),
                ],
                vertical=True,
                pills=True,
                className="bg-dark vh-100 d-flex flex-column",
            ),
            width=2,
            style={'padding': '0', 'margin': '0'},
            className="px-0"
        ),
        # Page content
        dbc.Col(
            [
                dcc.Location(id='url', refresh=False),
                html.Div(id='page-content', style={'overflow-y': 'auto', 'height': 'calc(100vh - 75px)'})
            ],
            width=10,
            className="px-0"
        ),
    ], className="g-0", style={'height': '100vh'}),
], style={'height': '100vh', 'overflow': 'hidden'})

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def render_page_content(pathname):
    # Content for the "Recommender by Rating" page
    if pathname == "/rating":
        # Create the movie rating cards inside a scrollable div
        movie_rating_cards = html.Div(
            [
                dbc.Card(
                    [
                        dbc.CardHeader("Step 1: Rate as many movies as possible"),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Card(
                                                [
                                                    html.H5(movie['title'], className='card-title'),
                                                    dcc.Slider(
                                                        id=movie['id'],
                                                        min=0, max=5, step=1,
                                                        value=0,
                                                        marks={i: str(i) for i in range(6)}
                                                    )
                                                ],
                                                body=True,
                                                className="mb-4"
                                            ),
                                            width=4
                                        ) for movie in sample_movies
                                    ],
                                    className="mb-4"
                                )
                            ],
                            style={'overflowY': 'scroll', 'height': '500px'} 
                        )
                    ],
                    className="mt-3",
                )
            ]
        )
        # Rest of the layout for "Recommender by Rating" page
        recommendation_section = dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Step 2: Discover movies you might like"),
                    dbc.CardBody([
                        dbc.Button("Click here to get your recommendations", id="get-recommendations-rating", color="primary")
                    ])
                ]),
                width=12
            )
        ], className="mt-4")

        recommendations = dbc.Row([
                dbc.Col(html.Div(id='recommendations-output-rating'), width=12)
            ], className="mt-4")

        # Combine all UI elements into the container
        return dbc.Container([movie_rating_cards, recommendation_section, recommendations])
    else:
        # Content for the "Recommender by Genre" page
        return dbc.Container([
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Step 1: Select your favorite genre"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id='genre-dropdown',
                                options=[{'label': genre, 'value': genre} for genre in recommendations_table.columns],
                                placeholder='Select a genre',
                            )
                        ])
                    ]),
                    width=12
                ),
            ], className="mt-3"),  
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Step 2: Discover movies you might like"),
                        dbc.CardBody([
                            dbc.Button("Click here to get your recommendations", id="get-recommendations", color="primary")
                        ])
                    ]),
                    width=12
                ),
            ], className="mt-4"),  
            dbc.Row([
                dbc.Col(html.Div(id='recommendations-output'), width=12)
            ], className="mt-4")
        ])

@app.callback(
    Output('recommendations-output', 'children'),
    [Input('get-recommendations', 'n_clicks')],
    [State('genre-dropdown', 'value')]
)
def display_recommendations(n_clicks, genre):
    if n_clicks and genre in recommendations_table.columns:
        recommendations = recommendations_table[genre].tolist()
        return dbc.ListGroup([dbc.ListGroupItem(movie) for movie in recommendations])
    return ""

@app.callback(
    Output('recommendations-output-rating', 'children'),
    [Input('get-recommendations-rating', 'n_clicks')],
    [State(movie['id'], 'value') for movie in sample_movies]
)
def display_recommendations_based_on_ratings(n_clicks, *ratings):
    if n_clicks:
        movie_ratings = {movie['title']: rating for movie, rating in zip(sample_movies, ratings)}
        recommendations = myIBCF(movie_ratings)

        # Create a grid of movie cards that are responsive to the viewport
        card_content = []
        for rec in recommendations:
            card = dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H5(f"Rank {rec['rank']}", className="card-title"),
                            html.P(rec['title'], className="card-text"),
                        ]
                    ),
                ],
            )
            # Cards will take up 6 columns on small screens, 4 columns on medium screens, and 3 columns on large screens
            card_content.append(dbc.Col(card, width=12, sm=6, md=4, lg=3, xl=3))

        return dbc.Row(card_content, className="g-4")  

    return ""

# Callback for dynamically setting the active style
@app.callback(
    [Output("nav-genre", "className"), Output("nav-rating", "className")],
    [Input('url', 'pathname')]
)
def update_nav_active_styles(pathname):
    # The base style
    base_class = "nav-link"
    # The active class
    active_class = "nav-link active"
    
    # Depending on the current pathname, set the active class to the appropriate link
    return [
        active_class if pathname == "/" else base_class,
        active_class if pathname == "/rating" else base_class
    ]

# Additional callback to set the style attribute conditionally
@app.callback(
    [Output("nav-genre", "style"), Output("nav-rating", "style")],
    [Input('url', 'pathname')]
)
def set_active_link_style(pathname):
    active_style = {'color': 'white', 'background-color': '#2c3238'}
    inactive_style = {'color': 'white', 'background-color': 'transparent'}
    return [
        active_style if pathname == "/" else inactive_style,
        active_style if pathname == "/rating" else inactive_style
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
