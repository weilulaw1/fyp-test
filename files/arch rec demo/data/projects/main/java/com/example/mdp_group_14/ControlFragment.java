package com.example.mdp_group_28;

import static com.example.mdp_group_28.Home.refreshMessageReceivedNS;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Point;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


public class ControlFragment extends Fragment {
    private static final String TAG = "ControlFragment";

    SharedPreferences sharedPreferences;

    // Control Button
    ImageButton moveForwardImageBtn, turnRightImageBtn, moveBackImageBtn, turnLeftImageBtn,turnbleftImageBtn,turnbrightImageBtn;
    ImageButton exploreResetButton, fastestResetButton;

    private static long exploreTimer, fastestTimer;
    public static ToggleButton exploreButton, fastestButton;
    public static TextView exploreTimeTextView, fastestTimeTextView, robotStatusTextView;
    private static GridMap gridMap;

    // Timer
    public static Handler timerHandler = new Handler();

    //Button startSend;

    public static Runnable timerRunnableExplore = new Runnable() {
        @Override
        public void run() {
            long millisExplore = System.currentTimeMillis() - exploreTimer;
            int secondsExplore = (int) (millisExplore / 1000);
            int minutesExplore = secondsExplore / 60;
            secondsExplore = secondsExplore % 60;

            if (!Home.stopTimerFlag) {
                exploreTimeTextView.setText(String.format("%02d:%02d", minutesExplore,
                        secondsExplore));
                timerHandler.postDelayed(this, 500);
            }
        }
    };

    public static Runnable timerRunnableFastest = new Runnable() {
        @Override
        public void run() {
            long millisFastest = System.currentTimeMillis() - fastestTimer;
            int secondsFastest = (int) (millisFastest / 1000);
            int minutesFastest = secondsFastest / 60;
            secondsFastest = secondsFastest % 60;

            if (!Home.stopWk9TimerFlag) {
                fastestTimeTextView.setText(String.format("%02d:%02d", minutesFastest,
                        secondsFastest));
                timerHandler.postDelayed(this, 500);
            }
        }
    };


    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @SuppressLint({"WrongViewCast", "MissingInflatedId"})
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // inflate
        View root = inflater.inflate(R.layout.controls, container, false);

        // get shared preferences
        sharedPreferences = getActivity().getSharedPreferences("Shared Preferences",
                Context.MODE_PRIVATE);

        // variable initialization
        moveForwardImageBtn = Home.getUpBtn();
        turnRightImageBtn = Home.getRightBtn();
        moveBackImageBtn = Home.getDownBtn();
        turnLeftImageBtn = Home.getLeftBtn();
        turnbleftImageBtn = Home.getbLeftBtn();
        turnbrightImageBtn = Home.getbRightBtn();
        exploreTimeTextView = root.findViewById(R.id.exploreTimeTextView2);
        fastestTimeTextView = root.findViewById(R.id.fastestTimeTextView2);
        exploreButton = root.findViewById(R.id.exploreToggleBtn2);
        fastestButton = root.findViewById(R.id.fastestToggleBtn2);
        exploreResetButton = root.findViewById(R.id.exploreResetImageBtn2);
        fastestResetButton = root.findViewById(R.id.fastestResetImageBtn2);
        robotStatusTextView = Home.getRobotStatusTextView();
        fastestTimer = 0;
        exploreTimer = 0;
        //startSend = root.findViewById(R.id.startSend); //just added, need to test
/*
        leftleftButton = root.findViewById(R.id.button1);
        leftrightButton = root.findViewById(R.id.button2);
        rightrightButton = root.findViewById(R.id.button3);
        rightleftButton = root.findViewById(R.id.button4);

*/


        gridMap = Home.getGridMap();

