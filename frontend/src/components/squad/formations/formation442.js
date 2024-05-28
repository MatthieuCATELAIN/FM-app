import React from "react";
import Position from "../components/position";
import "./442style.css";

function Formation442({ bestTeam, bestTeamRoles, handleRoleChange }) {

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
    <div className="formation442">
      <div className="attackLane442">
        {renderPosition(0, "ATTACK")}
        {renderPosition(1, "ATTACK")}
      </div>
      <div className="midLane442">
        {renderPosition(2, "MID")}
        {renderPosition(3, "MID")}
        {renderPosition(4, "MID")}
        {renderPosition(5, "MID")}
      </div>
      <div className="backLane442">
        {renderPosition(6, "LAT")}
        {renderPosition(7, "DEF")}
        {renderPosition(8, "DEF")}
        {renderPosition(9, "LAT")}
      </div>
      <div className="gkLane442">
        {renderPosition(10, "GK")}
      </div>
    </div>
  );
}

export default Formation442;