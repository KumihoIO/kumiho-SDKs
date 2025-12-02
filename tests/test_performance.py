import kumiho
import time
import uuid
import random
import logging

# Configure logging for the test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def unique_name(prefix: str) -> str:
    """Generates a unique name with a prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def test_item_search_performance():
    """
    Generates a large number of items and measures creation and search time.
    """
    root_space_name = unique_name('perf_test')
    num_projects = 5
    num_sequences_per_project = 10
    num_shots_per_sequence = 20
    num_items_per_shot = 5
    total_items = num_projects * num_sequences_per_project * num_shots_per_sequence * num_items_per_shot
    
    kinds = ["model", "dataset", "rig", "texture", "animation"]
    created_item_names = []

    logging.info(f"--- Performance Test Started ---")
    logging.info(f"Root space for this run: {root_space_name}")
    logging.info(f"Will create {total_items} items across a nested hierarchy.")

    # --- 1. Data Creation ---
    start_creation = time.perf_counter()
    
    # Create root space (top-level)
    root_project = kumiho.create_project(root_space_name)
    root_space = root_project.create_space(name=root_space_name, parent_path="/")
    for i in range(num_projects):
        # Create project space under root
        proj_space = root_space.create_space(f"proj_{i:02d}")
        for j in range(num_sequences_per_project):
            # Create sequence space under project
            seq_space = proj_space.create_space(f"seq_{j:03d}")
            for k in range(num_shots_per_sequence):
                # Create shot space under sequence
                shot_space = seq_space.create_space(f"shot_{k:04d}")
                for l in range(num_items_per_shot):
                    kind = random.choice(kinds)
                    iname = unique_name(f"asset_{l}")
                    item = shot_space.create_item(item_name=iname, kind=kind)
                    logging.info(f"Created item: {item.kref.uri}")
                    if l == 0:  # Store one name per shot for later search test
                        created_item_names.append(iname)

    end_creation = time.perf_counter()
    creation_time = end_creation - start_creation
    logging.info(f"[REPORT] Data Creation Time: {creation_time:.4f} seconds.")
    logging.info(f"[REPORT] Avg time per item: {(creation_time / total_items) * 1000:.4f} ms.")

    # --- 2. Search Performance ---
    logging.info("--- Starting Search Benchmarks ---")

    # A) Search by kind (broad)
    start_search_kind = time.perf_counter()
    results_kind = kumiho.item_search(kind_filter="model")
    end_search_kind = time.perf_counter()
    logging.info(f"[REPORT] Search by Kind ('model'): Found {len(results_kind)} results in {end_search_kind - start_search_kind:.4f} seconds.")

    # B) Search by context (medium)
    search_context = f"{root_space_name}/proj_01/seq_001"
    start_search_context = time.perf_counter()
    results_context = kumiho.item_search(context_filter=search_context)
    end_search_context = time.perf_counter()
    logging.info(f"[REPORT] Search by Context ('{search_context}'): Found {len(results_context)} results in {end_search_context - start_search_context:.4f} seconds.")

    # C) Search by name (specific)
    search_name = random.choice(created_item_names)
    start_search_name = time.perf_counter()
    results_name = kumiho.item_search(name_filter=search_name)
    end_search_name = time.perf_counter()
    logging.info(f"[REPORT] Search by Name ('{search_name}'): Found {len(results_name)} results in {end_search_name - start_search_name:.4f} seconds.")

    # --- 3. Teardown ---
    logging.info(f"--- Tearing down test data ---")
    start_delete = time.perf_counter()
    root_project.delete(force=True)
    end_delete = time.perf_counter()
    logging.info(f"[REPORT] Teardown Time: {end_delete - start_delete:.4f} seconds.")
    
    logging.info(f"--- Performance Test Finished ---")