        // Button Listener
        moveForwardImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked moveForwardImageBtn");
                if (gridMap.getCanDrawRobot()) {
                    gridMap.moveRobot("forward");
                    Home.refreshLabel();    // update x and y coordinate displayed
                    // display different statuses depending on validity of robot action
                    if (gridMap.getValidPosition()){
                        updateStatus("moving forward");}
                    else {
                        Home.printMessage("message","obstacle");
                        updateStatus("Unable to move forward");
                    }

                    Home.printMessage("message","f");
                }
                else
                    updateStatus("Please press 'SET START POINT'");
                showLog("Exiting moveForwardImageBtn");
            }
        });

        turnRightImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked turnRightImageBtn");
                if (gridMap.getCanDrawRobot()) {
                    gridMap.moveRobot("right");
                    Home.refreshLabel();
                    Home.printMessage("message","fr");
//                    showLog("test");
                    System.out.println(Arrays.toString(gridMap.getCurCoord()));
                }
                else
                    updateStatus("Please press 'SET START POINT'");
                showLog("Exiting turnRightImageBtn");
            }
        });
        turnbrightImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked turnbRightImageBtn");
                if (gridMap.getCanDrawRobot()) {
                    gridMap.moveRobot("backright");
                    Home.refreshLabel();
                    Home.printMessage("message","br");
                    System.out.println(Arrays.toString(gridMap.getCurCoord()));
                }
                else
                    updateStatus("Please press 'SET START POINT'");
                showLog("Exiting turnbRightImageBtn");
            }
        });

        moveBackImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked moveBackwardImageBtn");
                if (gridMap.getCanDrawRobot()) {
                    gridMap.moveRobot("back");
                    Home.refreshLabel();
                    if (gridMap.getValidPosition())
                        updateStatus("moving backward");
                    else
                        updateStatus("Unable to move backward");
                    Home.printMessage("message","b");
                }
                else
                    updateStatus("Please press 'SET START POINT'");
                showLog("Exiting moveBackwardImageBtn");
            }
        });

        turnLeftImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked turnLeftImageBtn");
                if (gridMap.getCanDrawRobot()) {
                    gridMap.moveRobot("left");
                    Home.refreshLabel();
                    updateStatus("turning left");
                    Home.printMessage("message","fl");
                }
                else
                    updateStatus("Please press 'SET START POINT'");
                showLog("Exiting turnLeftImageBtn");
            }
        });
        turnbleftImageBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                showLog("Clicked turnbLeftImageBtn");
                if (gridMap.getCanDrawRobot()) {
                    gridMap.moveRobot("backleft");
                    Home.refreshLabel();
                    updateStatus("turning left");
                    Home.printMessage("message","bl");
                }
                else
                    updateStatus("Please press 'SET START POINT'");
                showLog("Exiting turnbLeftImageBtn");
            }
        });


        // Start Task 1 challenge
        exploreButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showLog("Clicked Task 1 Btn (exploreToggleBtn)");
                ToggleButton exploreToggleBtn = (ToggleButton) v;

                if (exploreToggleBtn.getText().equals("TASK 1 START")) {
                    showToast("Task 1 timer stop!");
                    robotStatusTextView.setText("Task 1 Stopped");
                    timerHandler.removeCallbacks(timerRunnableExplore);
                    TaskManager.getInstance().setTask1Started(false);



                }
                else if (exploreToggleBtn.getText().equals("STOP")) {
                    // Get String value that represents obstacle configuration
                    String msg = gridMap.getObstacles();
                    // Send this String over via BT
                    //Home.printCoords(msg);
                    //Send BEGIN to the robot
                    Home.printMessage("control","start"); //send a string "BEGIN" to the RPI
                    // Start timer
                    Home.stopTimerFlag = false;
                    showToast("Task 1 timer start!");

                    JSONArray robotPositions = DataManager.getInstance().getRobotPositions();

                    if (robotPositions != null) {
                        List<Point> fullPath = null;
                        try {
                            fullPath = generateFullPath(robotPositions);
                        } catch (JSONException e) {
                            throw new RuntimeException(e);
                        }


                        final Handler handler = new Handler();
                        List<Point> finalFullPath = fullPath;
                        for (Point point : finalFullPath) {
                            Log.d(TAG, "Point: (" + point.x + ", " + point.y + ")");
                        }

                        for (int i = 0; i < finalFullPath.size(); i++) {
                            final int index = i;
                            handler.postDelayed(new Runnable() {
                                @Override
                                public void run() {
                                    //JSONObject robotData = robotPositions.getJSONObject(index);
                                    //int xCoord = robotData.getInt("x");
                                    //int yCoord = robotData.getInt("y");
                                    //int directionValue = robotData.getInt("d");
                                    Point point = finalFullPath.get(index); // Get the point from the full path
                                    int xCoord = point.x;
                                    int yCoord = point.y;
                                    int directionValue = calculateDirection(point); // Calculate the direction as needed

                                    updateRobotPosition(xCoord, yCoord, directionValue);
                                    Log.d(TAG, "Updating position");
                                }
                            }, i * 150); // Delay each step by x ms (1000 ms)
                        }
                    } else {
                        Log.d(TAG, "robotPositions is not available.");
                    }

                    robotStatusTextView.setText("Task 1 Started");
                    exploreTimer = System.currentTimeMillis();
                    timerHandler.postDelayed(timerRunnableExplore, 0);
                    TaskManager.getInstance().setTask1Started(true);
                }
                else {
                    showToast("Else statement: " + exploreToggleBtn.getText());
                }
                showLog("Exiting exploreToggleBtn");
            }

            private void updateRobotPosition(int xCoord, int yCoord, int directionValue) {
                String direction = "";
                if (directionValue ==0 ) {    direction = "up"; // NORTH
                } else if (directionValue ==6) {    direction = "left"; // WEST
                } else if (directionValue ==4) {    direction = "down"; // SOUTH
                }else if (directionValue == 2 ) {    direction = "right"; // EAST
                }
                gridMap.setCurCoord(xCoord + 2, 19 - yCoord, direction);

            }
            private List<Point> generateFullPath(JSONArray robotPositions) throws JSONException {
                List<Point> fullPath = new ArrayList<>();

                for (int i = 0; i < robotPositions.length() - 1; i++) {
                    JSONObject currentPoint = robotPositions.getJSONObject(i);
                    JSONObject nextPoint = robotPositions.getJSONObject(i + 1);

                    // Get direction value
                    int directionValue = currentPoint.getInt("d");

                    // Add the current point to the path
                    fullPath.add(new Point(currentPoint.getInt("x"), currentPoint.getInt("y")));

                    // Calculate the difference in x and y coordinates
                    int xDiff = nextPoint.getInt("x") - currentPoint.getInt("x");
                    int yDiff = nextPoint.getInt("y") - currentPoint.getInt("y");

                    // Fill in intermediate points based on direction
                    if (directionValue == 2 || directionValue == 6) {
                        // Append x before y
                        if (xDiff != 0) {
                            int xStep = xDiff > 0 ? 1 : -1; // Step direction for x
                            for (int x = currentPoint.getInt("x") + xStep; x != nextPoint.getInt("x"); x += xStep) {
                                fullPath.add(new Point(x, currentPoint.getInt("y")));
                            }
                        }
                        if (yDiff != 0) {
                            int yStep = yDiff > 0 ? 1 : -1; // Step direction for y
                            for (int y = currentPoint.getInt("y") + yStep; y != nextPoint.getInt("y"); y += yStep) {
                                fullPath.add(new Point(nextPoint.getInt("x"), y));
                            }
                        }
                    } else if (directionValue == 0 || directionValue == 4) {
                        // Append y before x
                        if (yDiff != 0) {
                            int yStep = yDiff > 0 ? 1 : -1; // Step direction for y
                            for (int y = currentPoint.getInt("y") + yStep; y != nextPoint.getInt("y"); y += yStep) {
                                fullPath.add(new Point(currentPoint.getInt("x"), y));
                            }
                        }
                        if (xDiff != 0) {
                            int xStep = xDiff > 0 ? 1 : -1; // Step direction for x
                            for (int x = currentPoint.getInt("x") + xStep; x != nextPoint.getInt("x"); x += xStep) {
                                fullPath.add(new Point(x, nextPoint.getInt("y")));
                            }
                        }
                    }
                }

                // Add the last point
                fullPath.add(new Point(robotPositions.getJSONObject(robotPositions.length() - 1).getInt("x"),
                        robotPositions.getJSONObject(robotPositions.length() - 1).getInt("y")));

                return fullPath;
            }
            private int calculateDirection(Point point) {
                // Implement logic to determine the direction based on your requirements
                return 1; // Placeholder; replace with actual direction logic
            }

        });


        //Start Task 2 Challenge Timer
        fastestButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showLog("Clicked Task 2 Btn (fastestToggleBtn)");
                ToggleButton fastestToggleBtn = (ToggleButton) v;
                if (fastestToggleBtn.getText().equals("TASK 2 START")) {
                    showToast("Task 2 timer stop!");
                    robotStatusTextView.setText("Task 2 Stopped");
                    timerHandler.removeCallbacks(timerRunnableFastest);
                }
                else if (fastestToggleBtn.getText().equals("STOP")) {
                    showToast("Task 2 timer start!");
                    Home.printMessage("control","start"); //send a string "BEGIN" to the RPI
                    Home.stopWk9TimerFlag = false;
                    robotStatusTextView.setText("Task 2 Started");
                    fastestTimer = System.currentTimeMillis();
                    timerHandler.postDelayed(timerRunnableFastest, 0);
                }
                else
                    showToast(fastestToggleBtn.getText().toString());
                showLog("Exiting fastestToggleBtn");
            }
        });
