package com.example.mdp_group_28;

import org.json.JSONArray;

public class DataManager {
    private static DataManager instance;
    private JSONArray robotPositions;
    private StringBuilder messageBuffer = new StringBuilder();


    private DataManager() {
        // Private constructor to prevent instantiation
    }

    public static DataManager getInstance() {
        if (instance == null) {
            instance = new DataManager();
        }
        return instance;
    }

    public void setRobotPositions(JSONArray robotPositions) {
        this.robotPositions = robotPositions;
    }

    public JSONArray getRobotPositions() {
        return robotPositions;
    }
    public void appendToMessageBuffer(String messagePart) {
        messageBuffer.append(messagePart);
    }

    public String getBufferedMessage() {
        return messageBuffer.toString();
    }

    public void clearMessageBuffer() {
        messageBuffer.setLength(0);
    }
}
