import React from "react";
import Position from "../components/position";
import "./433style.css";

function Formation433({ bestTeam, bestTeamRoles, handleRoleChange }) {

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
    <div className="formation433">
      <div className="attackLane433">
        {renderPosition(0, "AIL")}
        {renderPosition(1, "ATTACK")}
        {renderPosition(2, "AIL")}
      </div>
      <div className="midLane433">
        {renderPosition(3, "MID")}
        {renderPosition(4, "MID")}
        {renderPosition(5, "MID")}
      </div>
      <div className="backLane433">
      {renderPosition(6, "LAT")}
        {renderPosition(7, "DEF")}
        {renderPosition(8, "DEF")}
        {renderPosition(9, "LAT")}
      </div>
      <div className="gkLane433">
        {renderPosition(10, "GK")}
      </div>
    </div>
  );
}

export default Formation433;