//challenge 1
        exploreResetButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showLog("Clicked exploreResetImageBtn");
                showToast("Resetting exploration time...");
                exploreTimeTextView.setText("00:00");
                robotStatusTextView.setText("Not Available");
                if(exploreButton.isChecked())
                    exploreButton.toggle();
                timerHandler.removeCallbacks(timerRunnableExplore);
                showLog("Exiting exploreResetImageBtn");
            }
        });
// challenge 2
        fastestResetButton.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view) {
                showLog("Clicked fastestResetImgBtn");
                showToast("Resetting Fastest Time...");
                fastestTimeTextView.setText("00:00");
                robotStatusTextView.setText("Fastest Car Finished");
                if(fastestButton.isChecked()){
                    fastestButton.toggle();
                }
                timerHandler.removeCallbacks(timerRunnableFastest);
                showLog("Exiting fastestResetImgBtn");
            }
        });

        /*
        startSend.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view) {
                showLog("Clicked startSendBtn");
                showToast("Sending BEGIN to robot...");
                exploreButton.toggle();
                if (exploreButton.getText().equals("WK8 START")) {
                    showToast("Auto Movement/ImageRecog timer stop!");
                    robotStatusTextView.setText("Auto Movement Stopped");
                    timerHandler.removeCallbacks(timerRunnableExplore);
                }
                else if (exploreButton.getText().equals("STOP")) {
                    // Get String value that represents obstacle configuration
                    String msg = gridMap.getObstacles();
                    // Send this String over via BT
                    //Home.printCoords(msg);
                    // Start timer
                    Home.stopTimerFlag = false;
                    showToast("Auto Movement/ImageRecog timer start!");

                    robotStatusTextView.setText("Auto Movement Started");
                    exploreTimer = System.currentTimeMillis();
                    timerHandler.postDelayed(timerRunnableExplore, 0);
                }
                //ok
                Home.printMessage("BEGIN"); //send a string "BEGIN" to the RPI
                showLog("Exiting startSend");
            }
        });
         */

        return root;
    }



    private static void showLog(String message) {
        Log.d(TAG, message);
    }

    private void showToast(String message) {
        Toast.makeText(getContext(), message, Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onDestroy(){
        super.onDestroy();
    }

    private void updateStatus(String message) {
        Toast toast = Toast.makeText(getContext(), message, Toast.LENGTH_SHORT);
        toast.setGravity(Gravity.TOP,0, 0);
        toast.show();
    }
}
