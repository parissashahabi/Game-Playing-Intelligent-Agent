package com.example;

import java.io.IOException;
import java.util.Random;


public class Main extends Base {
    public Main() {
        super();
    }

    public Main(String serverIp, int serverPort) {
        super(serverIp, serverPort);
    }

    public Main(String serverIp) {
        super(serverIp);
    }

    public Main(int serverPort) {
        super(serverPort);
    }

    @Override
    public Action doTurn() {
        // Do your logic here
        Action[] all = new Action[] { Action.Down, Action.Left, Action.Up, Action.Right, Action.NoOp };
        Random random = new Random();
        return all[random.nextInt(5)];
    }

    public static void main(String[] args) throws IOException {
        Main client = new Main("127.0.0.1", 9921);
        client.play();
    }
}
