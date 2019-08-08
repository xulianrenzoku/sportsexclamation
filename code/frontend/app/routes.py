from flask import Flask, render_template, request, redirect, \
    send_from_directory
import re

from dfs_data import *
from team_hist import create_lineup_dist


app = Flask(__name__)
day = '2019-03-26'
dfs_fanduel = DfsData(day, "fanduel")
dfs_draftkings = DfsData(day, "draftkings")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# @app.route("/<path:path>")
# def send_static(path):
#     return send_from_directory("", path)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.form:
        if "fanduel" in request.form:
            return redirect("/fanduel")
        if "draftkings" in request.form:
            return redirect("/draftkings")
    return render_template("home.html")


@app.route("/fanduel", methods=["GET", "POST"])
def show_fanduel():
    player_display_dict = dfs_fanduel.create_dashboard_display_dict()
    if request.form:
        # An entry from ONE SHINING LINEUP being clicked
        if "pg" in request.form:
            to_change = request.form.get("pg")[-1]
            return render_template('fanduel_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="pg",
                                   to_change=to_change,
                                   selected=dfs_fanduel.selected,
                                   lineup_name=dfs_fanduel.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_fanduel.remain_budget))
        if "sg" in request.form:
            to_change = str(int(request.form.get("sg")[-1]) + 2)
            return render_template('fanduel_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="sg",
                                   to_change=to_change,
                                   selected=dfs_fanduel.selected,
                                   lineup_name=dfs_fanduel.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_fanduel.remain_budget))
        if "sf" in request.form:
            to_change = str(int(request.form.get("sf")[-1]) + 4)
            return render_template('fanduel_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="sf",
                                   to_change=to_change,
                                   selected=dfs_fanduel.selected,
                                   lineup_name=dfs_fanduel.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_fanduel.remain_budget))
        if "pf" in request.form:
            to_change = str(int(request.form.get("pf")[-1]) + 6)
            return render_template('fanduel_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="pf",
                                   to_change=to_change,
                                   selected=dfs_fanduel.selected,
                                   lineup_name=dfs_fanduel.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_fanduel.remain_budget))
        if "c" in request.form:
            to_change = str(int(request.form.get("c")[-1]) + 8)
            return render_template('fanduel_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="c",
                                   to_change=to_change,
                                   selected=dfs_fanduel.selected,
                                   lineup_name=dfs_fanduel.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_fanduel.remain_budget))

        # An entry from SELECT pool being clicked
        for key in request.form:
            if key.startswith("select_"):
                to_change = request.form.get("to_change_order")
                m = re.match(r".*_(?P<select_pool>.+)_(?P<select_order>.+)",
                             key)
                print(m.groups())
                select_pool = m.group("select_pool")
                select_index = int(m.group("select_order")) - 1
                dfs_fanduel.select(select_pool, select_index, to_change)

                # iterate over all current players to generate histogram
                active_lineup = []
                for position, players in dfs_fanduel.selected.items():
                    for player in players:
                        # try needed for the first sweep
                        try:
                            active_lineup.append(player[0])
                        except IndexError:
                            pass
                create_lineup_dist(active_lineup, 'fd',
                                   write_path='static/' +
                                              'layout_f_template/' +
                                              'lineup_dist_fd.png')

                return render_template('fanduel_v2.html',
                                       day=day,
                                       record=player_display_dict,
                                       select_pool=select_pool,
                                       to_change=to_change,
                                       selected=dfs_fanduel.selected,
                                       lineup_name=dfs_fanduel.lineup,
                                       remain_budget='${:,}'.format(
                                           dfs_fanduel.remain_budget))

    return render_template('fanduel_v2.html',
                           day=day,
                           record=player_display_dict,
                           select_pool="",
                           selected=dfs_fanduel.selected,
                           lineup_name=dfs_fanduel.lineup,
                           remain_budget='${:,}'.format(
                               dfs_fanduel.remain_budget))


