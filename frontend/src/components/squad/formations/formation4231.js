import React from "react";
import Position from "../components/position";
import "./4231style.css";

function Formation4231({ bestTeam, bestTeamRoles, handleRoleChange }) {

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
    <div className="formation4231">
      <div className="attackLane4231">
        {renderPosition(0, "ATTACK")}
      </div>
      <div className="midLaneFront4231">
        {renderPosition(4, "AIl")}
        {renderPosition(5, "MID")}
        {renderPosition(5, "AIL")}
      </div>
      <div className="midLaneBack4231">
        {renderPosition(4, "MID")}
        {renderPosition(5, "MID")}
      </div>
      <div className="backLane4231">
        {renderPosition(6, "LAT")}
        {renderPosition(7, "DEF")}
        {renderPosition(8, "DEF")}
        {renderPosition(9, "LAT")}
      </div>
      <div className="gkLane4231">
        {renderPosition(10, "GK")}
      </div>
    </div>
  );
}

export default Formation4231;
