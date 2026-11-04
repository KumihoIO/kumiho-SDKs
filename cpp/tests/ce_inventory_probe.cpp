#include <kumiho/kumiho.hpp>
#include <grpcpp/grpcpp.h>
#include <cassert>
#include <iostream>
#include <set>

int main(int argc, char** argv) {
    assert(argc == 3);
    kumiho::api::Client client(grpc::CreateChannel(argv[1], grpc::InsecureChannelCredentials()));
    const std::string root = argv[2];
    const auto legacy = client.getChildSpaces(root, true);
    assert(legacy.size() == 1004);
    const auto all = client.getItemsPaged(root, "", "", true);
    assert(all.items.size() == 1004 && all.pagination_present && all.total_count == 1004 && all.has_more == false);
    std::set<std::string> spaces, items;
    std::string cursor;
    size_t count = 0;
    do {
        const auto page = client.getChildSpacesPaged(root, true, 251, cursor);
        assert(page.pagination_present && page.total_count == 1004 && page.items.size() == 251);
        for (const auto& space : page.items) spaces.insert(space->getPath());
        count += page.items.size(); cursor = page.next_cursor.value_or("");
        assert(page.has_more == !cursor.empty());
    } while (!cursor.empty());
    assert(count == 1004 && spaces.size() == 1004);
    count = 0;
    do {
        const auto page = client.getItemsPaged(root, "", "", true, 251, cursor);
        assert(page.pagination_present && page.total_count == 1004 && page.items.size() == 251);
        for (const auto& item : page.items) items.insert(item->getKref());
        count += page.items.size(); cursor = page.next_cursor.value_or("");
        assert(page.has_more == !cursor.empty());
    } while (!cursor.empty());
    assert(count == 1004 && items.size() == 1004);
    kumiho::SpaceResponse response; response.set_path(root);
    kumiho::api::Space space(response, &client);
    assert(space.getItemsPaged("", "", 0, "", true).items.size() == 1004);
    assert(space.getChildSpacesPaged(true, 251).total_count == 1004);
    std::cout << "C++ CE1.11.0 inventory: PASS (unpaged,4x251 pages,metadata,deprecated,legacy vector)\n";
}
