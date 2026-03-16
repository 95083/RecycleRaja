import React, { useEffect, useState } from 'react';

const Clock = () => {
    const [time, setTime] = useState({});

    const updateClock = () => {
        const utcDate = new Date();
        setTime({
            UTC: utcDate.toUTCString(),
            EST: utcDate.toLocaleString('en-US', { timeZone: 'America/New_York' }),
            PST: utcDate.toLocaleString('en-US', { timeZone: 'America/Los_Angeles' }),
            IST: utcDate.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }),
            JST: utcDate.toLocaleString('en-US', { timeZone: 'Asia/Tokyo' }),
            GMT: utcDate.toLocaleString('en-US', { timeZone: 'Europe/London' }),
        });
    };

    useEffect(() => {
        updateClock(); // Set initial time
        const intervalId = setInterval(updateClock, 1000); // Update every second
        return () => clearInterval(intervalId); // Cleanup on component unmount
    }, []);

    return (
        <div>
            <h1>Digital Clock</h1>
            <ul>
                <li>UTC: {time.UTC}</li>
                <li>EST: {time.EST}</li>
                <li>PST: {time.PST}</li>
                <li>IST: {time.IST}</li>
                <li>JST: {time.JST}</li>
                <li>GMT: {time.GMT}</li>
            </ul>
        </div>
    );
};

export default Clock;