@app.route("/draftkings", methods=["GET", "POST"])
def show_draftkings():
    player_display_dict = dfs_draftkings.create_dashboard_display_dict()
    if request.form:
        # An entry from ONE SHINING LINEUP being clicked
        if "pg" in request.form:
            to_change = request.form.get("pg")[-1]
            return render_template('draftkings_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="pg",
                                   to_change=to_change,
                                   selected=dfs_draftkings.selected,
                                   lineup_name=dfs_draftkings.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_draftkings.remain_budget))
        if "sg" in request.form:
            to_change = str(int(request.form.get("sg")[-1]) + 1)
            return render_template('draftkings_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="sg",
                                   to_change=to_change,
                                   selected=dfs_draftkings.selected,
                                   lineup_name=dfs_draftkings.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_draftkings.remain_budget))
        if "sf" in request.form:
            to_change = str(int(request.form.get("sf")[-1]) + 2)
            return render_template('draftkings_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="sf",
                                   to_change=to_change,
                                   selected=dfs_draftkings.selected,
                                   lineup_name=dfs_draftkings.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_draftkings.remain_budget))
        if "pf" in request.form:
            to_change = str(int(request.form.get("pf")[-1]) + 3)
            return render_template('draftkings_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="pf",
                                   to_change=to_change,
                                   selected=dfs_draftkings.selected,
                                   lineup_name=dfs_draftkings.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_draftkings.remain_budget))
        if "c" in request.form:
            to_change = str(int(request.form.get("c")[-1]) + 4)
            return render_template('draftkings_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="c",
                                   to_change=to_change,
                                   selected=dfs_draftkings.selected,
                                   lineup_name=dfs_draftkings.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_draftkings.remain_budget))
        if "g" in request.form:
            to_change = str(int(request.form.get("g")[-1]) + 5)
            return render_template('draftkings_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="g",
                                   to_change=to_change,
                                   selected=dfs_draftkings.selected,
                                   lineup_name=dfs_draftkings.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_draftkings.remain_budget))
        if "f" in request.form:
            to_change = str(int(request.form.get("f")[-1]) + 6)
            return render_template('draftkings_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="f",
                                   to_change=to_change,
                                   selected=dfs_draftkings.selected,
                                   lineup_name=dfs_draftkings.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_draftkings.remain_budget))
        if "util" in request.form:
            to_change = str(int(request.form.get("util")[-1]) + 7)
            return render_template('draftkings_v2.html',
                                   day=day,
                                   record=player_display_dict,
                                   select_pool="util",
                                   to_change=to_change,
                                   selected=dfs_draftkings.selected,
                                   lineup_name=dfs_draftkings.lineup,
                                   remain_budget='${:,}'.format(
                                       dfs_draftkings.remain_budget))

        # An entry from SELECT pool being clicked
        for key in request.form:
            if key.startswith("select_"):
                to_change = request.form.get("to_change_order")
                m = re.match(r".*_(?P<select_pool>.+)_(?P<select_order>.+)",
                             key)
                print(m.groups())
                select_pool = m.group("select_pool")
                select_index = int(m.group("select_order")) - 1
                dfs_draftkings.select(select_pool, select_index, to_change)

                # iterate over all current players to generate histogram
                active_lineup = []
                for position, players in dfs_draftkings.selected.items():
                    for player in players:
                        # try needed for the first sweep
                        try:
                            active_lineup.append(player[0])
                        except IndexError:
                            pass
                create_lineup_dist(active_lineup, 'dk',
                                   write_path='static/' +
                                              'layout_d_template/' +
                                              'lineup_dist_dk.png')

                return render_template('draftkings_v2.html',
                                       day=day,
                                       record=player_display_dict,
                                       select_pool=select_pool,
                                       to_change=to_change,
                                       selected=dfs_draftkings.selected,
                                       lineup_name=dfs_draftkings.lineup,
                                       remain_budget='${:,}'.format(
                                           dfs_draftkings.remain_budget))

    return render_template('draftkings_v2.html',
                           day=day,
                           record=player_display_dict,
                           select_pool="",
                           selected=dfs_draftkings.selected,
                           lineup_name=dfs_draftkings.lineup,
                           remain_budget='${:,}'.format(
                               dfs_draftkings.remain_budget))


@app.route("/player_fanduel", methods=["GET", "POST"])
def player_fanduel():
    return render_template('player_template_fd.html')


@app.route("/player_draftkings", methods=["GET", "POST"])
def player_draftkings():
    return render_template('player_template_dk.html')


@app.route("/projection_explorer_fd", methods=["GET", "POST"])
def projection_explorer_fd():
    return render_template('projection_explorer_fd.html')


@app.route("/projection_explorer_dk", methods=["GET", "POST"])
def projection_explorer_dk():
    return render_template('projection_explorer_dk.html')


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, ' \
                                        'no-cache, must-revalidate, ' \
                                        '4post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8080)
