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
        var all = new Action[] { Action.Down, Action.Left, Action.Up, Action.Right, Action.NoOp, Action.Teleport, Action.Trap };
        var random = new Random();
        return all[random.nextInt(7)];
    }

    public static void main(String[] args) throws IOException {
        var client = new Main("192.168.43.123", 9921);
        client.play();
    }
}
