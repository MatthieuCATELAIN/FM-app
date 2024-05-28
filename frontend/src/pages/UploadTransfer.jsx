import React, { useState } from 'react';
import axios from "axios";
import { Button, Input, Box } from "@mui/material";
import SideBar from "../components/SideBar";
import "../globals.css"; 

const UploadTransfer = () => {
      // Component state for file and squad data
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");

  // Event handler for file input change
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setFileName(selectedFile ? selectedFile.name : "");
  };

  // Event handler for form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Make a POST request to upload the file
      const reponse = await axios.post("/upload_transfer", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log(reponse.data.message)
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  // Render the component
  return (
    <div className="container">
      <div className="sidebar">
        <SideBar />
      </div>
      <div className="main-content">
        <h1>Upload Transfer HTML File</h1>
        <form onSubmit={handleSubmit}>
          {/* Hidden file input */}
          <Input
            type="file"
            id="fileInput"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
          {/* Styled button that triggers the file input */}
          <label htmlFor="fileInput">
            <Button variant="contained" component="span">
              Choose File
            </Button>
          </label>
          <Box component="span" ml={2}>{fileName}</Box>
          <Button variant="contained" type="submit">Upload</Button>
        </form>
      </div>
    </div>
  );
};

export default UploadTransfer;