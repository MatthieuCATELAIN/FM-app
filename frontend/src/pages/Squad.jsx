import React from "react";
import SideBar from "../components/SideBar";
import "../globals.css"; 
import SquadBuildingPage from "../components/squad/squadbuild";

const Squad = () => {

      return (
        <div className="container">
          <div className="sidebar">
          <SideBar/>
          </div>
          <div className="main-content">
          <SquadBuildingPage />
          </div>
        </div>
      )
    }

export default Squad;