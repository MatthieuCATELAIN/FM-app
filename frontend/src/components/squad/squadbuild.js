import "./styles.css";
import axios from "axios";
import React, { useState, useEffect } from "react";
import Select from "react-select";
import Formation from "./components/formation";

const formations = [
  { value: "4-4-2", label: "4-4-2" },
  { value: "4-3-3", label: "4-3-3" },
  { value: "4-5-1", label: "4-5-1" },
  { value: "3-5-2", label: "3-5-2" },
  { value: "4-2-3-1", label: "4-2-3-1" }
];


const players = [
  "player0",
  "player1",
  "player2",
  "player3",
  "player4",
  "player5",
  "player6",
  "player7",
  "player8",
  "player9",
  "player10",
];


function SquadBuildingPage() {
  const [selectedOption, setSelectedOption] = useState({
    value: "4-4-2",
    label: "4-4-2"
  });
  const formation = selectedOption.value;

  const [roleToPositionMapping, setRoleToPositionMapping] = useState({});
  const [bestTeam, setBestTeam] = useState(null);
  const [bestTeamRoles, setBestTeamRoles] = useState(null);
  const [savedFormation, setSavedFormation] = useState("");
  const [teamAverage, setTeamAverage] = useState(null);

  useEffect(() => {
    const fetchDataFormation = async () => {
      try {
        const response = await axios.get('/get_formation_data');
        const fetchedFormation = response.data.formation;
        setSelectedOption({
          value: fetchedFormation,
          label: fetchedFormation
        });
        setSavedFormation(fetchedFormation);
      } catch (error) {
        console.error('Error fetching formation data:', error);
      }
    };

    fetchDataFormation();
  }, []);

  const fetchDataTeam = async () => {
    try {
      const response = await axios.get('/get_best_team_saved');
      const savedRoles = response.data.roles;
      if (savedFormation === formation) {
        setBestTeam(response.data.team);
        setBestTeamRoles(savedRoles);
        players.forEach((player, index) => handleRoleChange(player, savedRoles[`player${index}`]));
        calculateTeamAverage(response.data.team);
      } else {
        setBestTeam(null)
        setBestTeamRoles(null)
        setTeamAverage(null);
      }
    } catch (error) {
      console.error('Error fetching team data:', error);
    }
  };

  useEffect(() => {
    if (savedFormation) {
      fetchDataTeam();
    }
    // eslint-disable-next-line
  }, [savedFormation, formation]);

  
  const handlePostBestTeam = () => {
    axios.post('/get_best_team', { selected_roles: roleToPositionMapping, formation: formation })
      .then(response => {
        setBestTeam(response.data);
        fetchDataTeam();
      })
      .catch(error => {
        console.error('Error fetching the best team:', error);
      });
  };

  const handleRoleChange = (player, newRole) => {
    setRoleToPositionMapping((prevMapping) => ({
      ...prevMapping,
      [player]: newRole,
    }));
  };

  const calculateTeamAverage = (team) => {
      const playersArray = Object.values(team);
      const totalNotes = playersArray.reduce((total, player) => total + parseFloat(player.Note || 0), 0);
      const average = totalNotes / playersArray.length;
      setTeamAverage(average.toFixed(2)); 
  };

  return (
    <div className="App">
      <div className="formationSection">
        <div className="formationOverlay">
          <Formation
            formation={formation}
            bestTeam={bestTeam}
            bestTeamRoles={bestTeamRoles}
            handleRoleChange={handleRoleChange}
          />
        </div>
      </div>

      <div className="formationSelector">
        <p>Squad Builder</p>
        <Select
          value={selectedOption}
          onChange={setSelectedOption}
          options={formations}
        />
        MOYENNE : {teamAverage}
        <button onClick={handlePostBestTeam}>Get Best Team</button>
      </div>
    </div>
  );
}

export default SquadBuildingPage;
