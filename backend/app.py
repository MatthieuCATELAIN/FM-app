from flask import Flask, request, jsonify
import pandas as pd
from bs4 import BeautifulSoup  

app = Flask(__name__)


@app.route('/upload_team', methods=['POST'])
def upload_file_team():
    global player_data_saved
    global column_headers_saved
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = 'team.html'
        file.save(file_path)
        modify_html_table_headers(file_path)
        column_headers_saved, player_data_saved = process_file(file_path)
        return jsonify({"message": "File uploaded and processed successfully"}), 200
    
@app.route('/upload_transfer', methods=['POST'])
def upload_file_transfer():
    global transfer_data_saved
    global transfer_column_headers_saved
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = 'transfer.html'
        file.save(file_path)
        modify_html_table_headers(file_path)
        transfer_column_headers_saved, transfer_data_saved = process_file(file_path)
        return jsonify({"message": "File uploaded and processed successfully"}), 200
    
def modify_html_table_headers(file_path):
    with open(file_path, 'r') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    det_counter = 0
    for th in soup.find_all('th'):
        if th.text != 'Détente':
            if th.text == 'Dét':
                if det_counter == 0:    
                    th.string.replace_with('Détente')
                elif det_counter == 2:
                    th.string.replace_with('Saut')
                det_counter += 1

    with open(file_path, 'w') as file:
        file.write(str(soup))

@app.route('/get_best_team', methods=['POST'])
def get_best_team():
    global formation_saved
    global best_team_saved
    global selected_roles_saved
    selected_roles = request.json.get('selected_roles')
    formation_saved = request.json.get('formation')
    best_team = select_best_team(selected_roles)
    selected_roles_saved = selected_roles
    best_team_saved = best_team
    return jsonify(best_team)

def select_best_team(selected_roles):
    best_team = {}
    selected_players = {}
    for position, role in selected_roles.items():
        best_player = get_best_player_for_role(role, selected_players, selected_roles)
        while best_player is None:
            role_index = column_headers_saved.index(role)
            role = column_headers_saved[role_index + 1] 
            best_player = get_best_player_for_role(role, selected_players, selected_roles)
        selected_players[role] = best_player
        best_team[position] = best_player

    return best_team

def get_best_player_for_role(role, selected_players, selected_roles):
    player_data_df = pd.DataFrame(player_data_saved, columns=column_headers_saved)
    column_index = column_headers_saved.index(role)
    sorted_data = player_data_df.sort_values(by=player_data_df.columns[column_index], ascending=False)
    
    for _, player in sorted_data.iterrows():
        player_name = player['Nom']
        if player_name not in selected_players or not selected_players[player_name]:
            better_role_found = False
            for selected_role, selected_role_value in selected_roles.items():
                    if player[role] < player[selected_role_value]:
                        better_role_found = True
                        break
            if not better_role_found:
                selected_players[player_name] = True 
                return {'Nom': player_name, 'Note': player[role]}
    return None


@app.route('/get_squad_data', methods=['GET'])
def get_squad_data():
    global player_data_saved, column_headers_saved
    return jsonify({"column_headers": column_headers_saved, "player_data": player_data_saved})

@app.route('/get_transfer_data', methods=['GET'])
def get_transfer_data():
    global transfer_data_saved, transfer_column_headers_saved
    return jsonify({"column_headers": transfer_column_headers_saved, "player_data": transfer_data_saved})

@app.route('/get_formation_data', methods=['GET'])
def get_formation_data():
    global formation_saved
    return jsonify({"formation": formation_saved})

@app.route('/get_best_team_saved', methods=['GET'])
def get_best_team_saved():
    global best_team_saved
    global selected_roles_saved
    return jsonify({"team": best_team_saved, "roles": selected_roles_saved})


