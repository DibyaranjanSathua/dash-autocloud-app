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
from dash.exceptions import PreventUpdate

from db import DBApi


app = dash.Dash(
    external_stylesheets=[dbc.themes.DARKLY, "style.css"],
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
        self._filters = []

    def setup(self):
        """ Setup the app layout """
        print("Inside setup")
        self.fetch_from_db()
        # Don't assign to the function output. Assing it to the function object so that whenever we
        # do some changes to layout, it will reflect without server restarting
        app.layout = self.get_root_layout
        return app.server

    def fetch_from_db(self):
        """ Fetch data from db """
        self._potential_deals = DBApi.get_instance().potential_records
        self._filters = DBApi.get_instance().filters
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
                    dbc.Alert(children="", id="error_alert", color="danger",
                              dismissable=True, is_open=False),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Alert(children="", id="save_filter_alert", color="success",
                              dismissable=True, is_open=False),
                    width="auto"
                ),
                dbc.Col(
                    dbc.Alert(children="", id="real_time_interval_output", color="success",
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
                            id="model_actual_filter_options"
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
                            dbc.Input(
                                type="number",
                                placeholder="Min Price",
                                id="odometer_actual_filter_min"
                            ),
                        ]
                    ),
                    dbc.FormGroup(
                        children=[
                            dbc.Label("Max", className="mr-2"),
                            dbc.Input(
                                type="number",
                                placeholder="Max Price",
                                id="odometer_actual_filter_max"
                            ),
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
                            dbc.Input(
                                type="number",
                                placeholder="Min Price",
                                id="price_actual_filter_min",
                            ),
                        ]
                    ),
                    dbc.FormGroup(
                        children=[
                            dbc.Label("Max", className="mr-2"),
                            dbc.Input(
                                type="number",
                                placeholder="Min Price",
                                id="price_actual_filter_max"
                            ),
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
                            dbc.Input(
                                type="number",
                                placeholder="Min Price",
                                id="offer_price_actual_filter_min"
                            ),
                        ]
                    ),
                    dbc.FormGroup(
                        children=[
                            dbc.Label("Max", className="mr-2"),
                            dbc.Input(
                                type="number",
                                placeholder="Min Price",
                                id="offer_price_actual_filter_max"
                            ),
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

    def get_sidebar_filter_save(self):
        """ Side bar filters save """
        return [
            dbc.FormGroup(
                children=[
                    dbc.Label("Filter name", className="mr-2"),
                    dbc.Input(
                        type="text",
                        placeholder="filter name",
                        id="filter_name"
                    ),
                ]
            ),
            dbc.Button("Save", color="warning", className="mt-2", id="filter_save_btn",
                       n_clicks=0),
        ]

    def get_sidebar_saved_filter_names(self):
        """ Show already saved filter names """
        radio_options = [
            {"label": f"{x['name']}", "value": f"{x['name']}"} for x in self._filters
        ]
        radio_options.insert(0, {"label": "None", "value": "None"})
        return [
            dbc.FormGroup(
                children=[
                    dbc.Label("Saved Filters", className="mr-2"),
                    dbc.RadioItems(
                        options=radio_options,
                        value="None",
                        id="filter_radioitems_input",
                    ),
                ]
            ),
        ]

    def get_sidebar_layout(self):
        """ Side bar layout for filters """
        return [
            dbc.Card(children=self.get_sidebar_filters(), body=True),
            dbc.Card(children=self.get_sidebar_filter_save(), body=True, className="mt-2"),
            dbc.Card(children=self.get_sidebar_saved_filter_names(), body=True, className="mt-2")
        ]

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
            css=[
                {"selector": ".Select-menu-outer", "rule": "display: block !important"},
            ],
            style_header={
                "backgroundColor": "rgb(104, 104, 104)",
            },
            style_cell={
                "backgroundColor": "rgb(48, 48, 48)",
                "color": "white",
                "textAlign": "center",
                "fontSize": "14px",
            },
            # style_cell_conditional=[
            #     {
            #         'if': {
            #             'column_id': 'Action',
            #         },
            #         'backgroundColor': 'rgb(204, 51, 255)',
            #     }
            # ],
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
                        # Real time update database
                        dcc.Interval(
                            id='real_time_db_update',
                            interval=15000,  # in milliseconds
                            n_intervals=0
                        ),
                        dbc.Col(children=self.get_sidebar_layout(), md=2),
                        dbc.Col(children=self.get_potential_deal_table_layout(), md=10)

                    ]
                ),
                dbc.Row(
                    dbc.Label(children="Made with ❤️ in India"),
                    className="justify-content-center"
                )
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
            records = [
                {
                    "PotentialDealID": record["PotentialDealID"],
                    "Action": record["Action"],
                    "Comment": record["Comment"]
                }
                for record in derived_viewport_data
            ]
            DBApi.get_instance().save_actions_comments(records=records)
            return ["Data saved successfully", True, 5000]
        return ["", False, 5000]

    @staticmethod
    @app.callback(
        [Output(component_id="potential_deal_table", component_property="data"),
         Output(component_id="error_alert", component_property="children"),
         Output(component_id="error_alert", component_property="is_open"),
         Output(component_id="error_alert", component_property="duration")],
        Input(component_id="filter_apply_btn", component_property="n_clicks"),
        [State(component_id="potential_deal_table", component_property="data"),
         State(component_id="year_actual_filter_options", component_property="value"),
         State(component_id="make_actual_filter_options", component_property="value"),
         State(component_id="model_actual_filter_options", component_property="value"),
         State(component_id="odometer_actual_filter_min", component_property="value"),
         State(component_id="odometer_actual_filter_max", component_property="value"),
         State(component_id="price_actual_filter_min", component_property="value"),
         State(component_id="price_actual_filter_max", component_property="value"),
         State(component_id="offer_price_actual_filter_min", component_property="value"),
         State(component_id="offer_price_actual_filter_max", component_property="value")]
    )
    def filter_potential_deal_table(apply_n_clicks, potential_deal_table_data,
                                    selected_year, selected_make, selected_model, min_odometer,
                                    max_odometer, min_price, max_price, min_offer_price,
                                    max_offer_price):
        """ Filter potential deals table data """
        potential_deal_db_data = DBApi.get_instance().potential_records
        filtered_year_ids = []
        filtered_make_ids = []
        filtered_model_ids = []
        filtered_min_odometer_ids = []
        filtered_max_odometer_ids = []
        filtered_min_price_ids = []
        filtered_max_price_ids = []
        filtered_min_offer_price_ids = []
        filtered_max_offer_price_ids = []

        if selected_year or selected_make or min_odometer or max_odometer or min_price or \
                max_price or min_offer_price or max_offer_price:
            # Odometer filter
            if min_odometer and max_odometer:
                if int(max_odometer) < int(min_odometer):
                    return [
                        potential_deal_table_data,
                        "Max odometer value should be greater than min odometer value",
                        True,
                        5000
                    ]
            if min_price and max_price:
                if int(max_price) < int(min_price):
                    return [
                        potential_deal_table_data,
                        "Max price value should be greater than min price value",
                        True,
                        5000
                    ]

            if min_offer_price and max_offer_price:
                if int(max_offer_price) < int(min_offer_price):
                    return [
                        potential_deal_table_data,
                        "Max offer price MMR value should be greater "
                        "than min offer price MMR value",
                        True,
                        5000
                    ]

            for data in potential_deal_db_data:
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

                # Model filter
                if selected_model:
                    for model in selected_model:
                        if model in data["make_model_year"].lower():
                            filtered_model_ids.append(data["PotentialDealID"])
                else:
                    filtered_model_ids.append(data["PotentialDealID"])

                # Min odometer filter
                if min_odometer:
                    if int(data["odometer"]) >= int(min_odometer):
                        filtered_min_odometer_ids.append(data["PotentialDealID"])
                else:
                    filtered_min_odometer_ids.append(data["PotentialDealID"])

                # Max odometer filter
                if max_odometer:
                    if int(data["odometer"]) <= int(max_odometer):
                        filtered_max_odometer_ids.append(data["PotentialDealID"])
                else:
                    filtered_max_odometer_ids.append(data["PotentialDealID"])

                # Min price filter
                if min_price:
                    if int(data["price"]) >= int(min_price):
                        filtered_min_price_ids.append(data["PotentialDealID"])
                else:
                    filtered_min_price_ids.append(data["PotentialDealID"])

                # Max price filter
                if max_price:
                    if int(data["price"]) <= int(max_price):
                        filtered_max_price_ids.append(data["PotentialDealID"])
                else:
                    filtered_max_price_ids.append(data["PotentialDealID"])

                # Min offer price filter
                if min_offer_price:
                    if int(data["OfferPricePctMMR"]) >= int(min_offer_price):
                        filtered_min_offer_price_ids.append(data["PotentialDealID"])
                else:
                    filtered_min_offer_price_ids.append(data["PotentialDealID"])

                # Max offer price filter
                if max_offer_price:
                    if int(data["OfferPricePctMMR"]) <= int(max_offer_price):
                        filtered_max_offer_price_ids.append(data["PotentialDealID"])
                else:
                    filtered_max_offer_price_ids.append(data["PotentialDealID"])

            filtered_ids = set(filtered_year_ids).intersection(
                set(filtered_make_ids),
                set(filtered_model_ids),
                set(filtered_min_odometer_ids),
                set(filtered_max_odometer_ids),
                set(filtered_min_price_ids),
                set(filtered_max_price_ids),
                set(filtered_min_offer_price_ids),
                set(filtered_max_offer_price_ids)
            )
            filtered_data = [
                data
                for data in potential_deal_db_data
                if data["PotentialDealID"] in filtered_ids
            ]
            return [filtered_data, "", False, 2000]
        return [potential_deal_db_data, "", False, 2000]

    @staticmethod
    @app.callback(
        [Output(component_id="year_actual_filter_options", component_property="value"),
         Output(component_id="make_actual_filter_options", component_property="value"),
         Output(component_id="model_actual_filter_options", component_property="value"),
         Output(component_id="odometer_actual_filter_min", component_property="value"),
         Output(component_id="odometer_actual_filter_max", component_property="value"),
         Output(component_id="price_actual_filter_min", component_property="value"),
         Output(component_id="price_actual_filter_max", component_property="value"),
         Output(component_id="offer_price_actual_filter_min", component_property="value"),
         Output(component_id="offer_price_actual_filter_max", component_property="value"),
         Output(component_id="filter_apply_btn", component_property="n_clicks")],
        [Input(component_id="filter_clear_btn", component_property="n_clicks"),
         Input(component_id="filter_radioitems_input", component_property="value")],
        State(component_id="filter_apply_btn", component_property="n_clicks")
    )
    def add_or_clear_filter(n_clicks, filter_name, apply_btn_n_clicks):
        """ Filter potential deals table data """
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == "filter_clear_btn":
                return [[], [], [], "", "", "", "", "", "", apply_btn_n_clicks+1]
            elif button_id == "filter_radioitems_input":
                if filter_name != "None":
                    filter_from_db = next(
                        x for x in DBApi.get_instance().filters  if x["name"] == filter_name
                    )
                    year = filter_from_db["year"].split(",")
                    make = filter_from_db["make"].split(",")
                    model = filter_from_db["model"].split(",")
                    min_odometer = filter_from_db["min_odometer"]
                    max_odometer = filter_from_db["max_odometer"]
                    min_price = filter_from_db["min_price"]
                    max_price = filter_from_db["max_price"]
                    min_offer_price = filter_from_db["min_offer_price"]
                    max_offer_price = filter_from_db["max_offer_price"]
                    return [year, make, model, min_odometer, max_odometer, min_price, max_price,
                            min_offer_price, max_offer_price, apply_btn_n_clicks+1]

        return [[], [], [], "", "", "", "", "", "", apply_btn_n_clicks]

    @staticmethod
    @app.callback(
        [Output(component_id="save_filter_alert", component_property="children"),
         Output(component_id="save_filter_alert", component_property="is_open"),
         Output(component_id="save_filter_alert", component_property="color"),
         Output(component_id="save_filter_alert", component_property="duration"),
         Output(component_id="filter_radioitems_input", component_property="options"),
         Output(component_id="filter_name", component_property="value")],
        Input(component_id="filter_save_btn", component_property="n_clicks"),
        [State(component_id="filter_name", component_property="value"),
         State(component_id="year_actual_filter_options", component_property="value"),
         State(component_id="make_actual_filter_options", component_property="value"),
         State(component_id="model_actual_filter_options", component_property="value"),
         State(component_id="odometer_actual_filter_min", component_property="value"),
         State(component_id="odometer_actual_filter_max", component_property="value"),
         State(component_id="price_actual_filter_min", component_property="value"),
         State(component_id="price_actual_filter_max", component_property="value"),
         State(component_id="offer_price_actual_filter_min", component_property="value"),
         State(component_id="offer_price_actual_filter_max", component_property="value"),
         State(component_id="filter_radioitems_input", component_property="options")]
    )
    def save_filter(n_clicks, filter_name, selected_year, selected_make, selected_model,
                    min_odometer, max_odometer, min_price, max_price, min_offer_price,
                    max_offer_price, filter_options):
        if n_clicks > 0:
            if not filter_name:
                return ["Filter name can'b be empty", True, "danger", 5000, filter_options, ""]
            year = ",".join(selected_year)
            make = ",".join(selected_make)
            model = ",".join(selected_model)
            DBApi.get_instance().save_filter(
                name=filter_name,
                year=year,
                make=make,
                model=model,
                min_odometer=min_odometer,
                max_odometer=max_odometer,
                min_price=min_price,
                max_price=max_price,
                min_offer_price=min_offer_price,
                max_offer_price=max_offer_price
            )
            # Refresh filter names from db
            DBApi.get_instance().get_all_filters()
            filter_options = [
                {"label": f"{x['name']}", "value": f"{x['name']}"}
                for x in DBApi.get_instance().filters
            ]
            filter_options.insert(0, {"label": "None", "value": "None"})

            return ["Filter saved successfully", True, "success", 5000, filter_options, ""]
        return ["", False, "success", 5000, filter_options, ""]

    @staticmethod
    @app.callback(
        Output(component_id="real_time_interval_output", component_property="children"),
        Input(component_id="real_time_db_update", component_property="n_intervals")
    )
    def real_time_db_update(n_intervals):
        """ Update the potential deal cash in every 15 sec """
        # Output is just a dummy one as each callback needs an output
        if n_intervals > 0:
            # This will refresh self._potential_records in db.py which is used in datatable
            DBApi.get_instance().get_all_potential_records()
        return ""


if __name__ == "__main__":
    AppLayout().setup()
    app.run_server(debug=True)
