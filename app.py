import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import copy

# Read the System 1 output CSV file
sys1_df = pd.read_csv('system_1_output.csv')

# Create a dictionary to hold genres and their movies
genre_dict = {}

for index, row in sys1_df.iterrows():
    genre = row['Genres']
    movie = row['Title']
    
    if genre in genre_dict:
        genre_dict[genre].append(movie)
    else:
        genre_dict[genre] = [movie]

# Creating a DataFrame with genres as columns and their movies as values
recommendations_table = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in genre_dict.items()]))

#Read Odered Movie ID and Title file
ordered_id_title_df = pd.read_csv('ordered_id_title_mappings.csv')
movies = []
for index, row in ordered_id_title_df.iterrows():
    if pd.notna(row['Title']):
        title = row['Title']
        movie_id = row['MovieID']  # Using 'MovieID' as 'id'
        movies.append({'title': title, 'id': movie_id})

# Assuming this is our Item-Based Collaborative Filtering function that returns recommendations
def myIBCF(ratings):
    # First, create a mapping from Title to MovieID using ordered_df
    title_to_id_map = ordered_id_title_df.set_index('Title')['MovieID'].to_dict()

    # Mapping titles to MovieIDs in the provided dictionary
    movie_ratings_mapped = {title_to_id_map.get(title, 'Unknown'): rating for title, rating in ratings.items()}

    # Creating the Series
    ratings_series = pd.Series(movie_ratings_mapped, index=ordered_id_title_df['MovieID'])

    # Replace 0 with NaN
    vector = ratings_series.replace(0, np.nan)

    # Reading the S matrix
    dataframeS = pd.read_csv('S3df.csv', index_col=0)

    #The maximum column (movie) number
    n_v = vector.shape[0]
    vector_copy = vector.copy(deep=True)
    vector_new = pd.Series(np.nan, index=vector.index)
    
    # Finding the row numbers where values are not NaN
    non_nan_rows = np.where(~np.isnan(vector_copy))[0]
    
    #Calculating Movie scores
    dataS = copy.deepcopy(dataframeS)
    dataS.fillna(0, inplace=True)
    for vl in range(n_v):
        if np.isnan(vector_copy[vl]):
            denominator = (dataS.loc[dataS.columns[vl], dataS.columns[non_nan_rows]]).sum()            
            numerator = np.dot(dataS.loc[dataS.columns[vl], dataS.columns[non_nan_rows]], vector_copy[non_nan_rows])
            prediction = numerator / denominator
            vector_new[vl] = prediction
    df_diff_sorted = vector_new.sort_values(ascending=False)
    top_10_diff = df_diff_sorted.head(10)

    # Extracting the row index (MovieID) from the Series
    movie_ids = top_10_diff.index

    # Maping the row index (MovieID) back to title using ordered_df
    id_to_title_map = ordered_id_title_df.set_index('MovieID')['Title'].to_dict()

    # Creating a dictionary with the title and rank
    ranked_movies = [{'title': id_to_title_map.get(movie_id, 'Unknown'), 'rank': rank+1} for rank, movie_id in enumerate(movie_ids)]

    return ranked_movies

app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css"
], suppress_callback_exceptions=True)
server = app.server

# Defining the layout of the app
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
        # Creating the movie rating cards inside a scrollable div
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
                                        ) for movie in movies
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

        # Combining all UI elements into the container
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
    [State(movie['id'], 'value') for movie in movies]
)
def display_recommendations_based_on_ratings(n_clicks, *ratings):
    if n_clicks:
        movie_ratings = {movie['title']: rating for movie, rating in zip(movies, ratings)}
        recommendations = myIBCF(movie_ratings)

        # Creating a grid of movie cards that are responsive to the viewport
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
