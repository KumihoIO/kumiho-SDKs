#include "kumiho.h"
#include <iostream>
#include <memory>
#include <string>
#include <map>

int main() {
    try {
        // Create a client using environment variable or default to localhost:50051
        auto client = kumiho::api::Client::createFromEnv();

        std::cout << "Kumiho C++ Client Example" << std::endl;
        std::cout << "==========================" << std::endl;

        // 1. Create a top-level group.
        std::cout << "1. Creating a top-level group 'animals'..." << std::endl;
        auto group = client->createGroup("/", "animals");
        std::cout << "   - Success. Path: " << group->getPath() << std::endl;

        // 2. Create a subgroup.
        std::cout << "2. Creating a subgroup 'mammals' under 'animals'..." << std::endl;
        auto subgroup = group->createGroup("mammals");
        std::cout << "   - Success. Path: " << subgroup->getPath() << std::endl;

        // 3. Create a product in the subgroup.
        std::cout << "3. Creating a product 'fox' in 'animals/mammals'..." << std::endl;
        auto product = subgroup->createProduct("fox", "character");
        std::cout << "   - Success. Kref: " << product->getKref().uri() << std::endl;

        // 4. Create a version for the product.
        std::cout << "4. Creating a version for the 'fox' product..." << std::endl;
        std::map<std::string, std::string> metadata = {
            {"description", "Initial model check-in"}
        };
        auto version = product->createVersion(metadata);
        std::cout << "   - Success. Kref: " << version->getKref().uri() << std::endl;

        // 5. Create a resource for the version.
        std::cout << "5. Creating a resource for the new version..." << std::endl;
        auto resource = version->createResource("main_geo", "/server/assets/fox/v001/fox.obj");
        std::cout << "   - Success. Kref: " << resource->getKref().uri() << std::endl;

    } catch (const std::runtime_error& e) {
        std::cerr << "An error occurred: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
