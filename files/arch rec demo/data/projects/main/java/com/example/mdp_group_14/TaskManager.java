package com.example.mdp_group_28;

public class TaskManager {
    private static TaskManager instance;
    private boolean isTask1Started = false;
    private TaskManager(){

    }
    public static TaskManager getInstance() {
        if (instance == null) {
            instance = new TaskManager();
        }
        return instance;
    }

    public boolean isTask1Started() {
        return isTask1Started;
    }

    public void setTask1Started(boolean started) {
        this.isTask1Started = started;
    }


}
