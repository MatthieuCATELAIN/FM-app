import React from "react";
import Formation442 from "../formations/formation442.js";
import Formation433 from "../formations/formation433.js";
import Formation352 from "../formations/formation352.js";
import Formation4231 from "../formations/formation4231.js";
import Formation451 from "../formations/formation451.js";
import "../styles.css";

function Formation(props) {
  const { formation, bestTeam, bestTeamRoles, handleRoleChange } = props;


  const formationComponents = {
    "4-4-2": <Formation442
    bestTeam={bestTeam}
    bestTeamRoles={bestTeamRoles}
    handleRoleChange={handleRoleChange}
     />,
    "4-3-3": <Formation433
    bestTeam={bestTeam}
    bestTeamRoles={bestTeamRoles}
    handleRoleChange={handleRoleChange}
     />,
    "3-5-2": (
      <Formation352
      bestTeam={bestTeam}
      bestTeamRoles={bestTeamRoles}
      handleRoleChange={handleRoleChange}
      />
    ),
    "4-2-3-1": 
      <Formation4231
      bestTeam={bestTeam}
      bestTeamRoles={bestTeamRoles}
      handleRoleChange={handleRoleChange}
    />,
    "4-5-1": <Formation451
    bestTeam={bestTeam}
    bestTeamRoles={bestTeamRoles}
    handleRoleChange={handleRoleChange}
     />
  };

  return <div className="formation-select">{formationComponents[formation]}</div>;
}

export default Formation;
