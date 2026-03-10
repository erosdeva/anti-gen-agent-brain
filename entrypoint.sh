#!/bin/bash
# Start the first process and put it in the background
python agent.py &

# Start the second process
streamlit run dashboard.py --server.port=8080 --server.address=0.0.0.0