def process_file(file_path):

    squad_rawdata_list = pd.read_html(file_path, header=0, encoding="utf-8", keep_default_na=False)
    squad_rawdata = squad_rawdata_list[0]

    # Process the data (you can add your processing logic here)
    squad_rawdata['Speed'] = ( squad_rawdata['Vit'] + squad_rawdata['Acc'] ) / 2

    # calculates Goalkeeper_Defend score
    squad_rawdata['gkd_key'] = ( squad_rawdata['Agi'] + squad_rawdata['Réf'] )
    squad_rawdata['gkd_green'] = ( squad_rawdata['Détente'] + squad_rawdata['Srf'] + squad_rawdata['Pbl'] + squad_rawdata['Dég'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] )
    squad_rawdata['gkd_blue'] = ( squad_rawdata['1c1'] + squad_rawdata['Rel'] + squad_rawdata['Ant'] + squad_rawdata['Déc'] )
    squad_rawdata['G'] =( ( ( squad_rawdata['gkd_key'] * 5) + (squad_rawdata['gkd_green'] * 3) + (squad_rawdata['gkd_blue'] * 1) ) / 32)
    squad_rawdata.G= squad_rawdata.G.round(1)
        
    # calculates Sweeper_keeper_Defend score
    squad_rawdata['skd_key'] = ( squad_rawdata['Agi'] + squad_rawdata['Réf'] )
    squad_rawdata['skd_green'] = ( squad_rawdata['Srf'] + squad_rawdata['Dég'] + squad_rawdata['1c1'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] )
    squad_rawdata['skd_blue'] = ( squad_rawdata['Détente'] + squad_rawdata['Ctr'] + squad_rawdata['Pbl'] + squad_rawdata['Pas'] + squad_rawdata['TSP'] + squad_rawdata['Déc'] + squad_rawdata['Vis'] + squad_rawdata['Acc'] )
    squad_rawdata['GL_D'] =( ( ( squad_rawdata['skd_key'] * 5) + (squad_rawdata['skd_green'] * 3) + (squad_rawdata['skd_blue'] * 1) ) / 36)
    squad_rawdata.GL_D= squad_rawdata.GL_D.round(1)
        
    # calculates Sweeper_keeper_Support score
    squad_rawdata['sks_key'] = ( squad_rawdata['Agi'] + squad_rawdata['Réf'] )
    squad_rawdata['sks_green'] = ( squad_rawdata['Srf'] + squad_rawdata['Dég'] + squad_rawdata['1c1'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] )
    squad_rawdata['sks_blue'] = ( squad_rawdata['Détente'] + squad_rawdata['Ctr'] + squad_rawdata['Pbl'] + squad_rawdata['Pas'] + squad_rawdata['TSP'] + squad_rawdata['Déc'] + squad_rawdata['Vis'] + squad_rawdata['Acc'] )
    squad_rawdata['GL_S'] =( ( ( squad_rawdata['sks_key'] * 5) + (squad_rawdata['sks_green'] * 3) + (squad_rawdata['sks_blue'] * 1) ) / 36)
    squad_rawdata.GL_S= squad_rawdata.GL_S.round(1)

    # calculates Sweeper_keeper_Attack score
    squad_rawdata['ska_key'] = ( squad_rawdata['Agi'] + squad_rawdata['Réf'] )
    squad_rawdata['ska_green'] = ( squad_rawdata['Srf'] + squad_rawdata['Dég'] + squad_rawdata['1c1'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] )
    squad_rawdata['ska_blue'] = ( squad_rawdata['Détente'] + squad_rawdata['Ctr'] + squad_rawdata['Pbl'] + squad_rawdata['Pas'] + squad_rawdata['TSP'] + squad_rawdata['Déc'] + squad_rawdata['Vis'] + squad_rawdata['Acc'] )
    squad_rawdata['GL_A'] =( ( ( squad_rawdata['ska_key'] * 5) + (squad_rawdata['ska_green'] * 3) + (squad_rawdata['ska_blue'] * 1) ) / 36)
    squad_rawdata.GL_A= squad_rawdata.GL_A.round(1)

    # calculates Ball_playing_defender_Defend score
    squad_rawdata['bpdd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['bpdd_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] )
    squad_rawdata['bpdd_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Tec'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Vis'] )
    squad_rawdata['DC_Rel_D'] =( ( ( squad_rawdata['bpdd_key'] * 5) + (squad_rawdata['bpdd_green'] * 3) + (squad_rawdata['bpdd_blue'] * 1) ) / 46)
    squad_rawdata.DC_Rel_D= squad_rawdata.DC_Rel_D.round(1)

    # calculates Ball_playing_defender_Stopper score
    squad_rawdata['bpds_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['bpds_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] + squad_rawdata['Agr'] + squad_rawdata['Crg'] + squad_rawdata['Déc'] )
    squad_rawdata['bpds_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Vis'] + squad_rawdata['Mar'] )
    squad_rawdata['DC_Rel_St'] =( ( ( squad_rawdata['bpds_key'] * 5) + (squad_rawdata['bpds_green'] * 3) + (squad_rawdata['bpds_blue'] * 1) ) / 50)
    squad_rawdata.DC_Rel_St= squad_rawdata.DC_Rel_St.round(1)

    # calculates Ball_playing_defender_Cover score
    squad_rawdata['bpdc_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['bpdc_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Pla'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] )
    squad_rawdata['bpdc_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Tec'] + squad_rawdata['Crg'] + squad_rawdata['Vis'] + squad_rawdata['Pui'] + squad_rawdata['Têt'] )
    squad_rawdata['DC_Rel_Co'] =( ( ( squad_rawdata['bpdc_key'] * 5) + (squad_rawdata['bpdc_green'] * 3) + (squad_rawdata['bpdc_blue'] * 1) ) / 47)
    squad_rawdata.DC_Rel_Co= squad_rawdata.DC_Rel_Co.round(1)

    # calculates Central_defender_Defend score
    squad_rawdata['cdd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['cdd_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] )
    squad_rawdata['cdd_blue'] = ( squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] )
    squad_rawdata['DC_Def'] =( ( ( squad_rawdata['cdd_key'] * 5) + (squad_rawdata['cdd_green'] * 3) + (squad_rawdata['cdd_blue'] * 1) ) / 40)
    squad_rawdata.DC_Def= squad_rawdata.DC_Def.round(1)

    # calculates Central_defender_Stopper score
    squad_rawdata['cds_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['cds_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Tcl'] + squad_rawdata['Agr'] + squad_rawdata['Crg'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] )
    squad_rawdata['cds_blue'] = ( squad_rawdata['Mar'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] )
    squad_rawdata['DC_Stop'] =( ( ( squad_rawdata['cds_key'] * 5) + (squad_rawdata['cds_green'] * 3) + (squad_rawdata['cds_blue'] * 1) ) / 44)
    squad_rawdata.DC_Stop= squad_rawdata.DC_Stop.round(1)

    # calculates Central_defender_Cover score
    squad_rawdata['cdc_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['cdc_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] )
    squad_rawdata['cdc_blue'] = ( squad_rawdata['Têt'] + squad_rawdata['Crg'] + squad_rawdata['Pui'] )
    squad_rawdata['DC_Couv'] =( ( ( squad_rawdata['cdc_key'] * 5) + (squad_rawdata['cdc_green'] * 3) + (squad_rawdata['cdc_blue'] * 1) ) / 41)
    squad_rawdata.DC_Couv= squad_rawdata.DC_Couv.round(1)

    # calculates Complete_wing_back_Support score
    squad_rawdata['cwbs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['cwbs_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Tec'] + squad_rawdata['Apl'] + squad_rawdata['Col'] )
    squad_rawdata['cwbs_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Déc'] + squad_rawdata['Ins'] + squad_rawdata['Pla'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] )
    squad_rawdata['Lat_Comp_S'] =( ( ( squad_rawdata['cwbs_key'] * 5) + (squad_rawdata['cwbs_green'] * 3) + (squad_rawdata['cwbs_blue'] * 1) ) / 45)
    squad_rawdata.Lat_Comp_S= squad_rawdata.Lat_Comp_S.round(1)

    # calculates Complete_wing_back_Attack score
    squad_rawdata['cwba_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['cwba_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Tec'] + squad_rawdata['Ins'] + squad_rawdata['Apl'] + squad_rawdata['Col'] )
    squad_rawdata['cwba_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] )
    squad_rawdata['Lat_Comp_A'] =( ( ( squad_rawdata['cwba_key'] * 5) + (squad_rawdata['cwba_green'] * 3) + (squad_rawdata['cwba_blue'] * 1) ) / 47)
    squad_rawdata.Lat_Comp_A= squad_rawdata.Lat_Comp_A.round(1)

    # calculates Full_back_Defend score
    squad_rawdata['fbd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['fbd_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] + squad_rawdata['Pla'] )
    squad_rawdata['fbd_blue'] = ( squad_rawdata['Cen'] + squad_rawdata['Pas'] + squad_rawdata['Déc'] + squad_rawdata['Col'] )
    squad_rawdata['Arr_Lat_D'] =( ( ( squad_rawdata['fbd_key'] * 5) + (squad_rawdata['fbd_green'] * 3) + (squad_rawdata['fbd_blue'] * 1) ) / 42)
    squad_rawdata.Arr_Lat_D= squad_rawdata.Arr_Lat_D.round(1)

    # calculates Full_back_Support score
    squad_rawdata['fbs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['fbs_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['fbs_blue'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Déc'] )
    squad_rawdata['Arr_Lat_S'] =( ( ( squad_rawdata['fbs_key'] * 5) + (squad_rawdata['fbs_green'] * 3) + (squad_rawdata['fbs_blue'] * 1) ) / 43)
    squad_rawdata.Arr_Lat_S= squad_rawdata.Arr_Lat_S.round(1)

    # calculates Full_back_Attack score
    squad_rawdata['fba_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['fba_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['fba_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Agi'] )
    squad_rawdata['Arr_Lat_A'] =( ( ( squad_rawdata['fba_key'] * 5) + (squad_rawdata['fba_green'] * 3) + (squad_rawdata['fba_blue'] * 1) ) / 46)
    squad_rawdata.Arr_Lat_A= squad_rawdata.Arr_Lat_A.round(1)

    # calculates Inverted_full_back_Defend score
    squad_rawdata['ifbd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['ifbd_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] )
    squad_rawdata['ifbd_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Agi'] + squad_rawdata['Saut'] )
    squad_rawdata['Lat_Inver'] =( ( ( squad_rawdata['ifbd_key'] * 5) + (squad_rawdata['ifbd_green'] * 3) + (squad_rawdata['ifbd_blue'] * 1) ) / 47)
    squad_rawdata.Lat_Inver= squad_rawdata.Lat_Inver.round(1)

    # calculates Inverted_wing_back_Defend score
    squad_rawdata['iwbd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['iwbd_green'] = ( squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['iwbd_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Mar'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Apl'] + squad_rawdata['Agi'] )
    squad_rawdata['Lat_Int_D'] =( ( ( squad_rawdata['iwbd_key'] * 5) + (squad_rawdata['iwbd_green'] * 3) + (squad_rawdata['iwbd_blue'] * 1) ) / 45)
    squad_rawdata.Lat_Int_D= squad_rawdata.Lat_Int_D.round(1)

    # calculates Inverted_wing_back_Support score
    squad_rawdata['iwbs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['iwbs_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Col'] )
    squad_rawdata['iwbs_blue'] = ( squad_rawdata['Mar'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Apl'] + squad_rawdata['Pla'] + squad_rawdata['Vis'] + squad_rawdata['Agi'] )
    squad_rawdata['Lat_Int_S'] =( ( ( squad_rawdata['iwbs_key'] * 5) + (squad_rawdata['iwbs_green'] * 3) + (squad_rawdata['iwbs_blue'] * 1) ) / 46)
    squad_rawdata.Lat_Int_S= squad_rawdata.Lat_Int_S.round(1)

    # calculates Inverted_wing_back_Attack score
    squad_rawdata['iwba_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['iwba_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Col'] + squad_rawdata['Vis'] )
    squad_rawdata['iwba_blue'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Tir'] + squad_rawdata['Mar'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Ins'] + squad_rawdata['Pla'] + squad_rawdata['Agi'] )
    squad_rawdata['Lat_Int_A'] =( ( ( squad_rawdata['iwba_key'] * 5) + (squad_rawdata['iwba_green'] * 3) + (squad_rawdata['iwba_blue'] * 1) ) / 56)
    squad_rawdata.Lat_Int_A= squad_rawdata.Lat_Int_A.round(1)

    # calculates Libero_Defend score
    squad_rawdata['ld_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['ld_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Têt'] + squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Tec'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Col'] + squad_rawdata['Pui'] )
    squad_rawdata['ld_blue'] = ( squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['End'] )
    squad_rawdata['Lib_Def'] =( ( ( squad_rawdata['ld_key'] * 5) + (squad_rawdata['ld_green'] * 3) + (squad_rawdata['ld_blue'] * 1) ) / 54)
    squad_rawdata.Lib_Def= squad_rawdata.Lib_Def.round(1)

    # calculates Libero_Support score
    squad_rawdata['ls_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['ls_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Têt'] + squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Tec'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Col'] + squad_rawdata['Pui'] )
    squad_rawdata['ls_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['Vis'] + squad_rawdata['End'] )
    squad_rawdata['Lib_Sup'] =( ( ( squad_rawdata['ls_key'] * 5) + (squad_rawdata['ls_green'] * 3) + (squad_rawdata['ls_blue'] * 1) ) / 56)
    squad_rawdata.Lib_Sup= squad_rawdata.Lib_Sup.round(1)

    # calculates No-nonsense_centre_back_Defend score
    squad_rawdata['ncbd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['ncbd_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] )
    squad_rawdata['ncbd_blue'] = ( squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] )
    squad_rawdata['DC_Strict_D'] =( ( ( squad_rawdata['ncbd_key'] * 5) + (squad_rawdata['ncbd_green'] * 3) + (squad_rawdata['ncbd_blue'] * 1) ) / 39)
    squad_rawdata.DC_Strict_D= squad_rawdata.DC_Strict_D.round(1)

    # calculates No-nonsense_centre_back_Stopper score
    squad_rawdata['ncbs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['ncbs_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Tcl'] + squad_rawdata['Agr'] + squad_rawdata['Crg'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] )
    squad_rawdata['ncbs_blue'] = ( squad_rawdata['Mar'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] )
    squad_rawdata['DC_Strict_St'] =( ( ( squad_rawdata['ncbs_key'] * 5) + (squad_rawdata['ncbs_green'] * 3) + (squad_rawdata['ncbs_blue'] * 1) ) / 41)
    squad_rawdata.DC_Strict_St= squad_rawdata.DC_Strict_St.round(1)

    # calculates No-nonsense_centre_back_Cover score
    squad_rawdata['ncbc_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['ncbc_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] )
    squad_rawdata['ncbc_blue'] = ( squad_rawdata['Têt'] + squad_rawdata['Crg'] + squad_rawdata['Pui'] )
    squad_rawdata['DC_Strict_Co'] =( ( ( squad_rawdata['ncbc_key'] * 5) + (squad_rawdata['ncbc_green'] * 3) + (squad_rawdata['ncbc_blue'] * 1) ) / 38)
    squad_rawdata.DC_Strict_Co= squad_rawdata.DC_Strict_Co.round(1)

    # calculates No-nonsense_full_back_Defend score
    squad_rawdata['nfbd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['nfbd_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] )
    squad_rawdata['nfbd_blue'] = ( squad_rawdata['Têt'] + squad_rawdata['Agr'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['Col'] )
    squad_rawdata['nfbd'] =( ( ( squad_rawdata['nfbd_key'] * 5) + (squad_rawdata['nfbd_green'] * 3) + (squad_rawdata['nfbd_blue'] * 1) ) / 40)
    squad_rawdata.Arr_Lat_Strict= squad_rawdata.nfbd.round(1)

    # calculates Wide_centre_back_Defend score
    squad_rawdata['wcbd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['wcbd_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] )
    squad_rawdata['wcbd_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Vol'] + squad_rawdata['Agi'] )
    squad_rawdata['DC_Exc_D'] =( ( ( squad_rawdata['wcbd_key'] * 5) + (squad_rawdata['wcbd_green'] * 3) + (squad_rawdata['wcbd_blue'] * 1) ) / 46)
    squad_rawdata.DC_Exc_D= squad_rawdata.DC_Exc_D.round(1)

    # calculates Wide_centre_back_Support score
    squad_rawdata['wcbs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['wcbs_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Têt'] + squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Pla'] + squad_rawdata['Pui'] )
    squad_rawdata['wcbs_blue'] = ( squad_rawdata['Cen'] + squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Vol'] + squad_rawdata['Agi'] + squad_rawdata['End'] )
    squad_rawdata['DC_Exc_S'] =( ( ( squad_rawdata['wcbs_key'] * 5) + (squad_rawdata['wcbs_green'] * 3) + (squad_rawdata['wcbs_blue'] * 1) ) / 51)
    squad_rawdata.DC_Exc_S= squad_rawdata.DC_Exc_S.round(1)

    # calculates Wide_centre_back_Attack score
    squad_rawdata['wcba_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Saut'] + squad_rawdata['Sgf'] )
    squad_rawdata['wcba_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Têt'] + squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Apl'] + squad_rawdata['End'] + squad_rawdata['Pui'] )
    squad_rawdata['wcba_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Vol'] + squad_rawdata['Agi'] )
    squad_rawdata['DC_Exc_A'] =( ( ( squad_rawdata['wcba_key'] * 5) + (squad_rawdata['wcba_green'] * 3) + (squad_rawdata['wcba_blue'] * 1) ) / 55)
    squad_rawdata.DC_Exc_A= squad_rawdata.DC_Exc_A.round(1)

    # calculates Wing_back_Defend score
    squad_rawdata['wbd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['wbd_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['wbd_blue'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] )
    squad_rawdata['Lat_Off_D'] =( ( ( squad_rawdata['wbd_key'] * 5) + (squad_rawdata['wbd_green'] * 3) + (squad_rawdata['wbd_blue'] * 1) ) / 45)
    squad_rawdata.Lat_Off_D= squad_rawdata.Lat_Off_D.round(1)

    # calculates Wing_back_Support score
    squad_rawdata['wbs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['wbs_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Apl'] + squad_rawdata['Col'] )
    squad_rawdata['wbs_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] )
    squad_rawdata['Lat_Off_S'] =( ( ( squad_rawdata['wbs_key'] * 5) + (squad_rawdata['wbs_green'] * 3) + (squad_rawdata['wbs_blue'] * 1) ) / 47)
    squad_rawdata.Lat_Off_S= squad_rawdata.Lat_Off_S.round(1)

    # calculates Wing_back_Attack score
    squad_rawdata['wba_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['wba_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Tcl'] + squad_rawdata['Tec'] + squad_rawdata['Apl'] + squad_rawdata['Col'] )
    squad_rawdata['wba_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Ins'] + squad_rawdata['Pla'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] )
    squad_rawdata['Lat_Off_A'] =( ( ( squad_rawdata['wba_key'] * 5) + (squad_rawdata['wba_green'] * 3) + (squad_rawdata['wba_blue'] * 1) ) / 48)
    squad_rawdata.Lat_Off_A= squad_rawdata.Lat_Off_A.round(1)

    # calculates Advanced_playmaker_Support score
    squad_rawdata['aps_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['aps_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Col'] + squad_rawdata['Vis'] )
    squad_rawdata['aps_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Ant'] + squad_rawdata['Ins'] + squad_rawdata['Agi'] )
    squad_rawdata['Meneur_Ava_S'] =( ( ( squad_rawdata['aps_key'] * 5) + (squad_rawdata['aps_green'] * 3) + (squad_rawdata['aps_blue'] * 1) ) / 48)
    squad_rawdata.Meneur_Ava_S= squad_rawdata.Meneur_Ava_S.round(1)

    # calculates Advanced_playmaker_Attack score
    squad_rawdata['apa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['apa_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Col'] + squad_rawdata['Vis'] )
    squad_rawdata['apa_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Ant'] + squad_rawdata['Ins'] + squad_rawdata['Agi'] )
    squad_rawdata['Meneur_Ava_A'] =( ( ( squad_rawdata['apa_key'] * 5) + (squad_rawdata['apa_green'] * 3) + (squad_rawdata['apa_blue'] * 1) ) / 48)
    squad_rawdata.Meneur_Ava_A= squad_rawdata.Meneur_Ava_A.round(1)

    # calculates Anchor_Defend score
    squad_rawdata['ad_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['ad_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] )
    squad_rawdata['ad_blue'] = ( squad_rawdata['Sgf'] + squad_rawdata['Col'] + squad_rawdata['Pui'] )
    squad_rawdata['MD_Senti'] =( ( ( squad_rawdata['ad_key'] * 5) + (squad_rawdata['ad_green'] * 3) + (squad_rawdata['ad_blue'] * 1) ) / 41)
    squad_rawdata.MD_Senti= squad_rawdata.MD_Senti.round(1)

    # calculates Attacking_midfielder_Support score
    squad_rawdata['ams_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['ams_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Tir'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Déc'] + squad_rawdata['Ins'] + squad_rawdata['Apl'] )
    squad_rawdata['ams_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Sgf'] + squad_rawdata['Vis'] + squad_rawdata['Agi'] )
    squad_rawdata['MO_S'] =( ( ( squad_rawdata['ams_key'] * 5) + (squad_rawdata['ams_green'] * 3) + (squad_rawdata['ams_blue'] * 1) ) / 48)
    squad_rawdata.MO_S= squad_rawdata.MO_S.round(1)

    # calculates Attacking_midfielder_Attack score
    squad_rawdata['ama_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['ama_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Tir'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Déc'] + squad_rawdata['Ins'] + squad_rawdata['Apl'] )
    squad_rawdata['ama_blue'] = ( squad_rawdata['Fin'] + squad_rawdata['Sgf'] + squad_rawdata['Vis'] + squad_rawdata['Agi'] )
    squad_rawdata['MO_A'] =( ( ( squad_rawdata['ama_key'] * 5) + (squad_rawdata['ama_green'] * 3) + (squad_rawdata['ama_blue'] * 1) ) / 51)
    squad_rawdata.MO_A= squad_rawdata.MO_A.round(1)

    # calculates Ball_winning_midfielder_Defend score
    squad_rawdata['bwmd_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['bwmd_green'] = ( squad_rawdata['Tcl'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Col'] )
    squad_rawdata['bwmd_blue'] = ( squad_rawdata['Mar'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] + squad_rawdata['Agi'] + squad_rawdata['Pui'] )
    squad_rawdata['MD_Recup_D'] =( ( ( squad_rawdata['bwmd_key'] * 5) + (squad_rawdata['bwmd_green'] * 3) + (squad_rawdata['bwmd_blue'] * 1) ) / 38)
    squad_rawdata.MD_Recup_D= squad_rawdata.MD_Recup_D.round(1)

    # calculates Ball_winning_midfielder_Support score
    squad_rawdata['bwms_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['bwms_green'] = ( squad_rawdata['Tcl'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Col'] )
    squad_rawdata['bwms_blue'] = ( squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Crg'] + squad_rawdata['Ctn'] + squad_rawdata['Agi'] + squad_rawdata['Pui'] )
    squad_rawdata['MD_Recup_S'] =( ( ( squad_rawdata['bwms_key'] * 5) + (squad_rawdata['bwms_green'] * 3) + (squad_rawdata['bwms_blue'] * 1) ) / 38)
    squad_rawdata.MD_Recup_S= squad_rawdata.MD_Recup_S.round(1)

    # calculates Box_to_box_midfielder_Support score
    squad_rawdata['b2bs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['b2bs_green'] = ( squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Apl'] + squad_rawdata['Col'] )
    squad_rawdata['b2bs_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Fin'] + squad_rawdata['Ctr'] + squad_rawdata['Tir'] + squad_rawdata['Tec'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Équ'] + squad_rawdata['Pui'] )
    squad_rawdata['B2B'] =( ( ( squad_rawdata['b2bs_key'] * 5) + (squad_rawdata['b2bs_green'] * 3) + (squad_rawdata['b2bs_blue'] * 1) ) / 44)
    squad_rawdata.B2B= squad_rawdata.B2B.round(1)

    # calculates Carrilero_Support score
    squad_rawdata['cars_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['cars_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['cars_blue'] = ( squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Apl'] + squad_rawdata['Vis'] )
    squad_rawdata['Carrilero'] =( ( ( squad_rawdata['cars_key'] * 5) + (squad_rawdata['cars_green'] * 3) + (squad_rawdata['cars_blue'] * 1) ) / 44)
    squad_rawdata.Carrilero= squad_rawdata.Carrilero.round(1)

    # calculates Central_midfielder_Defend score
    squad_rawdata['cmd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['cmd_green'] = ( squad_rawdata['Tcl'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['cmd_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] )
    squad_rawdata['MC_D'] =( ( ( squad_rawdata['cmd_key'] * 5) + (squad_rawdata['cmd_green'] * 3) + (squad_rawdata['cmd_blue'] * 1) ) / 42)
    squad_rawdata.MC_D= squad_rawdata.MC_D.round(1)

    # calculates Central_midfielder_Support score
    squad_rawdata['cms_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['cms_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Déc'] + squad_rawdata['Col'] )
    squad_rawdata['cms_blue'] = ( squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Apl'] + squad_rawdata['Vis'] )
    squad_rawdata['MC_S'] =( ( ( squad_rawdata['cms_key'] * 5) + (squad_rawdata['cms_green'] * 3) + (squad_rawdata['cms_blue'] * 1) ) / 41)
    squad_rawdata.MC_S= squad_rawdata.MC_S.round(1)

    # calculates Central_midfielder_Attack score
    squad_rawdata['cma_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['cma_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] )
    squad_rawdata['cma_blue'] = ( squad_rawdata['Tir'] + squad_rawdata['Tcl'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Col'] + squad_rawdata['Vis'] )
    squad_rawdata['MC_A'] =( ( ( squad_rawdata['cma_key'] * 5) + (squad_rawdata['cma_green'] * 3) + (squad_rawdata['cma_blue'] * 1) ) / 39)
    squad_rawdata.MC_A= squad_rawdata.MC_A.round(1)

    # calculates Deep_lying_playmaker_Defend score
    squad_rawdata['dlpd_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['dlpd_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Col'] + squad_rawdata['Vis'] )
    squad_rawdata['dlpd_blue'] = ( squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Pla'] + squad_rawdata['Équ'] )
    squad_rawdata['Meneur_Ret_D'] =( ( ( squad_rawdata['dlpd_key'] * 5) + (squad_rawdata['dlpd_green'] * 3) + (squad_rawdata['dlpd_blue'] * 1) ) / 45)
    squad_rawdata.Meneur_Ret_D= squad_rawdata.Meneur_Ret_D.round(1)

    # calculates Deep_lying_playmaker_Support score
    squad_rawdata['dlps_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['dlps_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Col'] + squad_rawdata['Vis'] )
    squad_rawdata['dlps_blue'] = ( squad_rawdata['Ant'] + squad_rawdata['Apl'] + squad_rawdata['Pla'] + squad_rawdata['Équ'] )
    squad_rawdata['Meneur_Ret_S'] =( ( ( squad_rawdata['dlps_key'] * 5) + (squad_rawdata['dlps_green'] * 3) + (squad_rawdata['dlps_blue'] * 1) ) / 45)
    squad_rawdata.Meneur_Ret_S= squad_rawdata.Meneur_Ret_S.round(1)

    # calculates Defensive_midfielder_Defend score
    squad_rawdata['dmd_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['dmd_green'] = ( squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['dmd_blue'] = ( squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Agr'] + squad_rawdata['Sgf'] + squad_rawdata['Pui'] + squad_rawdata['Déc'] )
    squad_rawdata['MD_Def'] =( ( ( squad_rawdata['dmd_key'] * 5) + (squad_rawdata['dmd_green'] * 3) + (squad_rawdata['dmd_blue'] * 1) ) / 41)
    squad_rawdata.MD_Def= squad_rawdata.MD_Def.round(1)

    # calculates Defensive_midfielder_Support score
    squad_rawdata['dms_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['dms_green'] = ( squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['dms_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Agr'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Pui'] )
    squad_rawdata['MD_Sup'] =( ( ( squad_rawdata['dms_key'] * 5) + (squad_rawdata['dms_green'] * 3) + (squad_rawdata['dms_blue'] * 1) ) / 42)
    squad_rawdata.MD_Sup= squad_rawdata.MD_Sup.round(1)

    # calculates Enganche_Support score
    squad_rawdata['engs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['engs_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Vis'] )
    squad_rawdata['engs_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Ant'] + squad_rawdata['Ins'] + squad_rawdata['Apl'] + squad_rawdata['Col'] + squad_rawdata['Agi'] )
    squad_rawdata['Enganche'] =( ( ( squad_rawdata['engs_key'] * 5) + (squad_rawdata['engs_green'] * 3) + (squad_rawdata['engs_blue'] * 1) ) / 44)
    squad_rawdata.Enganche= squad_rawdata.Enganche.round(1)

    # calculates Half_back_Defend score
    squad_rawdata['hbd_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['hbd_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['hbd_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Agr'] + squad_rawdata['Crg'] + squad_rawdata['Saut'] + squad_rawdata['Pui'] )
    squad_rawdata['Demi'] =( ( ( squad_rawdata['hbd_key'] * 5) + (squad_rawdata['hbd_green'] * 3) + (squad_rawdata['hbd_blue'] * 1) ) / 50)
    squad_rawdata.Demi= squad_rawdata.Demi.round(1)

    # calculates Inside_forward_Support score
    squad_rawdata['ifs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['ifs_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Fin'] + squad_rawdata['Ctr'] + squad_rawdata['Tec'] + squad_rawdata['Apl'] + squad_rawdata['Agi'] )
    squad_rawdata['ifs_blue'] = ( squad_rawdata['Tir'] + squad_rawdata['Pas'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Ins'] + squad_rawdata['Vis'] + squad_rawdata['Équ'] )
    squad_rawdata['Att_Int_S'] =( ( ( squad_rawdata['ifs_key'] * 5) + (squad_rawdata['ifs_green'] * 3) + (squad_rawdata['ifs_blue'] * 1) ) / 45)
    squad_rawdata.Att_Int_S= squad_rawdata.Att_Int_S.round(1)

    # calculates Inside_forward_Attack score
    squad_rawdata['ifa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['ifa_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Fin'] + squad_rawdata['Ctr'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Apl'] + squad_rawdata['Agi'] )
    squad_rawdata['ifa_blue'] = ( squad_rawdata['Tir'] + squad_rawdata['Pas'] + squad_rawdata['Sgf'] + squad_rawdata['Ins'] + squad_rawdata['Équ'] )
    squad_rawdata['Att_Int_A'] =( ( ( squad_rawdata['ifa_key'] * 5) + (squad_rawdata['ifa_green'] * 3) + (squad_rawdata['ifa_blue'] * 1) ) / 46)
    squad_rawdata.Att_Int_A= squad_rawdata.Att_Int_A.round(1)

    # calculates Inverted_winger_Support score
    squad_rawdata['iws_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['iws_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Agi'] )
    squad_rawdata['iws_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Tir'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Vis'] + squad_rawdata['Équ'] )
    squad_rawdata['Ail_Int_S'] =( ( ( squad_rawdata['iws_key'] * 5) + (squad_rawdata['iws_green'] * 3) + (squad_rawdata['iws_blue'] * 1) ) / 42)
    squad_rawdata.Ail_Int_S= squad_rawdata.Ail_Int_S.round(1)

    # calculates Inverted_winger_Attack score
    squad_rawdata['iwa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['iwa_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Agi'] )
    squad_rawdata['iwa_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Tir'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Ins'] + squad_rawdata['Apl'] + squad_rawdata['Vis'] + squad_rawdata['Équ'] )
    squad_rawdata['Ail_Int_A'] =( ( ( squad_rawdata['iwa_key'] * 5) + (squad_rawdata['iwa_green'] * 3) + (squad_rawdata['iwa_blue'] * 1) ) / 44)
    squad_rawdata.Ail_Int_A= squad_rawdata.Ail_Int_A.round(1)

    # calculates Mezzala_Support score
    squad_rawdata['mezs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['mezs_green'] = ( squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] )
    squad_rawdata['mezs_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Tir'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Vis'] + squad_rawdata['Équ'] )
    squad_rawdata['Mezzal_S'] =( ( ( squad_rawdata['mezs_key'] * 5) + (squad_rawdata['mezs_green'] * 3) + (squad_rawdata['mezs_blue'] * 1) ) / 40)
    squad_rawdata.Mezzal_S= squad_rawdata.Mezzal_S.round(1)

    # calculates Mezzala_Attack score
    squad_rawdata['meza_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['meza_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Vis'] )
    squad_rawdata['meza_blue'] = ( squad_rawdata['Fin'] + squad_rawdata['Ctr'] + squad_rawdata['Tir'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Ins'] + squad_rawdata['Équ'] )
    squad_rawdata['Mezzal_A'] =( ( ( squad_rawdata['meza_key'] * 5) + (squad_rawdata['meza_green'] * 3) + (squad_rawdata['meza_blue'] * 1) ) / 45)
    squad_rawdata.Mezzal_A= squad_rawdata.Mezzal_A.round(1)

    # calculates Raumdeuter_Attack score
    squad_rawdata['raua_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['raua_green'] = ( squad_rawdata['Fin'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Équ'] )
    squad_rawdata['raua_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Tec'] )
    squad_rawdata['Raumd_A'] =( ( ( squad_rawdata['raua_key'] * 5) + (squad_rawdata['raua_green'] * 3) + (squad_rawdata['raua_blue'] * 1) ) / 43)
    squad_rawdata.Raumd_A= squad_rawdata.Raumd_A.round(1)

    # calculates Regista_Support score
    squad_rawdata['regs_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['regs_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Ins'] + squad_rawdata['Apl'] + squad_rawdata['Col'] + squad_rawdata['Vis'] )
    squad_rawdata['regs_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Tir'] + squad_rawdata['Ant'] + squad_rawdata['Équ'] )
    squad_rawdata['Regista'] =( ( ( squad_rawdata['regs_key'] * 5) + (squad_rawdata['regs_green'] * 3) + (squad_rawdata['regs_blue'] * 1) ) / 51)
    squad_rawdata.Regista= squad_rawdata.Regista.round(1)

    # calculates Roaming_playmaker_Support score
    squad_rawdata['rps_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['rps_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Col'] + squad_rawdata['Vis'] )
    squad_rawdata['rps_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Tir'] + squad_rawdata['Ctn'] + squad_rawdata['Pla'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] )
    squad_rawdata['Meneur_Free'] =( ( ( squad_rawdata['rps_key'] * 5) + (squad_rawdata['rps_green'] * 3) + (squad_rawdata['rps_blue'] * 1) ) / 53)
    squad_rawdata.Meneur_Free= squad_rawdata.Meneur_Free.round(1)

    # calculates Segundo_volante_Support score
    squad_rawdata['svs_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['svs_green'] = ( squad_rawdata['Mar'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Apl'] + squad_rawdata['Pla'] )
    squad_rawdata['svs_blue'] = ( squad_rawdata['Fin'] + squad_rawdata['Ctr'] + squad_rawdata['Tir'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Équ'] + squad_rawdata['Pui'] )
    squad_rawdata['Segundo_S'] =( ( ( squad_rawdata['svs_key'] * 5) + (squad_rawdata['svs_green'] * 3) + (squad_rawdata['svs_blue'] * 1) ) / 44)
    squad_rawdata.Segundo_S= squad_rawdata.Segundo_S.round(1)

    # calculates Segundo_volante_Attack score
    squad_rawdata['sva_key'] = ( squad_rawdata['Vol'] + squad_rawdata['End'] + squad_rawdata['Acc'] + squad_rawdata['Vit'] )
    squad_rawdata['sva_green'] = ( squad_rawdata['Fin'] + squad_rawdata['Tir'] + squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Ant'] + squad_rawdata['Apl'] + squad_rawdata['Pla'] )
    squad_rawdata['sva_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Mar'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Équ'] )
    squad_rawdata['Segundo_A'] =( ( ( squad_rawdata['sva_key'] * 5) + (squad_rawdata['sva_green'] * 3) + (squad_rawdata['sva_blue'] * 1) ) / 47)
    squad_rawdata.Segundo_A= squad_rawdata.Segundo_A.round(1)

    # calculates Shadow_striker_Attack score
    squad_rawdata['ssa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['ssa_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Fin'] + squad_rawdata['Ctr'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Apl'] )
    squad_rawdata['ssa_blue'] = ( squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] )
    squad_rawdata['MO_SS'] =( ( ( squad_rawdata['ssa_key'] * 5) + (squad_rawdata['ssa_green'] * 3) + (squad_rawdata['ssa_blue'] * 1) ) / 44)
    squad_rawdata.MO_SS= squad_rawdata.MO_SS.round(1)

    # calculates Wide_midfielder_Defend score
    squad_rawdata['wmd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['wmd_green'] = ( squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Pla'] + squad_rawdata['Col'] )
    squad_rawdata['wmd_blue'] = ( squad_rawdata['Cen'] + squad_rawdata['Ctr'] + squad_rawdata['Mar'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] )
    squad_rawdata['MLat_D'] =( ( ( squad_rawdata['wmd_key'] * 5) + (squad_rawdata['wmd_green'] * 3) + (squad_rawdata['wmd_blue'] * 1) ) / 44)
    squad_rawdata.MLat_D= squad_rawdata.MLat_D.round(1)

    # calculates Wide_midfielder_Support score
    squad_rawdata['wms_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['wms_green'] = ( squad_rawdata['Pas'] + squad_rawdata['Tcl'] + squad_rawdata['Déc'] + squad_rawdata['Col'] )
    squad_rawdata['wms_blue'] = ( squad_rawdata['Cen'] + squad_rawdata['Ctr'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Apl'] + squad_rawdata['Pla'] + squad_rawdata['Vis'] )
    squad_rawdata['MLat_S'] =( ( ( squad_rawdata['wms_key'] * 5) + (squad_rawdata['wms_green'] * 3) + (squad_rawdata['wms_blue'] * 1) ) / 41)
    squad_rawdata.MLat_S= squad_rawdata.MLat_S.round(1)

    # calculates Wide_midfielder_Attack score
    squad_rawdata['wma_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['wma_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Déc'] + squad_rawdata['Col'] )
    squad_rawdata['wma_blue'] = ( squad_rawdata['Tcl'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Apl'] + squad_rawdata['Vis'] )
    squad_rawdata['MLat_A'] =( ( ( squad_rawdata['wma_key'] * 5) + (squad_rawdata['wma_green'] * 3) + (squad_rawdata['wma_blue'] * 1) ) / 41)
    squad_rawdata.MLat_A= squad_rawdata.MLat_A.round(1)

    # calculates Wide_target_forward_Support score
    squad_rawdata['wtfs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['wtfs_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Crg'] + squad_rawdata['Col'] + squad_rawdata['Saut'] + squad_rawdata['Pui'] )
    squad_rawdata['wtfs_blue'] = ( squad_rawdata['Cen'] + squad_rawdata['Ctr'] + squad_rawdata['Ant'] + squad_rawdata['Apl'] + squad_rawdata['Équ'] )
    squad_rawdata['Pivot_Exc_S'] =( ( ( squad_rawdata['wtfs_key'] * 5) + (squad_rawdata['wtfs_green'] * 3) + (squad_rawdata['wtfs_blue'] * 1) ) / 40)
    squad_rawdata.Pivot_Exc_S= squad_rawdata.Pivot_Exc_S.round(1)

    # calculates Wide_target_forward_Attack score
    squad_rawdata['wtfa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['wtfa_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Crg'] + squad_rawdata['Apl'] + squad_rawdata['Saut'] + squad_rawdata['Pui'] )
    squad_rawdata['wtfa_blue'] = ( squad_rawdata['Cen'] + squad_rawdata['Fin'] + squad_rawdata['Ctr'] + squad_rawdata['Ant'] + squad_rawdata['Col'] + squad_rawdata['Équ'] )
    squad_rawdata['Pivot_Exc_A'] =( ( ( squad_rawdata['wtfa_key'] * 5) + (squad_rawdata['wtfa_green'] * 3) + (squad_rawdata['wtfa_blue'] * 1) ) / 41)
    squad_rawdata.Pivot_Exc_A= squad_rawdata.Pivot_Exc_A.round(1)

    # calculates Winger_Support score
    squad_rawdata['ws_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['ws_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Tec'] + squad_rawdata['Agi'] )
    squad_rawdata['ws_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Apl'] + squad_rawdata['Équ'] )
    squad_rawdata['Ail_S'] =( ( ( squad_rawdata['ws_key'] * 5) + (squad_rawdata['ws_green'] * 3) + (squad_rawdata['ws_blue'] * 1) ) / 36)
    squad_rawdata.Ail_S= squad_rawdata.Ail_S.round(1)

    # calculates Winger_Attack score
    squad_rawdata['wa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['End'] + squad_rawdata['Vol'] )
    squad_rawdata['wa_green'] = ( squad_rawdata['Cen'] + squad_rawdata['Drb'] + squad_rawdata['Tec'] + squad_rawdata['Agi'] )
    squad_rawdata['wa_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Ant'] + squad_rawdata['Ins'] + squad_rawdata['Apl'] + squad_rawdata['Équ'] )
    squad_rawdata['Ail_A'] =( ( ( squad_rawdata['wa_key'] * 5) + (squad_rawdata['wa_green'] * 3) + (squad_rawdata['wa_blue'] * 1) ) / 38)
    squad_rawdata.Ail_A= squad_rawdata.Ail_A.round(1)

    # calculates Advanced_forward_Attack score
    squad_rawdata['afa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['afa_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Apl'] )
    squad_rawdata['afa_blue'] = ( squad_rawdata['Pas'] + squad_rawdata['Ant'] + squad_rawdata['Déc'] + squad_rawdata['Vol'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] + squad_rawdata['End'] )
    squad_rawdata['Att_Avanc'] =( ( ( squad_rawdata['afa_key'] * 5) + (squad_rawdata['afa_green'] * 3) + (squad_rawdata['afa_blue'] * 1) ) / 37)
    squad_rawdata.Att_Avanc= squad_rawdata.Att_Avanc.round(1)

    # calculates Complete_forward_Support score
    squad_rawdata['cfs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['cfs_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Têt'] + squad_rawdata['Tir'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Vis'] + squad_rawdata['Agi'] + squad_rawdata['Pui'] )
    squad_rawdata['cfs_blue'] = ( squad_rawdata['Col'] + squad_rawdata['Vol'] + squad_rawdata['Équ'] + squad_rawdata['Saut'] + squad_rawdata['End'] )
    squad_rawdata['Att_Comp_S'] =( ( ( squad_rawdata['cfs_key'] * 5) + (squad_rawdata['cfs_green'] * 3) + (squad_rawdata['cfs_blue'] * 1) ) / 59)
    squad_rawdata.Att_Comp_S= squad_rawdata.Att_Comp_S.round(1)

    # calculates Complete_forward_Attack score
    squad_rawdata['cfa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['cfa_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Têt'] + squad_rawdata['Tec'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Apl'] + squad_rawdata['Agi'] + squad_rawdata['Pui'] )
    squad_rawdata['cfa_blue'] = ( squad_rawdata['Tir'] + squad_rawdata['Pas'] + squad_rawdata['Déc'] + squad_rawdata['Col'] + squad_rawdata['Vis'] + squad_rawdata['Vol'] + squad_rawdata['Équ'] + squad_rawdata['Saut'] + squad_rawdata['End'] )
    squad_rawdata['Att_Comp_A'] =( ( ( squad_rawdata['cfa_key'] * 5) + (squad_rawdata['cfa_green'] * 3) + (squad_rawdata['cfa_blue'] * 1) ) / 51)
    squad_rawdata.Att_Comp_A= squad_rawdata.Att_Comp_A.round(1)

    # calculates Deep_lying_forward_Support score
    squad_rawdata['dlfs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['dlfs_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Col'] )
    squad_rawdata['dlfs_blue'] = ( squad_rawdata['Ant'] + squad_rawdata['Ins'] + squad_rawdata['Vis'] + squad_rawdata['Équ'] + squad_rawdata['Pui'] )
    squad_rawdata['Att_Retr_S'] =( ( ( squad_rawdata['dlfs_key'] * 5) + (squad_rawdata['dlfs_green'] * 3) + (squad_rawdata['dlfs_blue'] * 1) ) / 41)
    squad_rawdata.Att_Retr_S= squad_rawdata.Att_Retr_S.round(1)

    # calculates Deep_lying_forward_Attack score
    squad_rawdata['dlfa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['dlfa_green'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Col'] )
    squad_rawdata['dlfa_blue'] = ( squad_rawdata['Drb'] + squad_rawdata['Ant'] + squad_rawdata['Ins'] + squad_rawdata['Vis'] + squad_rawdata['Équ'] + squad_rawdata['Pui'] )
    squad_rawdata['Att_Retr_A'] =( ( ( squad_rawdata['dlfa_key'] * 5) + (squad_rawdata['dlfa_green'] * 3) + (squad_rawdata['dlfa_blue'] * 1) ) / 42)
    squad_rawdata.Att_Retr_A= squad_rawdata.Att_Retr_A.round(1)

    # calculates False_nine_Support score
    squad_rawdata['f9s_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['f9s_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] + squad_rawdata['Vis'] + squad_rawdata['Agi'] )
    squad_rawdata['f9s_blue'] = ( squad_rawdata['Ant'] + squad_rawdata['Ins'] + squad_rawdata['Col'] + squad_rawdata['Équ'] )
    squad_rawdata['Faux_9'] =( ( ( squad_rawdata['f9s_key'] * 5) + (squad_rawdata['f9s_green'] * 3) + (squad_rawdata['f9s_blue'] * 1) ) / 46)
    squad_rawdata.Faux_9= squad_rawdata.Faux_9.round(1)

    # calculates Poacher_Attack score
    squad_rawdata['pa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['pa_green'] = ( squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Apl'] )
    squad_rawdata['pa_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Têt'] + squad_rawdata['Tec'] + squad_rawdata['Déc'] )
    squad_rawdata['Renard'] =( ( ( squad_rawdata['pa_key'] * 5) + (squad_rawdata['pa_green'] * 3) + (squad_rawdata['pa_blue'] * 1) ) / 28)
    squad_rawdata.Renard= squad_rawdata.Renard.round(1)

    # calculates Pressing_forward_Defend score
    squad_rawdata['pfd_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['pfd_green'] = ( squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Déc'] + squad_rawdata['Col'] + squad_rawdata['Vol'] + squad_rawdata['End'] )
    squad_rawdata['pfd_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] + squad_rawdata['Pui'] )
    squad_rawdata['Att_Press_D'] =( ( ( squad_rawdata['pfd_key'] * 5) + (squad_rawdata['pfd_green'] * 3) + (squad_rawdata['pfd_blue'] * 1) ) / 42)
    squad_rawdata.Att_Press_D= squad_rawdata.Att_Press_D.round(1)

    # calculates Pressing_forward_Support score
    squad_rawdata['pfs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['pfs_green'] = ( squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Déc'] + squad_rawdata['Col'] + squad_rawdata['Vol'] + squad_rawdata['End'] )
    squad_rawdata['pfs_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Apl'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] + squad_rawdata['Pui'] )
    squad_rawdata['Att_Press_S'] =( ( ( squad_rawdata['pfs_key'] * 5) + (squad_rawdata['pfs_green'] * 3) + (squad_rawdata['pfs_blue'] * 1) ) / 44)
    squad_rawdata.Att_Press_S= squad_rawdata.Att_Press_S.round(1)

    # calculates Pressing_forward_Attack score
    squad_rawdata['pfa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['pfa_green'] = ( squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Crg'] + squad_rawdata['Apl'] + squad_rawdata['Col'] + squad_rawdata['Vol'] + squad_rawdata['End'] )
    squad_rawdata['pfa_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Sgf'] + squad_rawdata['Ctn'] + squad_rawdata['Déc'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] + squad_rawdata['Pui'] )
    squad_rawdata['Att_Press_A'] =( ( ( squad_rawdata['pfa_key'] * 5) + (squad_rawdata['pfa_green'] * 3) + (squad_rawdata['pfa_blue'] * 1) ) / 43)
    squad_rawdata.Att_Press_A= squad_rawdata.Att_Press_A.round(1)
        
    # calculates Target_forward_Support score
    squad_rawdata['tfs_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['tfs_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Crg'] + squad_rawdata['Col'] + squad_rawdata['Équ'] + squad_rawdata['Saut'] + squad_rawdata['Pui'] )
    squad_rawdata['tfs_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Apl'] )
    squad_rawdata['Pivot_S'] =( ( ( squad_rawdata['tfs_key'] * 5) + (squad_rawdata['tfs_green'] * 3) + (squad_rawdata['tfs_blue'] * 1) ) / 39)
    squad_rawdata.Pivot_S= squad_rawdata.Pivot_S.round(1)

    # calculates Target_forward_Attack score
    squad_rawdata['tfa_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['tfa_green'] = ( squad_rawdata['Têt'] + squad_rawdata['Crg'] + squad_rawdata['Sgf'] + squad_rawdata['Apl'] + squad_rawdata['Équ'] + squad_rawdata['Saut'] + squad_rawdata['Pui'] )
    squad_rawdata['tfa_blue'] = ( squad_rawdata['Ctr'] + squad_rawdata['Agr'] + squad_rawdata['Ant'] + squad_rawdata['Déc'] + squad_rawdata['Col'] )
    squad_rawdata['Pivot_A'] =( ( ( squad_rawdata['tfa_key'] * 5) + (squad_rawdata['tfa_green'] * 3) + (squad_rawdata['tfa_blue'] * 1) ) / 41)
    squad_rawdata.Pivot_A= squad_rawdata.Pivot_A.round(1)

    # calculates Trequartista_Attack score
    squad_rawdata['trea_key'] = ( squad_rawdata['Acc'] + squad_rawdata['Vit'] + squad_rawdata['Fin'] )
    squad_rawdata['trea_green'] = ( squad_rawdata['Drb'] + squad_rawdata['Ctr'] + squad_rawdata['Pas'] + squad_rawdata['Tec'] + squad_rawdata['Sgf'] + squad_rawdata['Déc'] + squad_rawdata['Ins'] + squad_rawdata['Apl'] + squad_rawdata['Vis'] )
    squad_rawdata['trea_blue'] = ( squad_rawdata['Ant'] + squad_rawdata['Agi'] + squad_rawdata['Équ'] )
    squad_rawdata['Att_Soutien'] =( ( ( squad_rawdata['trea_key'] * 5) + (squad_rawdata['trea_green'] * 3) + (squad_rawdata['trea_blue'] * 1) ) / 45)
    squad_rawdata.Att_Soutien= squad_rawdata.Att_Soutien.round(1)
    
    # Filter out columns containing 'key', 'green', or 'blue' in their names
    filtered_columns = [col for col in squad_rawdata.columns if not any(keyword in col.lower() for keyword in ['key', 'green', 'blue', 'idu', 'enr', 'nnal', 'nat', 'média'])]
    squad_rawdata_filtered = squad_rawdata[filtered_columns]
    column_headers = squad_rawdata_filtered.columns.tolist()

    # Convert the DataFrame to a list of lists
    players_data = squad_rawdata_filtered.values.tolist()

    return column_headers, players_data



if __name__ == '__main__':
    app.run(debug=True)