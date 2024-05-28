import React, { useEffect, useState } from 'react';
import { Table, TableHead, TableRow, TableCell, TableBody, TableContainer, Paper } from '@mui/material';
import SideBar from "../components/SideBar";
import axios from "axios";
import "../globals.css"; 

const TransferView = () => {

    const [squadData, setSquadData] = useState([]);
    const [columnHeaders, setColumnHeaders] = useState([]);
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

    const handleSort = (key) => {
        let direction = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('/get_transfer_data');
                setColumnHeaders(response.data.column_headers);
                setSquadData(response.data.player_data);
            } catch (error) {   
                console.error('Error fetching data:', error);
            }
        };

        fetchData();
    }, []);


    const sortedData = () => {
        const sortableData = [...squadData];
        if (sortConfig.key !== null) {
            sortableData.sort((a, b) => {
                const valueA = a[columnHeaders.indexOf(sortConfig.key)];
                const valueB = b[columnHeaders.indexOf(sortConfig.key)];

                if (valueA < valueB) {
                    return sortConfig.direction === 'asc' ? -1 : 1;
                }
                if (valueA > valueB) {
                    return sortConfig.direction === 'asc' ? 1 : -1;
                }
                return 0;
            });
        }
        return sortableData;
    };

    return (
        <div className="container" style={{ display: 'flex' }}>
            <div className="sidebar">
                <SideBar />
            </div>
            {( squadData &&
            <div className="main-content" style={{ flex: 1, overflow: 'auto' }}>
                <TableContainer component={Paper}>
                    <Table stickyHeader aria-label="sticky table">
                        <TableHead>
                            <TableRow>
                                {columnHeaders.slice(0, 10).map((header, index) => (
                                    <TableCell key={index} onClick={() => handleSort(header)}>
                                        {header}
                                        {sortConfig.key === header && (
                                            sortConfig.direction === 'asc' ? ' ⬆️' : ' ⬇️'
                                        )}
                                    </TableCell>
                                ))}
                                {columnHeaders.slice(50).map((header, index) => (
                                    <TableCell key={index + 50} onClick={() => handleSort(header)}>
                                        {header}
                                        {sortConfig.key === header && (
                                            sortConfig.direction === 'asc' ? ' ⬆️' : ' ⬇️'
                                        )}
                                    </TableCell>
                                ))}
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {sortedData().map((row, rowIndex) => (
                                <TableRow key={rowIndex}>
                                    {row.slice(0, 10).map((value, columnIndex) => (
                                        <TableCell key={columnIndex}>{value}</TableCell>
                                    ))}
                                    {row.slice(50).map((value, columnIndex) => (
                                        <TableCell key={columnIndex + 50}>{value}</TableCell>
                                    ))}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </div>
            )}
        </div>
    );
};

export default TransferView;