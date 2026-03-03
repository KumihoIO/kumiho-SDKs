/**
 * @file artifact.hpp
 * @brief Artifact entity representing file references within revisions.
 *
 * Artifacts are the leaf nodes of the Kumiho hierarchy. They point to
 * actual files on local disk, network storage, or cloud URIs. Kumiho
 * tracks the path and metadata but does not upload or modify the files.
 */

#pragma once

#include <string>
#include <memory>
#include <optional>
#include "kumiho/types.hpp"
#include "kumiho/kref.hpp"
#include "kumiho.grpc.pb.h"

namespace kumiho {
namespace api {

// Forward declarations
class Client;
class Revision;
class Item;
class Space;
class Project;

/**
 * @brief A file reference within a revision in the Kumiho system.
 *
 * Artifacts point to actual files on local disk, network storage, or
 * cloud URIs. Kumiho tracks the path and metadata but does not upload
 * or modify the files.
 *
 * The artifact's kref includes both revision and artifact name:
 * `kref://project/space/item.kind?r=1&a=artifact_name`
 *
 * Example:
 * @code
 *   auto mesh = revision->createArtifact("mesh", "/assets/hero.fbx");
 *   auto textures = revision->createArtifact("textures", "smb://server/tex/hero/");
 *   
 *   // Set metadata
 *   mesh->setMetadata({{"triangles", "2.5M"}, {"format", "FBX 2020"}});
 *   
 *   // Set as default artifact
 *   mesh->setDefault();
 * @endcode
 */
class Artifact {
public:
    /**
     * @brief Construct an Artifact from a protobuf response.
     * @param response The protobuf ArtifactResponse message.
     * @param client The client for making API calls.
     */
    Artifact(const ::kumiho::ArtifactResponse& response, Client* client);

    /**
     * @brief Get the artifact's unique Kref.
     * @return The Kref URI for this artifact.
     */
    Kref getKref() const;

    /**
     * @brief Get the artifact name.
     * @return The name of this artifact (e.g., "mesh", "textures").
     */
    std::string getName() const;

    /**
     * @brief Get the file location.
     * @return The file path or URI where the artifact is stored.
     */
    std::string getLocation() const;

    /**
     * @brief Get the parent revision's Kref.
     * @return The Kref of the revision containing this artifact.
     */
    Kref getRevisionKref() const;

    /**
     * @brief Get the parent item's Kref.
     * @return The Kref of the item containing this artifact.
     */
    Kref getItemKref() const;

    /**
     * @brief Get the artifact's metadata.
     * @return A map of metadata key-value pairs.
     */
    Metadata getMetadata() const;

    /**
     * @brief Get the creation timestamp.
     * @return ISO timestamp when the artifact was created, or nullopt.
     */
    std::optional<std::string> getCreatedAt() const;

    /**
     * @brief Get the author's user ID.
     * @return The UUID of the user who created the artifact.
     */
    std::string getAuthor() const;

    /**
     * @brief Get the author's display name.
     * @return The username of the artifact creator.
     */
    std::string getUsername() const;

    /**
     * @brief Check if the artifact is deprecated.
     * @return True if deprecated, false otherwise.
     */
    bool isDeprecated() const;

    /**
     * @brief Set or update metadata for this artifact.
     *
     * Metadata is merged with existing metadata—existing keys are
     * overwritten and new keys are added.
     *
     * @param metadata Dictionary of metadata key-value pairs.
     * @return The updated Artifact.
     */
    std::shared_ptr<Artifact> setMetadata(const Metadata& metadata);

    /**
     * @brief Get a single metadata attribute.
     * @param key The attribute key to retrieve.
     * @return The attribute value, or nullopt if not found.
     */
    std::optional<std::string> getAttribute(const std::string& key);

    /**
     * @brief Set a single metadata attribute.
     * @param key The attribute key to set.
     * @param value The attribute value.
     * @return True if the attribute was set successfully.
     */
    bool setAttribute(const std::string& key, const std::string& value);

    /**
     * @brief Delete a single metadata attribute.
     * @param key The attribute key to delete.
     * @return True if the attribute was deleted successfully.
     */
    bool deleteAttribute(const std::string& key);

    /**
     * @brief Delete this artifact.
     * @param force If true, permanently delete. If false, soft delete (deprecate).
     */
    void deleteArtifact(bool force = false);

    /**
     * @brief Get the parent revision.
     * @return The Revision containing this artifact.
     */
    std::shared_ptr<Revision> getRevision();

    /**
     * @brief Get the parent item.
     * @return The Item containing this artifact.
     */
    std::shared_ptr<Item> getItem();

    /**
     * @brief Get the parent space.
     * @return The Space containing this artifact's item.
     */
    std::shared_ptr<Space> getSpace();

    /**
     * @brief Get the parent project.
     * @return The Project containing this artifact.
     */
    std::shared_ptr<Project> getProject();

    /**
     * @brief Set this artifact as the default for its revision.
     *
     * When resolving a revision without specifying an artifact name,
     * the default artifact's location is returned.
     */
    void setDefault();

    /**
     * @brief Set the deprecated status.
     * @param deprecated True to deprecate, false to restore.
     * @return The updated Artifact.
     */
    std::shared_ptr<Artifact> setDeprecated(bool deprecated);

    // --- Backwards Compatibility Aliases ---

    /** @brief Alias for getRevisionKref(). @deprecated Use getRevisionKref() instead. */
    Kref getVersionKref() const;

    /** @brief Alias for getItemKref(). @deprecated Use getItemKref() instead. */
    Kref getProductKref() const;

    /** @brief Alias for deleteArtifact(). @deprecated Use deleteArtifact() instead. */
    void deleteResource(bool force = false);

    /** @brief Alias for getRevision(). @deprecated Use getRevision() instead. */
    std::shared_ptr<Revision> getVersion();

    /** @brief Alias for getItem(). @deprecated Use getItem() instead. */
    std::shared_ptr<Item> getProduct();

    /** @brief Alias for getSpace(). @deprecated Use getSpace() instead. */
    std::shared_ptr<Space> getGroup();

private:
    ::kumiho::ArtifactResponse response_;
    Client* client_;
};

// Backwards compatibility alias
using Resource = Artifact;

} // namespace api
} // namespace kumiho
