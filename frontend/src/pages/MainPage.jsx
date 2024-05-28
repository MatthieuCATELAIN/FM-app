import React from "react";
import SideBar from "../components/SideBar";
import "../globals.css"; 

const MainPage = () => {

      return (
        <div className="container">
          <div className="sidebar">
          <SideBar/>
          </div>
          <div className="main-content">
          <h1>About the project</h1>
          <p>This project has been created with the inspiration of the work of squirrel_plays.</p>
          <p>The two views used in the game are created by him.</p>
          <p>I rework his table of characteristics and the way of calculating score.</p>
          <p>Rest of the project is mine.</p>
          <h1>How to use it ?</h1>
          <p>Use the view for team in game, and export it with a format of HTML.</p>
          <p>Upload your team.html.</p>
          <p>You are free to navigate on the classic view and the complex view.</p>
          <p>On the squad page, you can create manually your best 11.</p>
          <p>One of the feature I started to develop and have to improve.</p>
           <p>With a formation and 11 chosen roles, you can generate the best 11 !</p>
           <p>You have an upload transfer file function, working as same as team file, but using the view for transfer in game.</p>
           <p>You have a view to compare players and add the best one to your squad for winning many titles.</p>
          </div>
        </div>
      )
    }

export default MainPage;