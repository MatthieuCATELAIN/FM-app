import React from "react";
import Position from "../components/position";
import "./352style.css";

function Formation352({ bestTeam, bestTeamRoles, handleRoleChange }) {

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

  const renderPosition = (playerIndex, positionName) => {
    const player = bestTeam ? bestTeam[`player${playerIndex}`] : null;
    const role = bestTeamRoles ? bestTeamRoles[`player${playerIndex}`] : null;

    return (
      <Position
        playerName={players[playerIndex]}
        positionName={positionName}
        onRoleChange={(role) => handleRoleChange(players[playerIndex], role)}
        selectedPlayer={player ? `${player.Nom} (${player.Note})` : ""}
        selectedRole={role || ""}
      />
    );
  };


  return (
    <div className="formation352">
      <div className="attackLane352">
        {renderPosition(0, "ATTACK")}
        {renderPosition(1, "ATTACK")}
      </div>
      <div className="midLane352">
        {renderPosition(2, "LAT")}
        {renderPosition(3, "MID")}
        {renderPosition(4, "MID")}
        {renderPosition(5, "MID")}
        {renderPosition(6, "LAT")}
      </div>
      <div className="backLane352">
        {renderPosition(7, "DEF")}
        {renderPosition(8, "DEF")}
        {renderPosition(9, "DEF")}
      </div>
      <div className="gkLane352">
        {renderPosition(10, "GK")}
      </div>
    </div>
  );
}

export default Formation352;
