#include "kumiho.h"
#include <iostream>
#include <memory>
#include <string>
#include <csignal>
#include <cstdlib> // For system()

// Global flag to handle graceful shutdown
volatile sig_atomic_t g_keep_running = 1;

void sigint_handler(int) {
    g_keep_running = 0;
}

void PrintUsage() {
    std::cout << "Kumiho Event Listener v1.0" << std::endl;
    std::cout << "==========================" << std::endl;
    std::cout << std::endl;
    std::cout << "DESCRIPTION:" << std::endl;
    std::cout << "  Listens to real-time events from a Kumiho server and optionally executes" << std::endl;
    std::cout << "  commands when events are received. This enables automation workflows" << std::endl;
    std::cout << "  triggered by asset changes in the Kumiho media asset management system." << std::endl;
    std::cout << std::endl;
    std::cout << "USAGE:" << std::endl;
    std::cout << "  kumiho_listener [options] [command]" << std::endl;
    std::cout << std::endl;
    std::cout << "OPTIONS:" << std::endl;
    std::cout << "  -h, --help              Show this help message and exit" << std::endl;
    std::cout << "  -s, --server SERVER     Server endpoint (default: localhost:8080)" << std::endl;
    std::cout << "  -r, --routing-key KEY   Filter events by routing key pattern (optional)" << std::endl;
    std::cout << "                          Supports wildcards. Examples:" << std::endl;
    std::cout << "                            'version.created' - Only version creation events" << std::endl;
    std::cout << "                            'product.*' - All product-related events" << std::endl;
    std::cout << "                            '*' - All events (default)" << std::endl;
    std::cout << "  -k, --kref-filter KEY   Filter events by kref URI pattern (optional)" << std::endl;
    std::cout << "                          Supports wildcards. Examples:" << std::endl;
    std::cout << "                            'kref://projectA/**' - All events in projectA" << std::endl;
    std::cout << "                            'kref://projectA/**/*.model' - Model events in projectA" << std::endl;
    std::cout << std::endl;
    std::cout << "ARGUMENTS:" << std::endl;
    std::cout << "  command                 Command to execute when events are received." << std::endl;
    std::cout << "                          Use quotes for commands with spaces." << std::endl;
    std::cout << "                          Available variables in commands:" << std::endl;
    std::cout << "                            {type} - Event type (e.g., 'version.created')" << std::endl;
    std::cout << "                            {kref} - Kumiho reference URI" << std::endl;
    std::cout << "                            {routing_key} - Full routing key" << std::endl;
    std::cout << "                            {timestamp} - Event timestamp" << std::endl;
    std::cout << std::endl;
    std::cout << "EXAMPLES:" << std::endl;
    std::cout << "  # Listen for all events and log them" << std::endl;
    std::cout << "  kumiho_listener" << std::endl;
    std::cout << std::endl;
    std::cout << "  # Listen for version creation events only" << std::endl;
    std::cout << "  kumiho_listener -r 'version.created'" << std::endl;
    std::cout << std::endl;
    std::cout << "  # Listen for all product-related events" << std::endl;
    std::cout << "  kumiho_listener -r 'product.*'" << std::endl;
    std::cout << std::endl;
    std::cout << "  # Listen for events in a specific project" << std::endl;
    std::cout << "  kumiho_listener -k 'kref://projectA/**'" << std::endl;
    std::cout << std::endl;
    std::cout << "  # Combine routing key and kref filters" << std::endl;
    std::cout << "  kumiho_listener -k 'kref://projectA/**' -r 'product.model.created'" << std::endl;
    std::cout << std::endl;
    std::cout << "  # Combined syntax: model events in projectA with specific actions" << std::endl;
    std::cout << "  kumiho_listener 'kref://projectA/**/*.model%actions=product.model.created,version.tagged'" << std::endl;
    std::cout << std::endl;
    std::cout << "  # Execute command on events" << std::endl;
    std::cout << "  kumiho_listener 'echo \"Event: {type} - {kref}\"' " << std::endl;
    std::cout << std::endl;
    std::cout << "  # Trigger build script for a specific project" << std::endl;
    std::cout << "  kumiho_listener -s 'prod-server:8080' '/scripts/trigger_build.sh'" << std::endl;
    std::cout << std::endl;
    std::cout << "  # Send webhook notifications for new versions" << std::endl;
    std::cout << "  kumiho_listener -r 'version.created' 'curl -X POST -H \"Content-Type: application/json\" -d \"{\\\"event\\\":\\\"version_created\\\",\\\"kref\\\":\\\"{kref}\\\"}\" https://webhook.example.com/notify'" << std::endl;
    std::cout << std::endl;
    std::cout << "  # Monitor specific asset types for quality control" << std::endl;
    std::cout << "  kumiho_listener -r 'product.model.created' '/scripts/validate_model.sh {kref}'" << std::endl;
    std::cout << std::endl;
    std::cout << "  # Track changes in a specific shot" << std::endl;
    std::cout << "  kumiho_listener -k 'kref://projectA/shot_001/**' 'notify-send \"Shot changed\" \"{kref}\"' " << std::endl;
    std::cout << std::endl;
    std::cout << "  # CI/CD integration - trigger builds on version tagging" << std::endl;
    std::cout << "  kumiho_listener -r 'version.tagged' '/scripts/ci_trigger.sh {kref}'" << std::endl;
    std::cout << std::endl;
    std::cout << "EVENT TYPES:" << std::endl;
    std::cout << "  group.created, group.updated, group.deleted" << std::endl;
    std::cout << "  product.created, product.updated, product.deleted" << std::endl;
    std::cout << "  version.created, version.updated, version.deleted, version.tagged, version.untagged" << std::endl;
    std::cout << "  resource.created, resource.updated, resource.deleted" << std::endl;
    std::cout << "  link.created, link.updated, link.deleted" << std::endl;
    std::cout << std::endl;
    std::cout << "NOTES:" << std::endl;
    std::cout << "  - Press Ctrl+C to exit gracefully" << std::endl;
    std::cout << "  - Commands are executed synchronously and may block event processing" << std::endl;
    std::cout << "  - Use environment variables or wrapper scripts for complex automation" << std::endl;
}

