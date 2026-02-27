import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;

public class SimpleHttpServer {

    public static void main(String[] args) throws IOException {
        // Create server on localhost, port 9080
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 9080), 0);

        // Define the handler
        server.createContext("/", new HttpHandler() {
            @Override
            public void handle(HttpExchange exchange) throws IOException {
                String path = exchange.getRequestURI().getPath();

                if ("/api/ucore/manifest".equals(path) && "GET".equalsIgnoreCase(exchange.getRequestMethod())) {
                    byte[] response = "{}".getBytes();
                    exchange.getResponseHeaders().set("Content-Type", "application/json");
                    exchange.sendResponseHeaders(200, response.length);
                    try (OutputStream os = exchange.getResponseBody()) {
                        os.write(response);
                    }
                } else {
                    // Send 401 Unauthorized for everything else
                    exchange.sendResponseHeaders(401, -1); // -1 indicates no body
                }
                exchange.close();
            }
        });

        System.out.println("Server started at http://127.0.0.1:9080");
        server.setExecutor(null); // creates a default executor
        server.start();
    }
}
