"""
File:           app.py
Author:         Dibyaranjan Sathua
Created on:     20/02/21, 12:23 am
"""
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from db import DBApi


app = dash.Dash(
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
)


class AppLayout:
    """ Class responsible for app layout """

    def __init__(self):
        self._db_api = DBApi()
        self._potential_deals = []
        self._potential_deals_cols = []
        self._years = []
        self._make_model = {}
        self._action_options = []

    def setup(self):
        """ Setup the app layout """
        self.fetch_from_db()
        # Don't assign to the function output. Assing it to the function object so that whenever we
        # do some changes to layout, it will reflect without server restarting
        app.layout = self.get_root_layout

    def fetch_from_db(self):
        """ Fetch data from db """
        self._potential_deals = DBApi.get_instance().potential_records
        # Add markdown for url
        for data in self._potential_deals:
            data["url"] = f"[Link]({data['url']})"
        self._potential_deals_cols = self._db_api.get_potential_deal_columns()
        self._years = self._db_api.get_unique_years(self._potential_deals)
        self._make_model = self._db_api.get_all_make_models()
        self._action_options = ["Action1", "Action2", "Action3"]

    def get_nav_bar_layout(self):
        """ Nav bar layout """
        save_bar = dbc.Row(
            [
                dbc.Col(
                    dbc.Alert(children="", id="status_alert", color="success",
                              dismissable=True, is_open=False),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Button("Save", id="navbar_save_btn", color="warning", className="ml-2",
                               n_clicks=0),
                    width="auto",
                ),
            ],
            no_gutters=True,
            className="ml-auto flex-nowrap",
            align="center",
        )
        return dbc.Navbar(
            children=[
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            # dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                            dbc.Col(dbc.NavbarBrand("AutoCloud", className="ml-2")),
                        ],
                        align="center",
                        no_gutters=True,
                    ),
                    href="#",
                ),
                save_bar,
            ],
            color="primary",
            dark=True,
            sticky="top",
            className="mb-2"
        )

    def get_year_filter(self, color, classname):
        """ Return year filter """
        return [
            dbc.Button("Year", id="year_filter_btn", color=color, className=classname, n_clicks=0),
            dbc.Collapse(
                dbc.FormGroup(
                    children=[
                        dbc.Checklist(
                            options=[
                                {"label": f"{year[0]} ({year[1]})", "value": year[0]}
                                for year in self._years
                            ],
                            className="ml-4",
                            id="year_actual_filter_options"
                        )
                    ]
                ),
                id="year_filter_options",
                is_open=False
            )
        ]

    def get_make_filter(self, color, classname):
        """ Return make filter """
        return [
            dbc.Button("Make", id="make_filter_btn", color=color, className=classname, n_clicks=0),
            dbc.Collapse(
                dbc.FormGroup(
                    children=[
                        dbc.Checklist(
                            options=[
                                {"label": make, "value": make.lower()}
                                for make in self._make_model.keys()
                            ],
                            className="ml-4",
                            id="make_actual_filter_options"
                        )
                    ]
                ),
                id="make_filter_options",
                is_open=False
            )
        ]

    def get_model_filter(self, color, classname):
        """ Return make filter """
        return [
            dbc.Button("Model", id="model_filter_btn", color=color, className=classname,
                       n_clicks=0),
            dbc.Collapse(
                dbc.FormGroup(
                    children=[
                        dbc.Checklist(
                            options=[
                                {"label": model, "value": model.lower()}
                                for model_list in self._make_model.values() for model in model_list
                            ],
                            className="ml-4",
                        )
                    ]
                ),
                id="model_filter_options",
                is_open=False
            )
        ]

    def get_odometer_filter(self, color, classname):
        """ Return odometer filter """
        return [
            dbc.Button("Odometer", id="odometer_filter_btn", color=color, className=classname,
                       n_clicks=0),
            dbc.Collapse(
                children=[
                    dbc.FormGroup(
                        children=[
                            dbc.Label("Min", className="mr-2"),
                            dbc.Input(type="text", placeholder="Min Price"),
                        ]
                    ),
                    dbc.FormGroup(
                        children=[
                            dbc.Label("Max", className="mr-2"),
                            dbc.Input(type="text", placeholder="Min Price"),
                        ]
                    ),
                ],
                id="odometer_filter_options",
                is_open=False
            )
        ]

    def get_price_filter(self, color, classname):
        """ Return price filter """
        return [
            dbc.Button("Price", id="price_filter_btn", color=color, className=classname,
                       n_clicks=0),
            dbc.Collapse(
                children=[
                    dbc.FormGroup(
                        children=[
                            dbc.Label("Min", className="mr-2"),
                            dbc.Input(type="text", placeholder="Min Price"),
                        ]
                    ),
                    dbc.FormGroup(
                        children=[
                            dbc.Label("Max", className="mr-2"),
                            dbc.Input(type="text", placeholder="Min Price"),
                        ]
                    ),
                ],
                id="price_filter_options",
                is_open=False
            )
        ]

    def get_offer_price_filter(self, color, classname):
        """ Return price filter """
        return [
            dbc.Button("OfferPricePctMMR", id="offer_price_filter_btn", color=color,
                       className=classname, n_clicks=0),
            dbc.Collapse(
                children=[
                    dbc.FormGroup(
                        children=[
                            dbc.Label("Min", className="mr-2"),
                            dbc.Input(type="text", placeholder="Min Price"),
                        ]
                    ),
                    dbc.FormGroup(
                        children=[
                            dbc.Label("Max", className="mr-2"),
                            dbc.Input(type="text", placeholder="Min Price"),
                        ]
                    ),
                ],
                id="offer_price_filter_options",
                is_open=False
            )
        ]

    def get_sidebar_filters(self):
        """ Side bar filters """
        color = "primary"
        classname = "mb-2"
        return [
            *self.get_year_filter(color=color, classname=classname),
            *self.get_make_filter(color=color, classname=classname),
            *self.get_model_filter(color=color, classname=classname),
            *self.get_odometer_filter(color=color, classname=classname),
            *self.get_price_filter(color=color, classname=classname),
            *self.get_offer_price_filter(color=color, classname=classname),
            dbc.Button("Apply", color="warning", className="mt-2", id="filter_apply_btn",
                       n_clicks=0),
            dbc.Button("Clear Filters", color="warning", className="mb-2 mt-2", id="filter_clear_btn",
                       n_clicks=0)
        ]

    def get_sidebar_layout(self):
        """ Side bar layout for filters """
        return [dbc.Card(children=self.get_sidebar_filters(), body=True), ]

    def get_potential_deal_table_layout(self):
        """ Potential deal table """
        columns = [{"id": x, "name": x} for x in self._potential_deals_cols]
        action_column = [x for x in columns if x["id"] == "Action"].pop()
        action_column["presentation"] = "dropdown"
        url_column = [x for x in columns if x["id"] == "url"].pop()
        url_column["presentation"] = "markdown"
        return dash_table.DataTable(
            id="potential_deal_table",
            columns=columns,
            data=self._potential_deals,
            page_size=50,
            style_table={"overflowX": "auto"},
            editable=True,
            css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],
            style_header={
                "backgroundColor": "rgb(104, 104, 104)",
            },
            style_cell={
                "backgroundColor": "rgb(48, 48, 48)",
                "color": "white",
                "textAlign": "center",
                "fontSize": "14px",
            },
            dropdown={
                "Action": {
                    # "clearable": True,
                    "options": [{"label": x, "value": x} for x in self._action_options]
                },
            },
        )

    def get_root_layout(self):
        """ Return main page layout """
        layout = dbc.Container(
            fluid=True,
            children=[
                self.get_nav_bar_layout(),
                dbc.Row(
                    [
                        dbc.Col(children=self.get_sidebar_layout(), md=2),
                        dbc.Col(children=self.get_potential_deal_table_layout(), md=10)

                    ]
                ),
            ]
        )
        return layout

    @staticmethod
    @app.callback(
        Output(component_id="year_filter_options", component_property="is_open"),
        Input(component_id="year_filter_btn", component_property="n_clicks"),
        State(component_id="year_filter_options", component_property="is_open")
    )
    def show_hide_year_options(n_clicks, is_open):
        """ Show or hide the year options """
        if n_clicks:
            return not is_open
        return is_open

    @staticmethod
    @app.callback(
        Output(component_id="make_filter_options", component_property="is_open"),
        Input(component_id="make_filter_btn", component_property="n_clicks"),
        State(component_id="make_filter_options", component_property="is_open")
    )
    def show_hide_make_options(n_clicks, is_open):
        """ Show or hide the year options """
        if n_clicks:
            return not is_open
        return is_open

    @staticmethod
    @app.callback(
        Output(component_id="model_filter_options", component_property="is_open"),
        Input(component_id="model_filter_btn", component_property="n_clicks"),
        State(component_id="model_filter_options", component_property="is_open")
    )
    def show_hide_model_options(n_clicks, is_open):
        """ Show or hide the year options """
        if n_clicks:
            return not is_open
        return is_open

    @staticmethod
    @app.callback(
        Output(component_id="odometer_filter_options", component_property="is_open"),
        Input(component_id="odometer_filter_btn", component_property="n_clicks"),
        State(component_id="odometer_filter_options", component_property="is_open")
    )
    def show_hide_odometer_options(n_clicks, is_open):
        """ Show or hide the year options """
        if n_clicks:
            return not is_open
        return is_open

    @staticmethod
    @app.callback(
        Output(component_id="price_filter_options", component_property="is_open"),
        Input(component_id="price_filter_btn", component_property="n_clicks"),
        State(component_id="price_filter_options", component_property="is_open")
    )
    def show_hide_price_options(n_clicks, is_open):
        """ Show or hide the year options """
        if n_clicks:
            return not is_open
        return is_open

    @staticmethod
    @app.callback(
        Output(component_id="offer_price_filter_options", component_property="is_open"),
        Input(component_id="offer_price_filter_btn", component_property="n_clicks"),
        State(component_id="offer_price_filter_options", component_property="is_open")
    )
    def show_hide_offer_price_options(n_clicks, is_open):
        """ Show or hide the year options """
        if n_clicks:
            return not is_open
        return is_open

    @staticmethod
    @app.callback(
        [Output(component_id="status_alert", component_property="children"),
         Output(component_id="status_alert", component_property="is_open"),
         Output(component_id="status_alert", component_property="duration")],
        Input(component_id="navbar_save_btn", component_property="n_clicks"),
        State(component_id="potential_deal_table", component_property="derived_viewport_data")
    )
    def save_action_comments(n_clicks, derived_viewport_data):
        """ Save the data to db """
        if n_clicks > 0:
            db_api = DBApi()
            records = [
                {
                    "PotentialDealID": record["PotentialDealID"],
                    "Action": record["Action"],
                    "Comment": record["Comment"]
                }
                for record in derived_viewport_data
            ]
            db_api.save_actions_comments(records=records)
            return ["Data saved successfully", True, 2000]
        return ["", False, 2000]

    @staticmethod
    @app.callback(
        Output(component_id="potential_deal_table", component_property="data"),
        [Input(component_id="filter_apply_btn", component_property="n_clicks"),
         Input(component_id="filter_clear_btn", component_property="n_clicks")],
        [State(component_id="year_actual_filter_options", component_property="value"),
         State(component_id="make_actual_filter_options", component_property="value")]
    )
    def filter_potential_deal_table(apply_n_clicks, clear_n_clicks, selected_year, selected_make):
        """ Filter potential deals table data """
        potential_deal_data = DBApi.get_instance().potential_records
        if clear_n_clicks > 0:
            return potential_deal_data
        filtered_year_ids = []
        filtered_make_ids = []
        for data in potential_deal_data:
            # Year filter
            if selected_year:
                for year in selected_year:
                    if year in data["make_model_year"]:
                        filtered_year_ids.append(data["PotentialDealID"])
                        break
            else:
                filtered_year_ids.append(data["PotentialDealID"])

            # Make filter
            if selected_make:
                for make in selected_make:
                    if make in data["make_model_year"].lower():
                        filtered_make_ids.append(data["PotentialDealID"])
            else:
                filtered_make_ids.append(data["PotentialDealID"])

        if selected_year or selected_make:
            filtered_ids = set(filtered_year_ids).intersection(set(filtered_make_ids))
            filtered_data = [
                data for data in potential_deal_data if data["PotentialDealID"] in filtered_ids
            ]
            return filtered_data
        return potential_deal_data


if __name__ == "__main__":
    AppLayout().setup()
    app.run_server(debug=True)
