.loading-state {
    text-align: center;
    padding: 2rem;
    color: #666;
}

.spinner {
    width: 24px;
    height: 24px;
    border: 3px solid rgba(151, 67, 244, 0.2);
    border-radius: 50%;
    border-top-color: #9743F4;
    animation: spin 1s ease-in-out infinite;
    margin: 0 auto 10px;
}

.spinner.small {
    width: 16px;
    height: 16px;
    border-width: 2px;
    display: inline-block;
    margin: 0 5px 0 0;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.pulse {
    animation: pulse 0.3s ease;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}