int main(int argc, char** argv) {
    std::string server_endpoint = "localhost:8080";
    std::string routing_key_filter = "";
    std::string kref_filter = "";
    std::string command = "";

    // Parse command line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "-h" || arg == "--help") {
            PrintUsage();
            return 0;
        } else if (arg == "-s" || arg == "--server") {
            if (i + 1 < argc) {
                server_endpoint = argv[++i];
            } else {
                std::cerr << "Error: --server option requires a value" << std::endl;
                PrintUsage();
                return 1;
            }
        } else if (arg == "-r" || arg == "--routing-key") {
            if (i + 1 < argc) {
                routing_key_filter = argv[++i];
            } else {
                std::cerr << "Error: --routing-key option requires a value" << std::endl;
                PrintUsage();
                return 1;
            }
        } else if (arg == "-k" || arg == "--kref-filter") {
            if (i + 1 < argc) {
                kref_filter = argv[++i];
            } else {
                std::cerr << "Error: --kref-filter option requires a value" << std::endl;
                PrintUsage();
                return 1;
            }
        } else if (arg[0] == '-') {
            std::cerr << "Error: Unknown option '" << arg << "'" << std::endl;
            PrintUsage();
            return 1;
        } else {
            // Positional argument - should be the command
            if (command.empty()) {
                command = arg;
            } else {
                std::cerr << "Error: Unexpected positional argument '" << arg << "'" << std::endl;
                PrintUsage();
                return 1;
            }
        }
    }

    // Parse combined filter syntax: kref://pattern%actions=routing_keys
    if (!routing_key_filter.empty() && routing_key_filter.find("kref://") == 0) {
        size_t actions_pos = routing_key_filter.find("%actions=");
        if (actions_pos != std::string::npos) {
            kref_filter = routing_key_filter.substr(0, actions_pos);
            routing_key_filter = routing_key_filter.substr(actions_pos + 9); // Skip "%actions="
        } else {
            // Just a kref filter without actions
            kref_filter = routing_key_filter;
            routing_key_filter = "";
        }
    }

    // Register signal handler for Ctrl+C
    signal(SIGINT, sigint_handler);

    try {
        // Create a client connected to the specified server
        auto channel = grpc::CreateChannel(server_endpoint, grpc::InsecureChannelCredentials());
        kumiho::api::Client client(channel);

        // Test server connectivity with a simple RPC call
        std::cout << "Testing server connectivity..." << std::endl;
        try {
            // Try to get root groups as a connectivity test
            auto test_groups = client.getChildGroups("/");
            std::cout << "Server connection successful." << std::endl;
        } catch (const std::exception& e) {
            std::cerr << "Error: Failed to connect to server at " << server_endpoint << std::endl;
            std::cerr << "Details: " << e.what() << std::endl;
            std::cerr << "Make sure the Kumiho server is running and accessible." << std::endl;
            return 1;
        }

        // Build connection message
        std::cout << "Connecting to Kumiho server at " << server_endpoint;
        if (!routing_key_filter.empty() || !kref_filter.empty()) {
            std::cout << " (filters: ";
            if (!routing_key_filter.empty()) {
                std::cout << "routing_key='" << routing_key_filter << "'";
            }
            if (!routing_key_filter.empty() && !kref_filter.empty()) {
                std::cout << ", ";
            }
            if (!kref_filter.empty()) {
                std::cout << "kref='" << kref_filter << "'";
            }
            std::cout << ")";
        } else {
            std::cout << " (listening for all events)";
        }
        if (!command.empty()) {
            std::cout << " - will execute command on events";
        }
        std::cout << "..." << std::endl;
        std::cout << "Press Ctrl+C to exit." << std::endl;
        std::cout << "--------------------------------------------------------" << std::endl;

        // Start listening to the event stream
        auto stream = client.eventStream(routing_key_filter, kref_filter);
        kumiho::api::Event event;

        int event_count = 0;
        while (g_keep_running && stream->readNext(event)) {
            event_count++;
            std::cout << "Event #" << event_count << " Received:" << std::endl;
            std::cout << "  Routing Key: " << event.getRoutingKey() << std::endl;
            std::cout << "  Kref:        " << event.getKref().uri() << std::endl;
            
            auto details = event.getDetails();
            if (!details.empty()) {
                std::cout << "  Details:" << std::endl;
                for (const auto& pair : details) {
                    std::cout << "    - " << pair.first << ": " << pair.second << std::endl;
                }
            }
            std::cout << "--------------------------------------------------------" << std::endl;

            // Execute command if provided
            if (!command.empty()) {
                std::cout << "Executing command: " << command << std::endl;
                int result = system(command.c_str());
                if (result != 0) {
                    std::cerr << "Command execution failed with exit code: " << result << std::endl;
                }
                std::cout << "--------------------------------------------------------" << std::endl;
            }
        }

        if (!g_keep_running) {
            std::cout << "\nCaught interrupt signal. Shutting down gracefully." << std::endl;
        } else {
            std::cout << "\nEvent stream ended." << std::endl;
            std::cout << "This usually means:" << std::endl;
            std::cout << "  - The server closed the connection" << std::endl;
            std::cout << "  - Network connectivity was lost" << std::endl;
            std::cout << "  - The server encountered an error" << std::endl;
            std::cout << "  - Invalid filter patterns were specified" << std::endl;
            if (event_count == 0) {
                std::cout << "\nNo events were received. Possible causes:" << std::endl;
                std::cout << "  - No events match your filter criteria" << std::endl;
                std::cout << "  - The server has no recent activity" << std::endl;
                std::cout << "  - Check your filter patterns: routing_key='" << routing_key_filter << "', kref='" << kref_filter << "'" << std::endl;
            } else {
                std::cout << "Total events received: " << event_count << std::endl;
            }
        }

    } catch (const std::runtime_error& e) {
        std::cerr << "An error occurred: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
