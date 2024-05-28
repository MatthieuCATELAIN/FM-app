import React, { useEffect, useState } from 'react';
import img from "../../../images/portrait.svg";
import axios from "axios";


const GK_roles = [
  "G", "GL_D", "GL_S", "GL_A"
];

const DEF_roles = [
  "DC_Rel_D",	"DC_Rel_St", 	"DC_Rel_Co",	"DC_Def",	"DC_Stop",	"DC_Couv", "Lib_Def",	"Lib_Sup",	"DC_Strict_D",	"DC_Strict_St",	"DC_Strict_Co"
];

const MID_roles = [
  "MD_Senti", "MD_Recup_D", "MD_Recup_S", "Meneur_Free", "Meneur_Ret_D",	"Meneur_Ret_S",	"MD_Def",	"MD_Sup", "Demi", "Segundo_S",	"Segundo_A", "B2B", "Carrilero",	"MC_D",	"MC_S",	"MC_A", "Mezzal_S"	,"Mezzal_A", "MO_S"	,"MO_A", "Meneur_Ava_S", "Meneur_Ava_A", "MO_SS"
];

const LAT_roles = [
  "Lat_Comp_S",	"Lat_Comp_A",	"Arr_Lat_D",	"Arr_Lat_S",	"Arr_Lat_A",	"Lat_Inver",	"Lat_Int_D",	"Lat_Int_S",	"Lat_Int_A", "Lat_Off_D",	"Lat_Off_S",	"Lat_Off_A"
];

const AIL_roles = [
  "MLat_D",	"MLat_S",	"MLat_A", "Att_Int_S",	"Att_Int_A",	"Ail_Int_S",	"Ail_Int_A",	"Mezzal_S",	"Mezzal_A",	"Raumd_A",	"Regista",	"Meneur_Free", "Pivot_Exc_S",	"Pivot_Exc_A",	"Ail_S",	"Ail_A"
];

const ATT_roles = [
  "Att_Avanc", "Att_Comp_S", "Att_Comp_A", "Att_Retr_S", "Att_Retr_A",
  "Faux_9", "Renard", "Att_Press_D", "Att_Press_S", "Att_Press_A",
  "Pivot_S", "Pivot_A", "Att_Soutien"
];

function Position(props) {

  const [selectedPlayer, setSelectedPlayer] = useState();
  const [squadData, setSquadData] = useState([]);
  const [columnHeaders, setColumnHeaders] = useState([]);
  const [selectedRole, setSelectedRole] = useState("");

  const handleRoleChange = (event) => {
    const role = event.target.value;
    setSelectedRole(role);
    setSelectedPlayer("");
    props.onRoleChange(role);
    };

  const handlePlayerChange = (event) => {
    setSelectedPlayer(event.target.value);
  };

  const getColumnIndex = (role) => {
    return columnHeaders.indexOf(role);
  };

  useEffect(() => {
    const fetchData = async () => {
        try {
            const response = await axios.get('/get_squad_data');
            setColumnHeaders(response.data.column_headers);
            setSquadData(response.data.player_data);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    fetchData();
}, []);

  const getSortedColumnValues = () => {
    const columnIndex = getColumnIndex(selectedRole);
    if (columnIndex !== -1) {
      const sortableData = [...squadData];
      sortableData.sort((a, b) => {
        const valueA = b[columnIndex];
        const valueB = a[columnIndex];

        if (valueA < valueB) {
          return -1;
        }
        if (valueA > valueB) {
          return 1;
        }
        return 0;
      });

      return sortableData.slice(0, 5).map(row => ({
        name: row[1],
        note: row[columnIndex]
      }));
    }
    return [];
  };

  useEffect(() => {
    setSelectedRole(props.selectedRole);
  }, [props.selectedRole]);

  return (
    <div className="position">

      {props.selectedPlayer && (
  <div>
    <strong>{props.selectedPlayer}</strong>
  </div>
)}
      <div className="playerpoolcandidate">
        <img src={img} alt="profile" />
      </div>

      {props.positionName && (
        <div>
          { props.positionName === "ATTACK" && (
            <select value={selectedRole || ""} onChange={handleRoleChange}>
            <option value="">Select Role</option>
            {ATT_roles.map(role => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}  
          </select> 
          )}
          { props.positionName === "GK" && (
            <select value={selectedRole || ""} onChange={handleRoleChange}>
            <option value="">Select Role</option>
            {GK_roles.map(role => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}  
          </select> 
          )}
          { props.positionName === "DEF" && (
            <select value={selectedRole || ""} onChange={handleRoleChange}>
            <option value="">Select Role</option>
            {DEF_roles.map(role => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}  
          </select> 
          )}
                    { props.positionName === "LAT" && (
          <select value={selectedRole || ""} onChange={handleRoleChange}>
            <option value="">Select Role</option>
            {LAT_roles.map(role => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}  
          </select> 
          )}
          { props.positionName === "MID" && (
          <select value={selectedRole || ""} onChange={handleRoleChange}>
            <option value="">Select Role</option>
            {MID_roles.map(role => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}  
          </select> 
          )}
          { props.positionName === "AIL" && (
          <select value={selectedRole || ""} onChange={handleRoleChange}>
            <option value="">Select Role</option>
            {AIL_roles.map(role => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}  
          </select> 
          )}
          {selectedRole && (
            <div>
              <select value={selectedPlayer} onChange={handlePlayerChange}>
                <option value="">Select Player</option>
                {getSortedColumnValues().map(({ name, note }) => (
                  <option key={name} value={name}>
                    {name} ({note})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      )}

    </div>
  );
}

export default Position;