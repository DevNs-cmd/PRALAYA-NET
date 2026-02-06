import React from 'react';
import VSLAMCameraFeed from './VSLAMCameraFeed';

const DroneGrid = ({ drones }) => {
    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '12px',
            marginTop: '12px',
            maxHeight: '800px',
            overflowY: 'auto',
            paddingRight: '4px'
        }}>
            {drones.map(drone => (
                <VSLAMCameraFeed key={drone.id} drone={drone} />
            ))}

            {drones.length === 0 && (
                <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '20px', color: '#666' }}>
                    No Active Drones via V-SLAM Link
                </div>
            )}
        </div>
    );
};

export default DroneGrid;
